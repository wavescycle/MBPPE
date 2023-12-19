<template>
  <div class="make-center">
    <el-form ref="formRef" :rules="rules" :model="form" label-width="150px" label-position="top">
      <el-form-item label="Filename" prop="name">
        <el-select
            v-model="form.name"
            :placeholder="placeholder"
            ref="fileName"
        >
          <el-option
              v-for="(file, i) of form.fileList"
              :key="i"
              :label="file"
              :value="file"
          >
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="Method" prop="process">
        <el-radio-group v-model="form.process">
          <el-radio-button label="Filter"/>
          <el-radio-button label="ICA"/>
          <el-radio-button label="Reference"/>
          <el-radio-button label="Resample"/>
          <el-radio-button label="Plugin"/>
        </el-radio-group>
      </el-form-item>
      <el-form-item
          label="Filter"
          prop="methods"
          v-if="form.process === 'Filter'"
      >
        <el-select v-model="form.methods" placeholder="Select">
          <el-option key="lowpass" label="Low-pass filter" value="lowpass"></el-option>
          <el-option key="highpass" label="High-pass filter" value="highpass"></el-option>
          <el-option key="bandpass" label="Bandpass filter" value="bandpass"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item
          :label="label.low"
          prop="low"
          v-if="
          form.process === 'Filter' &&
          (form.methods === 'lowpass' || form.methods === 'bandpass')
        "
      >
        <el-col :span="4">
          <el-input
              v-model="form.low"
              placeholder="input"
              type="number"
              min="0"
          />
        </el-col>
      </el-form-item>
      <el-form-item
          :label="label.high"
          prop="high"
          v-if="
          form.process === 'Filter' &&
          (form.methods === 'highpass' || form.methods === 'bandpass')
        "
      >
        <el-col :span="4">
          <el-input
              v-model="form.high"
              placeholder="input"
              type="number"
              min="0"
          />
        </el-col>
      </el-form-item>
      <el-form-item label="Plugin" v-if="form.process==='Plugin'" prop="plugin" required>
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
      <el-form-item
          label="Channels"
          prop="channels"
          v-if="form.process !== 'ICA'&&form.process !== 'Resample'"
      >
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
      <el-form-item label="Mode" v-if="form.process === 'Reference'" prop="mode">
        <el-select
            v-model="form.refMode"
            collapse-tags
            placeholder="Reference Mode"
            :span="8"
        >
          <el-option
              v-for="(mode, i) of refMode"
              :key="i"
              :label="mode"
              :value="mode"
          ></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="Ref Channels" v-if="form.refMode !== 'average'" prop="refChannels" required>
        <el-select
            v-model="form.refChannels"
            multiple
            :span="8"
            :multiple-limit="form.refMode==='ear'?2:1"
        >
          <el-option
              v-for="(file, i) of CH_NAMES"
              :key="i"
              :label="file"
              :value="i"
          ></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="Sampling Rate" v-if="form.process==='Resample'" prop="fs" required>
        <el-input-number
            v-model="form.fs"
            :min="0"
            style="width: 220px"
        />
      </el-form-item>
      <el-form-item label="Params" v-if="form.process==='Plugin'" prop="pluginParams">
        <el-input
            style="width: 300px"
            v-model="form.pluginParams"
            :rows="2"
            type="textarea"
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
import {reactive, ref, computed, onMounted, watch} from "vue";
import {ElMessage, ElLoading} from "element-plus";
import {
  getFileList,
  postFilter,
  postICA,
  getPreData,
  postReference,
  postResample,
  getPlugin,
  postPluginHandler
} from "../utils/api";
import {CH_NAMES} from "../config/config.json";

export default {
  setup() {
    const rules = {
      name: [{required: true, message: "Select a file", trigger: "blur"}],
      methods: [{required: true, message: "Select the processing method", trigger: "blur"}],
      preData: [{required: true, message: "Select the pre data", trigger: "blur"}],
      low: [{required: true, message: "Enter the frequency", trigger: "blur"}],
      high: [{required: true, message: "Enter the frequency", trigger: "blur"}],
    };
    const refMode = ["average", "channel", "ear"]
    const formRef = ref(null);
    const loading = ref(null);
    const getPreDataLoading = ref(null)
    const form = reactive({
      name: "",
      process: "Filter",
      methods: "",
      channels: [],
      low: "",
      high: "",
      filter: false,
      fileList: [],
      preData: "",
      preDataList: [],
      refMode: "average",
      refChannels: [],
      fs: null,
      plugin: "",
      pluginParams: ""
    });
    const pluginList = ref([])


    const label = computed(() => {
      let labels = {
        low: "Cutoff Frequency",
        high: "Cutoff Frequency",
      };
      if (form.methods === "bandpass") {
        labels.low = "Lowest Frequency";
        labels.high = "Highest Frequency";
      }
      return labels;
    });

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
      // Form validation
      formRef.value.validate(async (valid) => {
        if (valid) {
          const loading = ElLoading.service({
            lock: true,
            text: "Loading",
          });
          const name = form.name;
          const methods = form.methods;
          const process = form.process;
          let channels = form.channels;
          if (channels.length === 0) channels = CH_NAMES.map((e, i) => i);
          let res;
          if (process === "Filter") {
            const low = form.low;
            const high = form.high;
            res = await postFilter(name, channels, methods, low, high, form.preData);
          } else if (process === "ICA") {
            res = await postICA(name, form.preData);
          } else if (process === "Reference") {
            const refCh = Array.isArray(form.refChannels) ? form.refChannels : [form.refChannels]
            res = await postReference(name, channels, form.preData, {mode: form.refMode, ref_ch: refCh})
          } else if (process === "Resample") {
            res = await postResample(name, form.preData, {new_fs: form.fs})
          } else if (process === "Plugin") {
            res = await postPluginHandler(name, channels, form.preData, {
              plugin: form.plugin,
              plugin_type: "Pre_Process",
              plugin_params: form.pluginParams
            })
          }
          loading.close();
          if (res.status === 200) ElMessage.success("success");
          else ElMessage.error(res.data);
        } else {
          return false;
        }
      });
    };
    // Reset
    const onReset = () => {
      formRef.value.resetFields();
    };

    onMounted(() => {
      getFileList().then((res) => {
        form.fileList = res.data;
      });
      getPlugin().then(res => {
        pluginList.value = res.data
      })
    })
    return {
      rules,
      CH_NAMES,
      label,
      loading,
      getPreDataLoading,
      formRef,
      form,
      placeholder,
      onSubmit,
      onReset,
      getPreDataList,
      refMode,
      pluginList
    };
  },
};
</script>
<style scoped></style>
