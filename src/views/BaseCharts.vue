<template>
  <div class="container">
    <el-form
        :model="form"
        class="demo-form-inline"
        ref="formRef"
        :rules="rules"
        :inline="true"
        label-width="80px"
    >
      <el-form-item label="Filename" prop="name" style="width: 220px">
        <el-select
            v-model="form.name"
            :placeholder="placeholder"
            @change="fileChange"
        >
          <!-- :loading="true" -->
          <el-option
              v-for="(file, i) of form.fileList"
              :key="i"
              :label="file"
              :value="file"
          >
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item
          label="Chart"
          prop="type"
          @change="chartChange"
          style="width: 200px"
      >
        <el-select v-model="form.type">
          <el-option
              v-for="item in options"
              :key="item.value"
              :label="item.label"
              :value="item.value"
          />
        </el-select>
        <!-- <el-radio-group v-model="form.type" size="small">
          <el-radio-button label="lineChart">Raw</el-radio-button>
          <el-radio-button label="psdChart">PSD</el-radio-button>
          <el-radio-button label="freqChart">Frequency</el-radio-button>
          <el-radio-button label="timeFreqChart">TimeFrequency</el-radio-button>
        </el-radio-group> -->
      </el-form-item>
      <el-form-item
          label="Channels"
          prop="channels"
          v-if="form.type !== 'psdChart'"
          style="width: 240px"
      >
        <el-select
            v-model="form.channels"
            :multiple="multiple"
            collapse-tags
            :placeholder="channelsPlaceholder"
            :multiple-limit="5"
        >
          <el-option
              v-for="(file, i) of CH_NAMES"
              :key="i"
              :label="file"
              :value="i"
          ></el-option>
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
      <el-form-item>
        <el-button type="primary" @click="onSubmit">Submit</el-button>
        <el-button @click="onReset">Reset</el-button>
      </el-form-item>
    </el-form>
    <div id="main" ref="main"></div>
  </div>
</template>

<script>
import * as echarts from "echarts";
import {ElMessage} from "element-plus";
import charts from "../utils/charts";
import {getFileList, getPreData} from "../utils/api";
import {reactive, computed, ref, onMounted} from "vue";
import {CH_NAMES} from "../config/config.json";

export default {
  name: "basecharts",
  setup() {
    const rules = {
      name: [
        {required: true, message: "Select a file", trigger: "blur"},
      ],
      preData: [{required: true, message: "Select the pre data", trigger: "blur"}],
    };
    const formRef = ref(null);
    const main = ref(null);
    const loading = ref(null);
    const getPreDataLoading = ref(null)
    const form = reactive({
      name: "",
      channels: [],
      fileList: [],
      preData: "",
      preDataList: [],
      type: "lineChart",
    });
    const options = [
      {
        value: "lineChart",
        label: "Raw",
      },
      {
        value: "psdChart",
        label: "PSD",
      },
      {
        value: "freqChart",
        label: "Frequency",
      },
      {
        value: "timeFreqChart",
        label: "TimeFrequency",
      },
    ];
    const featureExtMap = {
      'lineChart': '',
      'psdChart': 'PSD',
      'freqChart': 'Freq',
      'timeFreqChart': 'Time_Freq'
    }
    const width = 1200;
    const height = 600;
    let chart;

    getFileList().then((res) => {
      form.fileList = res.data;
    });

    let placeholder = computed(() =>
        form.fileList.length ? "Select" : "Upload data first"
    );
    let channelsPlaceholder = computed(() =>
        form.type === "lineChart" ? "10 channels are used by default" : "Select a channel"
    );
    let multiple = computed(() => (form.type === "lineChart" ? true : false));
    let chartChange = () => {
      if (form.type === "lineChart") form.channels = [];
      else form.channels = "";
      form.preDataList.length = 0;
      form.preData = ''
    };
    onMounted(() => {
      const myChart = echarts.init(main.value, null, {
        width: width,
        height: height,
      });
      chart = new charts(myChart);
      chart.emptyChart();
    });

    const fileChange = () => {
      form.preDataList.length = 0;
      form.preData = ''
    };

    const getPreDataList = async (visible) => {
      getPreDataLoading.value = true
      if (visible) {
        let res = await getPreData(form.name, featureExtMap[form.type])
        if (res.status === 200) {
          form.preDataList = res.data
          getPreDataLoading.value = false
        }
      }
    }
    const checkFilter = async () => {
      loading.value = true;
      if (form.isFilter) {
        form.isFilter = false;
      } else {
        const res = await getFileList(true);
        if (res.data.indexOf(form.name) !== -1) {
          form.isFilter = true;
        } else {
          ElMessage.error(`Filter the ${form.name} first`);
        }
      }
      loading.value = false;
    };

    const onSubmit = () => {
      formRef.value.validate((valid) => {
        if (valid) {
          if (form.channels.length === 0 && form.type === "lineChart") {
            // const len = CH_NAMES.length < 5 ? CH_NAMES.length : 5;
            const len = 10
            const alterChannels = new Array(len);
            for (let i = 0; i < len; i++) {
              alterChannels[i] = i;
            }
            form.channels = alterChannels;
          }
          if (typeof chart[form.type] === "function") {
            chart[form.type](form.name, form.preData, form.channels);
          } else {
            chart.errorChart();
            return false;
          }
        } else {
          return false;
        }
      });
    };

    const onReset = () => {
      formRef.value.resetFields();
    };

    return {
      rules,
      formRef,
      loading,
      main,
      form,
      options,
      multiple,
      chartChange,
      channelsPlaceholder,
      onSubmit,
      placeholder,
      fileChange,
      checkFilter,
      CH_NAMES,
      onReset,
      getPreDataList,
      getPreDataLoading
    };
  },
};
</script>

<style scoped>
/* .container {
  padding: 10px;
  position: relative;
  border: 0px;
  width: 100%;
  height: 80%;
} */
/* .content-title {
  clear: both;
  font-weight: 400;
  line-height: 50px;
  margin: 10px 0;
  font-size: 22px;
  color: #1f2f3d;
} */
</style>
