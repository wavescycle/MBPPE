<template>
  <el-container style="height: calc(100vh - 50px);">
    <el-menu
        default-active="/dashboard"
        active-text-color="#ffd04b"
        class="el-menu-vertical-demo"
        :collapse="false"
        background-color="#545c64"
        text-color="#fff"
        :router="true"
    >
      <template v-for="(item, index) in items" :key="index">
        <template v-if="item.subs">
          <el-sub-menu :index="item.index" :key="item.index">
            <template #title>
              <el-icon>
                <component :is="item.icon"/>
              </el-icon>
              <span>{{ item.title }}</span>
            </template>
            <template v-for="subItem in item.subs">
              <el-sub-menu
                  v-if="subItem.subs"
                  :index="subItem.index"
                  :key="subItem.index"
              >
                <template #title>{{ subItem.title }}</template>
                <el-menu-item
                    v-for="(threeItem, i) in subItem.subs"
                    :key="i"
                    :index="threeItem.index"
                >
                  {{ threeItem.title }}
                </el-menu-item
                >
              </el-sub-menu>
              <el-menu-item v-else :index="subItem.index" :key="subItem.index"
              >{{ subItem.title }}
              </el-menu-item>
            </template>
          </el-sub-menu>
        </template>
        <template v-else>
          <el-menu-item :index="item.index" :key="item.index">
            <el-icon>
              <component :is="item.icon"/>
            </el-icon>
            <template #title>{{ item.title }}</template>
          </el-menu-item>
        </template>
      </template>
    </el-menu>
  </el-container>
  <el-footer height="50px" style="background-color: #545c64">
    <el-input
        v-model="apiKey"
        type="password"
        placeholder="Press Enter Save key"
        show-password
        @keyup.enter="saveAPIKey"
    />
  </el-footer>
</template>
<script>
import {computed, ref} from "vue";
import {useStore} from "vuex";
import {useRoute} from "vue-router";
import {ElNotification} from "element-plus";

export default {
  setup() {
    const items = [
      {
        icon: "home-filled",
        index: "/dashboard",
        title: "Dashboard",
      },
      {
        icon: "folder-add",
        index: "/upload",
        title: "Data Upload",
      },
      {
        icon: "loading",
        title: "Data Processing",
        index: "2",
        subs: [
          {
            index: "/preprocess",
            title: "Pre-process",
          },
          {
            index: "/feature",
            title: "Analyse",
          },
        ],
      },
      {
        icon: "pie-chart",
        index: "/charts",
        title: "Visualisation",
      },
      {
        icon: "help",
        index: "/pipeline",
        title: "Pipeline",
      }, {
        icon: "DocumentAdd",
        index: "/plugin",
        title: "Plugin",
      }
    ];

    const route = useRoute();

    const onRoutes = computed(() => {
      return route.path;
    });

    const store = useStore();
    const collapse = computed(() => store.state.collapse);
    const apiKey = ref()

    const saveAPIKey = () => {
      localStorage.setItem("MBPPE-API-KEY", apiKey.value)
      ElNotification.success('Add API Key success')
    }
    return {
      items,
      onRoutes,
      collapse,
      apiKey,
      saveAPIKey
    };
  },
};
</script>

<style>
.el-menu-vertical-demo:not(.el-menu--collapse) {
  width: 200px;
  height: 100%;
  overflow: hidden;
}
</style>
