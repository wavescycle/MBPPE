import { createRouter, createWebHashHistory } from "vue-router";
import Home from "../views/Home.vue";

const routes = [
  {
    path: "/",
    redirect: "/dashboard",
  },
  {
    path: "/",
    name: "Home",
    component: Home,
    children: [
      {
        path: "/dashboard",
        name: "dashboard",
        meta: {
          title: "dashboard",
        },
        component: () =>
          import(/* webpackChunkName: "dashboard" */ "../views/Dashboard.vue"),
      },
      {
        path: "/charts",
        name: "basecharts",
        meta: {
          title: "Visualisation",
        },
        component: () =>
          import(/* webpackChunkName: "charts" */ "../views/BaseCharts.vue"),
      },
      {
        path: "/filter",
        name: "filter",
        meta: {
          title: "filter",
        },
        component: () =>
          import(/* webpackChunkName: "form" */ "../views/Filter.vue"),
      },
      {
        path: "/feature",
        name: "feature",
        meta: {
          title: "feature",
        },
        component: () =>
          import(/* webpackChunkName: "form" */ "../views/Feature.vue"),
      },
      {
        path: "/upload",
        name: "upload",
        meta: {
          title: "File Upload",
        },
        component: () =>
          import(/* webpackChunkName: "upload" */ "../views/Upload.vue"),
      },
    ],
  },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  next();
});

export default router;
