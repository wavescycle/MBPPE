<template>
  <el-form label-position="top">
    <div class="content-title">Upload files</div>
    <el-form-item prop="file" class="el-form-label">
      <el-upload
        class="upload"
        action=""
        multiple
        accept=".mat,.xlsx,.npz"
        ref="upload"
        :http-request="uploadFile"
        :auto-upload="false"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          Drop file here or <em>click to upload</em>
        </div>
        <template #tip>
          <div class="plugins-tips">support file type: .mat, .xlsx, .npz</div>
        </template>
      </el-upload>
    </el-form-item>
    <div class="content-title">Sampling rate</div>
    <el-form-item prop="freq">
      <el-input-number
        v-model="freq"
        :min="0"
        placeholder="200"
        style="width: 350px"
      />
    </el-form-item>
    <el-form-item>
      <el-button type="primary" @click="onSubmit">Submit</el-button>
      <el-button @click="onReset">Reset</el-button>
    </el-form-item>
  </el-form>
</template>

<script>
import { ref } from "vue";
import { ElNotification } from "element-plus";
import { postData } from "../utils/api";

export default {
  setup() {
    const freq = ref(null);
    const upload = ref(null);
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
    return { freq, uploadFile, upload, onSubmit, onReset };
  },
};
</script>

<style scoped>
.content-title {
  font-weight: 500;
  /* line-height: 50px; */
  margin: 10px 0;
  font-size: 25px;
  color: #1f2f3d;
}
</style>
