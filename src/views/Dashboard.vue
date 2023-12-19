<template>
  <div>
    <el-table :data="tableData" style="width: 100%" :border="true">
      <el-table-column prop="filename" label="Filename"/>
      <el-table-column prop="sample_rate" label="Sample Rate"/>
      <el-table-column prop="data_type" label="Data Type">
        <template #default="scope">
          <el-tree-select v-model="dataType[scope.$index]" :data="scope.row.data_type" :render-after-expand="false"
                          @change="selectChange"/>
        </template>
      </el-table-column>
      <el-table-column label="Action">
        <template #default="scope">
          <el-popconfirm
              confirm-button-text="Numpy"
              cancel-button-text="Matlab"
              icon-color="#626AEF"
              title="Choose export type"
              @confirm="exportAction(scope.$index,'npy')"
              @cancel="exportAction(scope.$index,'mat')"
          >
            <template #reference>
              <el-button>Export</el-button>
            </template>
          </el-popconfirm>
          <el-popconfirm title="All data type under this file will be deleted!"
                         @confirm="deleteAction(scope.row.filename)">
            <template #reference>
              <el-button type="danger">Delete</el-button>
            </template>
          </el-popconfirm>
          <el-progress :percentage="percent[scope.$index]" :width="24" :stroke-width="3"
                       v-show="percent[scope.$index]>0"/>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
import {download, getFileTreeList, deleteData} from "../utils/api";
import {ElNotification} from "element-plus"
import {ref, onMounted,} from "vue";

export default {
  name: "dashboard",
  setup() {
    const progressState = ref(false);
    const percent = ref([]);
    const tableData = ref(null);
    const dialogVisible = ref(false);
    const saveType = ref("data");
    const dataType = ref([])

    // Converting data into a multi-level list
    function transform(obj) {
      let result = [];
      for (let key in obj) {
        if (Array.isArray(obj[key])) {
          result.push({
            value: key,
            label: key,
            children: obj[key].map(item => ({value: `${key}.${item}`, label: `${key} > ${item}`}))
          });
        } else if (typeof obj[key] === 'object') {
          result.push({
            value: key,
            label: key,
            children: transform(obj[key])
          });
        }
      }
      return result;
    }

    const selectChange = () => {
      console.log(dataType.value)
    }
    // Delete Data Operation
    const deleteAction = (filename) => {
      deleteData(filename).then(res => {
        refreshData()
      })
    }
    // Export Data Operation
    const exportAction = (index, fileType) => {
      const rowValue = tableData.value[index]
      const typeValue = dataType.value[index]
      const types = typeValue?.split('.')
      if (types?.length > 1) {
        const method = types[0]
        const preData = types[1]
        const type = method === "Pre_Process" ? method : "Feature_Ext"

        download("data", rowValue.filename, (progressEvent) => {
          percent.value[index] = Math.floor(
              (progressEvent.loaded * 100) / progressEvent.total
          );
        }, preData, {file_type: fileType, storage_path: type, Feature_Ext: method}).then((res) => {
          const fileURL = window.URL.createObjectURL(res.data);
          const fileLink = document.createElement("a");

          fileLink.href = fileURL;
          fileLink.setAttribute("download", rowValue.filename + `.${fileType}`);
          document.body.appendChild(fileLink);
          fileLink.click();
          progressState.value = false;
        });
      } else {
        const msg = types?.length === 1 ? "You should select child Node" : "You show select data type"
        ElNotification({
          title: 'Warning',
          message: msg,
          type: 'warning',
        })
      }
    }
    const refreshData = () => {
      getFileTreeList().then((res) => {
        const data = res.data;
        dataType.value = Array.from({length: data.length})
        percent.value = new Array(data.length).fill(0);

        tableData.value = data.map(item => {
          let newItem = {...item};
          newItem.data_type = transform(item.data_type);
          return newItem;
        });

      })
    }
    onMounted(() => {
      refreshData()
    })

    return {
      progressState,
      tableData,
      dialogVisible,
      saveType,
      percent,
      dataType,
      selectChange,
      deleteAction,
      exportAction
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
