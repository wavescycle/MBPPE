<template>
  <div>
    <el-table :data="tableData" style="width: 100%" :border="true">
      <el-table-column prop="Filename" label="Filename" />
      <el-table-column prop="SampleRate" label="Sample Rate" />
      <el-table-column prop="Filter" label="Filter" />
      <el-table-column label="Save">
        <template #default="scope">
          <el-button @click="dialogVisible = true">SAVE</el-button>
          <el-dialog v-model="dialogVisible" title="SAVE" width="30%">
            <span>Filtered data </span><el-switch v-model="isfilter" />
            <el-select
              v-model="saveType"
              class="m-2"
              style="padding-left: 15px"
            >
              <el-option
                v-for="item in options"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
            <template #footer>
              <span class="dialog-footer">
                <el-button @click="dialogVisible = false">Cancel</el-button>
                <el-button type="primary" @click="save(scope.row)"
                  >Confirm</el-button
                >
              </span>
            </template>
          </el-dialog>
        </template>
      </el-table-column>
    </el-table>
    <el-progress :percentage="percent" :width=200 v-show="progressState" />
  </div>
</template>

<script>
// import Schart from "vue-schart";
import { getFileStatus, download } from "../utils/api";
import { CH_NAMES } from "../config/config.json";
import { ref } from "vue";
export default {
  name: "dashboard",
  setup() {
    const progressState = ref(false);
    const percent = ref(0);
    const tableData = ref(null);
    const dialogVisible = ref(false);
    const isfilter = ref(false);
    const saveType = ref("data");
    getFileStatus().then((res) => {
      tableData.value = res.data;
    });
    const save = async (row) => {
      const channels = CH_NAMES.map((e, i) => i);
      console.log(channels);
      dialogVisible.value = false;
      progressState.value = true;
      let type = saveType.value;
      if (type === "data" && isfilter.value) {
        type = "filter";
      }
      console.log(type);
      download(
        type,
        row.Filename,
        (progressEvent) => {
          percent.value = Math.floor(
            (progressEvent.loaded * 100) / progressEvent.total
          );
        },
        isfilter.value,
        channels
      ).then((res) => {
        var fileURL = window.URL.createObjectURL(res.data);
        var fileLink = document.createElement("a");

        fileLink.href = fileURL;
        fileLink.setAttribute("download", row.Filename + ".npy");
        document.body.appendChild(fileLink);
        fileLink.click();
        progressState.value = false;
      });
    };

    const options = [
      {
        value: "data",
        label: "Raw",
      },
      {
        value: "psd",
        label: "PSD",
      },
      {
        value: "de",
        label: "DE",
      },
    ];
    return {
      progressState,
      tableData,
      dialogVisible,
      isfilter,
      saveType,
      save,
      percent,
      options,
    };
  },
};
</script>

<style scoped>
/* .el-row {
  margin-bottom: 20px;
}

.grid-content {
  display: flex;
  align-items: center;
  height: 100px;
}

.grid-cont-right {
  flex: 1;
  text-align: center;
  font-size: 14px;
  color: #999;
}

.grid-num {
  font-size: 30px;
  font-weight: bold;
}

.grid-con-icon {
  font-size: 50px;
  width: 100px;
  height: 100px;
  text-align: center;
  line-height: 100px;
  color: #fff;
}

.grid-con-1 .grid-con-icon {
  background: rgb(45, 140, 240);
}

.grid-con-1 .grid-num {
  color: rgb(45, 140, 240);
}

.grid-con-2 .grid-con-icon {
  background: rgb(100, 213, 114);
}

.grid-con-2 .grid-num {
  color: rgb(45, 140, 240);
}

.grid-con-3 .grid-con-icon {
  background: rgb(242, 94, 67);
}

.grid-con-3 .grid-num {
  color: rgb(242, 94, 67);
}

.user-info {
  display: flex;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 2px solid #ccc;
  margin-bottom: 20px;
}

.user-avator {
  width: 120px;
  height: 120px;
  border-radius: 50%;
}

.user-info-cont {
  padding-left: 50px;
  flex: 1;
  font-size: 14px;
  color: #999;
}

.user-info-cont div:first-child {
  font-size: 30px;
  color: #222;
}

.user-info-list {
  font-size: 14px;
  color: #999;
  line-height: 25px;
}

.user-info-list span {
  margin-left: 70px;
}

.mgb20 {
  margin-bottom: 20px;
}

.todo-item {
  font-size: 14px;
}

.todo-item-del {
  text-decoration: line-through;
  color: #999;
}

.schart {
  width: 100%;
  height: 300px;
} */
</style>
