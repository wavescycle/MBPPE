import {createRouter, createWebHashHistory} from "vue-router";
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
                    title: "Dashboard",
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
                path: "/preprocess",
                name: "preprocess",
                meta: {
                    title: "PreProcess",
                },
                component: () =>
                    import(/* webpackChunkName: "form" */ "../views/PreProcess.vue"),
            },
            {
                path: "/feature",
                name: "feature",
                meta: {
                    title: "Feature",
                },
                component: () =>
                    import(/* webpackChunkName: "form" */ "../views/Feature.vue"),
            },
            {
                path: "/upload",
                name: "upload",
                meta: {
                    title: "FileUpload",
                },
                component: () =>
                    import(/* webpackChunkName: "upload" */ "../views/Upload.vue"),
            },
            {
                path: "/pipeline",
                name: "pipeline",
                meta: {
                    title: "Pipeline",
                },
                component: () =>
                    import(/* webpackChunkName: "dashboard" */ "../views/Pipeline.vue"),
            }
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
