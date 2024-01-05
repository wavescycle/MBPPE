<template>
  <div class="make-center">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
      <el-form-item label="Filename" prop="name">
        <el-select v-model="form.name" :placeholder="placeholder">
          <el-option
              v-for="(file, i) of form.fileList"
              :key="i"
              :label="file"
              :value="file"
          >
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="Method" prop="method">
        <el-radio-group v-model="form.method">
          <el-radio-button label="PSD"/>
          <el-radio-button label="DE"/>
          <el-radio-button label="Frequency"/>
          <el-radio-button label="TimeFrequency"/>
          <el-radio-button label="Plugin"/>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="Channels" prop="channels" v-if="form.method.includes('Frequency') ||form.method==='Plugin' ">
        <el-select
            v-model="form.channels"
            multiple
            collapse-tags
            placeholder="Default full selection"
            :span="8"
        >
          <el-option
              v-for="(file, i) of CH_NAMES"
              :key="i"
              :label="file"
              :value="i"
          ></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="BandList" prop="BandList" v-if="form.method==='Frequency'">
        <el-input
            style="width: 300px"
            v-model="form.bandList"
            :rows="2"
            type="textarea"
            placeholder='[{"name":"Delta","fmin":1,"fmax":4},{"name":"Theta","fmin":4,"fmax":8},{"name":"Alpha","fmin":8,"fmax":13},{"name":"Beta","fmin":13,"fmax":31},{"name":"Gamma","fmin":31,"fmax":50}]'
        />
      </el-form-item>
      <el-form-item label="PreData" prop="preData">
        <el-select
            v-model="form.preData"
            @visible-change="getPreDataList"
            :loading="getPreDataLoading"
        >
          <el-option
              v-for="(preData, i) of form.preDataList"
              :key="i"
              :label="preData"
              :value="preData"
          >
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="Plugin" v-if="form.method==='Plugin'" prop="plugin" required>
        <el-select v-model="form.plugin">
          <el-option
              v-for="(item, i) of pluginList"
              :key="i"
              :label="item"
              :value="item"
          >
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="Params" v-if="form.method==='Plugin'" prop="pluginParams">
        <el-input
            style="width: 300px"
            v-model="form.pluginParams"
            :rows="2"
            type="textarea"
        />
      </el-form-item>
      <el-form-item label="Advance Params" v-if="form.method!=='Plugin'&&form.method!=='DE'"
                    prop="advanceParams">
        <el-input
            style="width: 300px"
            v-model="form.advanceParams"
            :rows="2"
            type="textarea"
            placeholder="Need JSON format"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="onSubmit">Submit</el-button>
        <el-button @click="onReset">Reset</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
import {reactive, ref, computed, onMounted} from "vue";
import {
  getFileList,
  postPSD,
  postDE,
  getPreData,
  postFrequency,
  postTimeFrequency,
  getPlugin,
  postPluginHandler
} from "../utils/api";
import {ElMessage, ElLoading} from "element-plus";
import {CH_NAMES} from "../config/config.json"

export default {
  setup() {
    const loading = ref(null);
    const formRef = ref(null);
    const getPreDataLoading = ref(null)
    const form = reactive({
      name: "",
      filter: false,
      method: "PSD",
      fileList: [],
      preData: "",
      channels: [],
      bandList: "",
      preDataList: [],
      plugin: "",
      pluginParams: "",
      advanceParams: ""
    });
    const pluginList = ref([])

    const rules = {
      name: {required: true, message: "Select a file", trigger: "blur"},
      preData: {required: true, message: "Select the pre data", trigger: "blur"},
    }

    let placeholder = computed(() =>
        form.fileList?.length ? "Select" : "Upload data first"
    );
    const getPreDataList = async (visible) => {
      getPreDataLoading.value = true
      if (visible) {
        let res = await getPreData(form.name)
        if (res.status === 200) {
          form.preDataList = res.data
          getPreDataLoading.value = false
        }
      }
    }
    // Processing of requests for feature extract methods
    const onSubmit = () => {
      formRef.value.validate(async (valid) => {
        if (valid) {
          const loading = ElLoading.service({
            lock: true,
            text: "Loading",
          });
          let res = null;
          if (form.channels.length === 0) {
            form.channels = CH_NAMES.map((e, i) => i)
          }
          const advanceParams = form.advanceParams && JSON.parse(form.advanceParams);
          switch (form.method) {
            case "PSD":
              res = await postPSD(form.name, form.preData, {advance_params: advanceParams});
              break;
            case "DE":
              res = await postDE(form.name, form.preData);
              break;
            case "Frequency":
              res = await postFrequency(form.name, form.channels, form.preData, {
                band_list: form.bandList,
                advance_params: advanceParams
              })
              break;
            case "TimeFrequency":
              res = await postTimeFrequency(form.name, form.channels, form.preData, {advance_params: advanceParams})
              break
            case "Plugin":
              res = await postPluginHandler(form.name, form.channels, form.preData, {
                plugin: form.plugin,
                plugin_type: "Feature_Ext",
                plugin_params: form.pluginParams
              })
          }

          loading.close();
          if (res?.status === 200) ElMessage.success("success");
          else ElMessage.error(res?.data);
        } else {
          return false;
        }
      });
    };
    const onReset = () => {
      formRef.value.resetFields();
    };
    // Get the list of files and plugins
    onMounted(() => {
      getFileList().then((res) => {
        form.fileList = res.data;
      });
      getPlugin().then(res => {
        pluginList.value = res.data
      })
    })
    return {
      formRef,
      form,
      onSubmit,
      getPreDataLoading,
      placeholder,
      rules,
      onReset,
      loading,
      CH_NAMES,
      getPreDataList,
      pluginList
    };
  },
};
</script>

<style scoped></style>
