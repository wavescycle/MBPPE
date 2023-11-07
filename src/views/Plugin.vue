<template>
  <el-container>
    <el-header>
      <el-row justify="end">
        <el-col :span="4">
          <el-upload
              :limit="1"
              :action="UPLOAD_URL"
              :auto-upload="true"
              :on-success="refreshPlugin"
              class="plugin-demo"
          >
            <template #trigger>
              <el-button icon="circle-plus" type="primary" circle/>
            </template>
            <el-button style="margin-left: 20px" icon="refresh" type="primary" circle @click="refreshPlugin"/>
          </el-upload>
        </el-col>
      </el-row>
    </el-header>
    <el-main>
      <el-table :data="tableData" style="width: 100%">
        <el-table-column prop="pluginName" label="Plugin"/>
        <el-table-column label="Action">
          <template #default="scope">
            <el-popconfirm title="All data type under this file will be deleted!"
                           @confirm="deleteAction(scope.row.pluginName)">
              <template #reference>
                <el-button type="danger">Delete</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-main>
  </el-container>
</template>
<script>
import {URL, PORT} from "../config/config.json";
import {onMounted, ref} from "vue";
import {getPlugin, delPlugin} from "../utils/api";

export default {
  name: "plugin",
  setup() {
    const UPLOAD_URL = `${URL}:${PORT}/plugin`
    const tableData = ref(null);
    tableData.value = ['2016-05-03', '2017-05-03'
    ]
    const deleteAction = (pluginName) => {
      delPlugin(pluginName).then(res => {
        if (res.status === 200) {
          refreshPlugin()
        }
      })

    }
    const refreshPlugin = () => {
      getPlugin().then(res => {
        tableData.value = res.data.map(item => {
          return {
            pluginName: item
          }
        })
      })
    }
    onMounted(() => {
      refreshPlugin()

    })
    return {UPLOAD_URL, tableData, deleteAction, refreshPlugin}
  }
}
</script>
<style>
.plugin-demo {
  width: 100px;
  display: flex;
//justify-content: space-between;
}
</style>
