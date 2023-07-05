<template>
  <el-container>
    <el-header>
      <el-row justify="end">
        <el-col :span="6">
          <el-button icon="circle-plus" circle @click="dialogVisible=true"/>
          <el-button icon="refresh" circle @click="refreshTasks"/>
        </el-col>
      </el-row>
    </el-header>
    <el-main style="min-height: 600px;">
      <el-empty :image-size="300" v-show="emptyShow"/>
      <el-row justify="center"
              align="middle"
              :gutter="20"
              class="pipeline-row"
              v-for="task in taskList" :key="task.task_id">
        <el-col :span="14">
          <el-steps :active="task.current_task.progress+1" finish-status="success"
                    :process-status="task.current_task.status.toLowerCase()"
                    simple>
            <el-step :title="task.task_id.slice(0, 8)" icon="collection" status="process"/>
            <el-step :title="task.current_task.filename" icon="document" status="process"/>
            <el-step v-for="info in task.task_info" :title="info.task.method"/>
          </el-steps>
        </el-col>
        <el-col :span="1">
          <el-progress class="pipeline-progress"
                       type="circle"
                       :percentage="task.current_task.sum_progress_percent"
                       :width="50"
                       :stroke-width="4"
                       @click="showDrawer(task.task_id)"/>
        </el-col>
      </el-row>
      <el-dialog
          v-model="dialogVisible"
          width="30%"
          center
          @opened="dialogOpened"
          @closed="dialogClosed"
          custom-class="task-dialog"
          :close-on-click-modal="false"
      >
        <template #title>
          <el-steps :active="currentTaskIndex" finish-status="success">
            <el-step title="Step 1" description="Choose File"/>
            <el-step :title="'Step'+(index+1)" v-for="(item,index) in taskAddData.tasks"
                     :description="item.task.method"/>
          </el-steps>
        </template>
        <el-form ref="taskAddRef" :model="taskAddData" label-position="right" label-width="150px">
          <template v-if="currentTaskIndex===0">
            <el-form-item label="Filename" prop="filenames" required>
              <el-select
                  v-model="taskAddData.filenames"
                  multiple
                  collapse-tags
                  clearable
              >
                <el-option
                    v-for="(file, i) of fileList"
                    :key="i"
                    :label="file"
                    :value="file"
                >
                </el-option>
              </el-select>
            </el-form-item>
            <el-form-item
                label="Channels"
                prop="channels"
            >
              <el-select
                  v-model="taskAddData.channels"
                  multiple
                  collapse-tags
                  placeholder="Default full selection"
                  clearable
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
          </template>
          <template v-if="currentTaskIndex>0">
            <el-form ref="taskStepRef" :model="taskStepInfo" label-width="150px">
              <el-tabs v-model="taskTabRef" class="demo-tabs" type="card" stretch>
                <el-tab-pane label="Pre-Process" name="pre-process">
                  <el-form-item label="Method" prop="method" required>
                    <el-radio-group v-model="taskStepInfo.method">
                      <el-radio-button label="Filter"/>
                      <el-radio-button label="ICA"/>
                    </el-radio-group>
                  </el-form-item>
                  <el-form-item
                      label="Filter"
                      prop="info.method"
                      v-if="taskStepInfo.method === 'Filter'"
                      required
                  >
                    <el-select v-model="taskStepInfo.info.method" placeholder="Select">
                      <el-option key="low" label="Low-pass filter" value="low"></el-option>
                      <el-option key="high" label="High-pass filter" value="high"></el-option>
                      <el-option key="band" label="Bandpass filter" value="band"></el-option>
                    </el-select>
                  </el-form-item>
                  <el-form-item
                      :label="label.low"
                      prop="info.low"
                      v-if="
          taskStepInfo.method === 'Filter' &&
          (taskStepInfo.info.method === 'low' || taskStepInfo.info.method === 'band')
        "
                      required

                  >
                    <el-col :span="8">
                      <el-input
                          v-model="taskStepInfo.info.low"
                          placeholder="input"
                          type="number"
                          :min="0"
                      />
                    </el-col>
                  </el-form-item>
                  <el-form-item
                      :label="label.high"
                      prop="info.high"
                      v-if="
          taskStepInfo.method === 'Filter' &&
          (taskStepInfo.info.method === 'high' || taskStepInfo.info.method === 'band')
        "
                      required

                  >
                    <el-col :span="8">
                      <el-input
                          v-model="taskStepInfo.info.high"
                          placeholder="input"
                          type="number"
                          :min="0"
                      />
                    </el-col>
                  </el-form-item>
                </el-tab-pane>
                <el-tab-pane label="Feature Ext" name="feature-ext">
                  <el-form-item label="Method" prop="method" required>
                    <el-radio-group v-model="taskStepInfo.method">
                      <el-radio-button label="PSD"/>
                      <el-radio-button label="DE"/>
                    </el-radio-group>
                  </el-form-item>
                </el-tab-pane>
              </el-tabs>
            </el-form>
          </template>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="decreaseIndex"
                       :disabled="currentTaskIndex===0">Pre</el-button>
            <el-button @click="increaseIndex(currentTaskIndex===0?taskAddRef:taskStepRef)">Next</el-button>
            <el-button type="primary" @click="submitTask(taskStepRef)"
                       :disabled="currentTaskIndex===0">Confirm</el-button>
          </span>
        </template>
      </el-dialog>
      <el-drawer
          v-model="drawer"
          :title="drawerTitle"
          size="25%"
          @open="drawerOpen"
      >
        <el-skeleton :rows="8" :loading="drawerLoading" animated>
          <el-table
              ref="multipleTableRef"
              :data="tableData"
              style="width: 100%"
          >
            <el-table-column type="selection" width="55" :selectable="selectableJudge"/>
            <el-table-column prop="filename" label="Filename"/>
            <el-table-column prop="status" label="Status">
              <template #default="scope">
                <el-tag
                    :type="tagStatusTypes[scope.row.status] || tagStatusTypes.default"
                    disable-transitions
                    class="pipeline-tag"
                    v-show="taskDataExportProgress[scope.$index]===0"
                >{{ scope.row.status }}
                </el-tag>
                <el-progress :percentage="taskDataExportProgress[scope.$index]"
                             v-show="taskDataExportProgress[scope.$index]!==0"/>
              </template>

            </el-table-column>
          </el-table>
          <div style="margin-top: 20px">
            <el-button @click="download(drawerTitle)">Export</el-button>
            <el-button @click="clear()">Clear</el-button>
            <el-popconfirm title="Delete all task Data?" @confirm="removeSpecialTask(drawerTitle)">
              <template #reference>
                <el-button type="danger">Remove</el-button>
              </template>
            </el-popconfirm>

          </div>

          <el-descriptions title="Task Info" :column="1" style="margin-top: 20px" border>
            <el-descriptions-item label="Channels">
              <el-collapse>
                <el-collapse-item name="Channels">
                  <template #title>
                    Click to View Details
                  </template>
                  <highlightjs autodetect :code="JSON.stringify(specialTaskInfo.channels,null,2)"/>
                </el-collapse-item>
              </el-collapse>
            </el-descriptions-item>
            <el-descriptions-item label="Params">
              <highlightjs autodetect :code="JSON.stringify(specialTaskInfo.task_info,null,2)"/>
            </el-descriptions-item>
          </el-descriptions>
        </el-skeleton>
      </el-drawer
      >
    </el-main>
    <el-footer style="text-align: center;">
      <p style="color: #909399">Click progress to get more information</p>
    </el-footer>
  </el-container>

</template>
<script>
import {ref, reactive, computed, onMounted} from 'vue'
import {ElTable} from 'element-plus'
import {getAllTaskStatus, getTaskStatus, postTask, getFileList, deleteTask, getTaskData} from "../utils/api";
import {CH_NAMES} from "../config/config.json";

export default {
  name: "pipeline",
  setup() {
    const drawer = ref(false)
    const drawerLoading = ref(true)
    const multipleTableRef = ref(typeof ElTable)
    const tableData = ref(null);
    const taskList = ref(null)
    const drawerTitle = ref('')
    const dialogVisible = ref(false)
    const currentTaskIndex = ref(0)
    const taskAddRef = ref(null)
    const taskTabRef = ref('pre-process')
    const fileList = ref([])
    const emptyShow = ref(true)
    const specialTaskInfo = ref(null)
    const taskAddData = reactive({
      filenames: [],
      channels: [],
      tasks: [],
      info: {}
    })
    const taskStepRef = ref(null)
    const taskStepInfo = reactive({
          "method": "",
          "info": {}
        }
    )
    const taskDataExportProgress = ref([])
    const tagStatusTypes = {
      'SUCCESS': 'success',
      'ERROR': 'danger',
      'WAIT': 'info',
      'default': ''
    }
    const progressStatusTypes = {
      ...tagStatusTypes,
      'ERROR': 'exception',
      'WAIT': 'warning',
    }
    const drawerOpen = () => {
      drawerLoading.value = true
    }
    const dialogOpened = () => {
      getFileList("Raw").then(resp => {
        fileList.value = resp.data
      })
    }
    const download = (taskId) => {
      let select = multipleTableRef.value.getSelectionRows()
      for (let s of select) {
        const filename = s.filename
        const index = tableData.value.findIndex(e => e.filename === filename)
        getTaskData(taskId, filename, (progressEvent) => {
          taskDataExportProgress.value[index] = Math.floor(
              (progressEvent.loaded * 100) / progressEvent.total
          );
        }).then((res) => {
          const fileURL = window.URL.createObjectURL(res.data);
          const fileLink = document.createElement("a");

          fileLink.href = fileURL;
          fileLink.setAttribute("download", filename + ".npy");
          document.body.appendChild(fileLink);
          fileLink.click();
        });
      }
    }
    const clear = () => {
      multipleTableRef.value.clearSelection()

    }
    const selectableJudge = (row, index) => {
      return row.status === 'SUCCESS'
    }

    const calculatePercentage = (task) => {
      const status = task.status_info
      const successStatus = status.filter(item => item.status === 'SUCCESS').length
      return Number((successStatus / status.length * 100).toFixed(2))
    }
    const showDrawer = async (taskId) => {
      drawerTitle.value = taskId
      drawer.value = true
      let resp = await getTaskStatus(taskId)
      tableData.value = resp.data.status_info
      taskDataExportProgress.value = new Array(resp.data.status_info.length).fill(0)
      const channels = resp.data.channels.map((e) => CH_NAMES[e]);

      specialTaskInfo.value = {task_info: resp.data.task_info, channels}
      drawerLoading.value = false
    }
    const decreaseIndex = () => {
      if (currentTaskIndex.value > 0) {
        currentTaskIndex.value--;
        if (taskAddData.tasks[currentTaskIndex.value - 1]) {
          Object.assign(taskStepInfo, taskAddData.tasks[currentTaskIndex.value - 1]['task'])
        }
        switchTab()
      }
    }
    const increaseIndex = (validateRef) => {
      validateTaskForm(validateRef).then(valid => {
        if (valid && currentTaskIndex.value > 0) {
          switchTab()
          if (currentTaskIndex.value < taskAddData.tasks.length) {
            Object.assign(taskStepInfo, taskAddData.tasks[currentTaskIndex.value]['task'])
          } else {
            // deep copy
            addTaskToData()
            Object.assign(taskStepInfo, {
              "method": "",
              "info": {}
            })
          }
        } else {
          if (taskAddData.channels.length === 0) {
            taskAddData.channels = CH_NAMES.map((e, i) => i);
          }
        }
        currentTaskIndex.value++
      })
    }

    const validateTaskForm = async (validateRef) => {
      return await validateRef.validate()
    }

    const label = computed(() => {
      let labels = {
        low: "Cutoff Frequency",
        high: "Cutoff Frequency",
      };
      if (taskStepInfo.info.method === "band") {
        labels.low = "Lowest Frequency";
        labels.high = "Highest Frequency";
      }
      return labels;
    });

    const refreshTasks = async () => {
      let resp = await getAllTaskStatus()
      taskList.value = resp.data
      if (resp.data?.length > 0) {
        emptyShow.value = false
      }
      // taskList.value = new Array(10).fill({
      //   "current_task": {
      //     "filename": "4_20140621.mat",
      //     "progress": 2,
      //     "status": "SUCCESS"
      //   },
      //   "status_info": [
      //     {
      //       "filename": "4_20140621.mat",
      //       "status": "SUCCESS"
      //     }
      //   ],
      //   "task_id": "8b6c36fba5904916b346fb0554b67ace",
      //   "task_info": [
      //     {
      //       "seq": 1,
      //       "task": {
      //         "info": {
      //           "low": "40",
      //           "method": "low"
      //         },
      //         "method": "Filter"
      //       }
      //     },
      //     {
      //       "seq": 2,
      //       "task": {
      //         "info": {},
      //         "method": "ICA"
      //       }
      //     },
      //     {
      //       "seq": 3,
      //       "task": {
      //         "info": {},
      //         "method": "PSD"
      //       }
      //     },
      //     {
      //       "seq": 4,
      //       "task": {
      //         "info": {},
      //         "method": ""
      //       }
      //     }
      //   ]
      // })
    }

    const submitTask = (validateRef) => {
      validateRef.validate((valid) => {
        if (valid) {
          addTaskToData()
          postTask(taskAddData).then(res => {
            refreshTasks()
          })

          dialogVisible.value = false
        }
      })
    }
    const dialogClosed = () => {
      currentTaskIndex.value = 0
      taskTabRef.value = 'pre-process'

      Object.assign(taskAddData, {
        filenames: [],
        channels: [],
        tasks: []
      })
      Object.assign(taskStepInfo, {
        method: "",
        info: {}
      })
    }

    const removeSpecialTask = (taskId) => {
      deleteTask(taskId).then(res => {
        location.reload();
      })
    }

    const addTaskToData = () => {
      taskAddData.tasks.push(JSON.parse(JSON.stringify({seq: currentTaskIndex.value, task: taskStepInfo})))
    }

    onMounted(() => {
      refreshTasks()
    });

    const switchTab = () => {
      if (taskStepInfo.method === 'Filter' || taskStepInfo.method === 'ICA') {
        taskTabRef.value = 'pre-process'
      } else {
        taskTabRef.value = 'feature-ext'
      }
    }


    return {
      drawer,
      drawerLoading,
      drawerTitle,
      drawerOpen,
      showDrawer,
      tableData,
      multipleTableRef,
      download,
      clear,
      selectableJudge,
      tagStatusTypes,
      progressStatusTypes,
      taskList,
      calculatePercentage,
      dialogVisible,
      taskAddData,
      fileList,
      CH_NAMES,
      currentTaskIndex,
      decreaseIndex,
      increaseIndex,
      taskAddRef,
      taskStepInfo,
      label,
      taskTabRef,
      submitTask,
      dialogClosed,
      refreshTasks,
      dialogOpened,
      taskStepRef,
      emptyShow,
      specialTaskInfo,
      removeSpecialTask,
      taskDataExportProgress
    }
  }
}
</script>

<style scoped>
.pipeline-progress:hover {
  cursor: pointer;
}

.pipeline-tag {
  width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.el-row {
  margin-bottom: 20px;
}

.el-row:last-child {
  margin-bottom: 0;
}
</style>

<style>

.task-dialog {
  min-width: 480px;
}

.el-dropdown-link {
  cursor: pointer;
  color: var(--el-color-primary);
  display: flex;
  align-items: center;
}
</style>
