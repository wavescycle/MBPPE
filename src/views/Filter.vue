<template>
  <div class="make-center">
    <el-form ref="formRef" :rules="rules" :model="form" label-width="80px">
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
          <el-radio-button label="Filter" />
          <el-radio-button label="ICA" />
        </el-radio-group>
      </el-form-item>
      <el-form-item
        label="Filter"
        prop="methods"
        v-if="form.process == 'Filter'"
      >
        <el-select v-model="form.methods" placeholder="Select">
          <el-option key="low" label="Low-pass filter" value="low"></el-option>
          <el-option key="high" label="High-pass filter" value="high"></el-option>
          <el-option key="band" label="Bandpass filter" value="band"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item
        :label="label.low"
        prop="low"
        v-if="
          form.process == 'Filter' &&
          (form.methods === 'low' || form.methods === 'band')
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
          form.process == 'Filter' &&
          (form.methods === 'high' || form.methods === 'band')
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
      <el-form-item label="Filtered" prop="filter" v-if="form.process == 'ICA'">
        <el-switch
          v-model="form.filter"
          :loading="loading"
          :before-change="checkFilter"
        />
      </el-form-item>
      <el-form-item
        label="channels"
        prop="channels"
        v-if="form.process == 'Filter'"
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
      <el-form-item>
        <el-button type="primary" @click="onSubmit">Submit</el-button>
        <el-button @click="onReset">Reset</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
import { reactive, ref, computed } from "vue";
import { ElMessage, ElLoading } from "element-plus";
import { getFileList, postFilter, postICA } from "../utils/api";
import { CH_NAMES } from "../config/config.json";
export default {
  setup() {
    const rules = {
      name: [{ required: true, message: "Select a file", trigger: "blur" }],
      methods: [
        { required: true, message: "Select the processing method", trigger: "blur" },
      ],
      low: [{ required: true, message: "Enter the frequency", trigger: "blur" }],
      high: [{ required: true, message: "Enter the frequency", trigger: "blur" }],
    };
    const formRef = ref(null);
    const loading = ref(null);
    const form = reactive({
      name: "",
      process: "Filter",
      methods: "",
      channels: [],
      low: "",
      high: "",
      filter: false,
      fileList: [],
    });
    getFileList().then((res) => {
      form.fileList = res.data;
    });
    const label = computed(() => {
      let label = {
        low: "Cutoff frequency",
        high: "Cutoff frequency",
      };
      if (form.methods === "band") {
        label.low = "Lowest frequency";
        label.high = "Highest frequency";
      }
      return label;
    });
    let placeholder = computed(() =>
      form.fileList?.length ? "Select" : "Upload data first"
    );
    const checkFilter = async () => {
      loading.value = true;
      if (form.filter) {
        form.filter = false;
      } else {
        const res = await getFileList(true);
        if (res.data.indexOf(form.name) !== -1) {
          form.filter = true;
        } else {
          ElMessage.error(`Filter the ${form.name} first`);
        }
      }
      loading.value = false;
    };
    // Submit
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
          if (process == "Filter") {
            const low = form.low;
            const high = form.high;
            res = await postFilter(name, channels, methods, low, high);
          } else if (process == "ICA") {
            console.log("ICA");
            res = await postICA(name, form.filter);
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

    return {
      rules,
      CH_NAMES,
      label,
      loading,
      formRef,
      form,
      checkFilter,
      placeholder,
      onSubmit,
      onReset,
    };
  },
};
</script>
<style scoped></style>
