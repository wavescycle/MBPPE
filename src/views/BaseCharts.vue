<template>
  <el-container>
    <el-header>
      <el-form
          :model="form"
          ref="formRef"
          :rules="rules"
          :inline="true"
      >
        <el-form-item label="Filename" prop="name">
          <el-select
              v-model="form.name"
              :placeholder="placeholder"
              @change="fileChange"
              style="width: 150px"
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
        <el-form-item
            label="Chart"
            prop="type"
            @change="chartChange"
        >

          <el-select v-model="form.type" style="width: 150px">
            <el-option-group
                v-for="group in options"
                :key="group.label"
                :label="group.label"
            >
              <el-option
                  v-for="item in group.options"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
              />
            </el-option-group>
          </el-select>
        </el-form-item>
        <el-form-item
            label="Channels"
            prop="channels"
            v-if="form.type !== 'psdChart'"
        >
          <el-select
              v-model="form.channels"
              :multiple="multiple"
              collapse-tags
              :placeholder="channelsPlaceholder"
              :multiple-limit="8"
              style="width: 150px"
          >
            <el-option
                v-for="(ch, i) of CH_NAMES"
                :key="i"
                :label="ch"
                :value="i"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="Params" v-if="form.type.startsWith('Plugin')" prop="PluginParams">
          <el-input
              style="width: 300px"
              v-model="form.pluginParams"
              :rows="2"
              type="textarea"
          />
        </el-form-item>
        <el-form-item label="PreData" prop="preData">
          <el-select
              v-model="form.preData"
              @visible-change="getPreDataList"
              :loading="getPreDataLoading"
              style="width: 150px"
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
    </el-header>
    <el-main>
      <el-empty :image-size="350" v-show="emptyShow"/>
      <div id="main" ref="main" v-show="!emptyShow"></div>
    </el-main>
  </el-container>
</template>

<script>
import * as echarts from "echarts";
import charts from "../utils/charts";
import {getFileList, getPlugin, getPreData, postPluginHandler} from "../utils/api";
import {reactive, computed, ref, onMounted} from "vue";
import {CH_NAMES} from "../config/config.json";

export default {
  name: "basecharts",
  setup() {
    // Initializing Constants
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
      pluginParams: ""
    });
    const options = [{
      label: 'Built In',
      options: [
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
        }]
    }]
    const featureExtMap = {
      'lineChart': '',
      'psdChart': 'PSD',
      'freqChart': 'Freq',
      'timeFreqChart': 'Time_Freq'
    }
    const emptyShow = ref(true)
    // Visualization size
    // const width = 700;
    // const height = 500;
    const width = 700;
    const height = 500;
    let chart;

    let placeholder = computed(() =>
        form.fileList.length ? "Select" : "Upload data first"
    );
    let channelsPlaceholder = computed(() =>
        form.type === "lineChart" ? "8 channels are used by default" : "Select a channel"
    );
    let multiple = computed(() => form.type === "lineChart");
    let chartChange = () => {
      form.channels = [];
      form.preDataList.length = 0;
      form.preData = ''
    };

    onMounted(() => {
      getFileList().then((res) => {
        form.fileList = res.data;
      });
      getPlugin().then(res => {
        options.push({
          label: 'Plugins', options: res.data.map(item => {
            return {
              value: `Plugins$${item}`,
              label: item
            }
          })
        })
      })
      // init chart
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
    // Processing of visualization requests
    const onSubmit = () => {
      formRef.value.validate((valid) => {
        if (valid) {
          emptyShow.value = false
          if (form.channels.length === 0) {
            if (form.type === "lineChart") {
              const len = 8
              const alterChannels = new Array(len);
              for (let i = 0; i < len; i++) {
                alterChannels[i] = i;
              }

              form.channels = alterChannels;
            } else if (form.type === "freqChart" || form.type === "timeFreqChart") {
              form.channels = 0
            }
          }
          if (form.type.startsWith('Plugin')) {
            chart.imageChart(form.name,
                form.preData,
                form.channels,
                form.type.split('$')[1],
                form.pluginParams)
          } else if (typeof chart[form.type] === "function") {
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
      CH_NAMES,
      onReset,
      getPreDataList,
      getPreDataLoading,
      emptyShow
    };
  },
};
</script>

<style scoped>
#main {
  margin-top: 20px;
}
</style>
