<template>
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
</template>
<script>
import {computed} from "vue";
import {useStore} from "vuex";
import {useRoute} from "vue-router";

export default {
  setup() {
    const items = [
      {
        icon: "home-filled",
        index: "/dashboard",
        title: "HomePage",
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
            index: "/filter",
            title: "Pre-processing",
          },
          {
            index: "/feature",
            title: "Feature extraction",
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
      },
    ];

    const route = useRoute();

    const onRoutes = computed(() => {
      return route.path;
    });

    const store = useStore();
    const collapse = computed(() => store.state.collapse);

    return {
      items,
      onRoutes,
      collapse,
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
