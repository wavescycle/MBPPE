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
          <el-radio-button label="PSD" />
          <el-radio-button label="DE" />
        </el-radio-group>
      </el-form-item>
      <el-form-item label="Filtered" prop="filter">
        <el-switch
          v-model="form.filter"
          :loading="loading"
          :before-change="checkFilter"
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
import { reactive, ref, computed } from "vue";
import { getFileList, postPSD, postDE } from "../utils/api";
import { ElMessage, ElLoading } from "element-plus";
export default {
  setup() {
    const loading = ref(null);
    const formRef = ref(null);
    const form = reactive({
      name: "",
      filter: false,
      method: "PSD",
      fileList: [],
    });

    const rules = {
      name: {
        required: true,
        message: "Select a file",
        trigger: "blur",
      },
    };
    getFileList().then((res) => {
      form.fileList = res.data;
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
    const onSubmit = () => {
      formRef.value.validate(async (valid) => {
        if (valid) {
          const loading = ElLoading.service({
            lock: true,
            text: "Loading",
          });
          let res = null;
          if (form.method === "PSD") {
            res = await postPSD(form.name, form.filter);
          } else {
            res = await postDE(form.name, form.filter);
          }
          loading.close();
          if (res.status === 200) ElMessage.success("success");
          else ElMessage.error(res.data);
        } else {
          return false;
        }
      });
    };
    const onReset = () => {
      formRef.value.resetFields();
    };
    return {
      formRef,
      form,
      onSubmit,
      placeholder,
      rules,
      onReset,
      checkFilter,
      loading,
    };
  },
};
</script>

<style scoped></style>
