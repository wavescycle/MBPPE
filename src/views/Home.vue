<template>
  <el-container
    class="layout-container-demo"
    style="height: 100%; border: 0px solid #eee"
  >
    <el-aside width="200px"><v-sidebar /></el-aside>
    <el-main>
      <router-view v-slot="{ Component }">
        <transition name="move" mode="out-in">
          <!-- <keep-alive :include="tagsList"> -->
          <component :is="Component" />
          <!-- </keep-alive> -->
        </transition>
      </router-view>
    </el-main>
  </el-container>
</template>

<script>
import vSidebar from "../components/Sidebar.vue";
export default {
  components: { vSidebar },
  setup() {
    return {};
  },
};
</script>

<style scoped>
.layout-container-demo {
  position: relative;
  color: var(--el-text-color-primary);
  border: 1px solid rgb(248, 250, 251);
}
/* .layout-container-demo .el-aside {
  color: var(--el-text-color-primary);
  background: #fff !important;
  border-right: solid 1px #e6e6e6;
  box-sizing: border-box;
} */
/* .layout-container-demo .el-main {
  margin: 10px 30px 30px;
  border: 1px solid #ddd;
  border-radius: 12px;
  background-color: #fff;
  box-shadow: 0px 0px 2px #fbfbfb;
} */
</style>
