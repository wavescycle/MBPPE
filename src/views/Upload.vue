<template>
  <el-form label-position="top">
    <div class="content-title">Upload Files</div>
    <el-form-item prop="file" class="el-form-label">
      <el-upload
          class="upload"
          action=""
          multiple
          accept=".mat"
          ref="upload"
          :http-request="uploadFile"
          :auto-upload="false"
      >
        <el-icon class="el-icon--upload">
          <upload-filled/>
        </el-icon>
        <div class="el-upload__text">
          Drop file here or <em>click to upload</em>
        </div>
        <!--        <template #tip>-->
        <!--          <div class="plugins-tips">support file type: .mat, .xlsx, .npz</div>-->
        <!--        </template>-->
      </el-upload>
    </el-form-item>
    <div class="content-title">Sampling Rate</div>
    <el-form-item prop="freq">
      <el-input-number
          v-model="freq"
          :min="0"
          placeholder="200"
          style="width: 250px"
      />
    </el-form-item>
    <div class="content-title">Format Mode</div>
    <el-form-item prop="format">
      <el-tree-select
          v-model="mode"
          :data="treeData"
          :render-after-expand="false"
          style="width: 250px"
      />
    </el-form-item>
    <el-form-item>
      <el-button type="primary" @click="onSubmit">Submit</el-button>
      <el-button @click="onReset">Reset</el-button>
    </el-form-item>
  </el-form>
</template>

<script>
import {ref} from "vue";
import {ElNotification} from "element-plus";
import {postData} from "../utils/api";

export default {
  setup() {
    const freq = ref(null);
    const upload = ref(null);
    const mode = ref("truncate")
    const padMode = ["constant", "edge", "linear_ramp", "maximum", "mean", "median", "minimum", "reflect", "symmetric", "wrap", "empty"]
    const treeData = [
      {
        value: 'truncate',
        label: 'Truncate',
      },
      {
        value: 'pad',
        label: 'Pad',
        children: padMode.map(m => {
          return {"value": m, "label": m}
        })
      }
    ]
    const onSubmit = () => {
      upload.value.submit();
    };

    const onReset = () => {
      formRef.value.resetFields();
    };

    async function uploadFile(params) {
      let file = params.file;
      let filename = file.name;
      let formData = new FormData();

      formData.append("file", file);
      formData.append("freq", freq.value || 200);
      formData.append("format", mode.value);
      let res = await postData(filename, formData, (progressEvent) => {
        params.onProgress({
          percent: Math.floor(
              (progressEvent.loaded * 100) / progressEvent.total
          ),
        });
      });
      if (res.status === 201) {
        ElNotification({
          type: "success",
          message: "success",
          "custom-class": "custom-message",
        });
      } else {
        ElNotification({
          type: "error",
          message: res.data ?? "Unexpected Error",
          "custom-class": "custom-message",
        });
        upload.abort();
      }
    }

    return {freq, uploadFile, upload, onSubmit, onReset, mode, treeData};
  },
};
</script>

<style scoped>
.content-title {
  font-weight: 500;
  line-height: 30px;
  margin: 10px 0;
  font-size: 25px;
  color: #1f2f3d;
}
</style>
