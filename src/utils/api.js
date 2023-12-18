import request from "./request";
import {URL, PORT} from "../config/config.json";
import npy from "./npy";
import Qs from "qs";

const req = new request(URL, PORT);

/**
 * @get api, config
 * @post api, data, config
 * @config https://axios-http.com/docs/req_config
 */
function delEmptyItems(data) {
    Object.keys(data).forEach(
        (key) =>
            (data[key] === null || data[key] === "" || data[key] === undefined) &&
            delete data[key]
    );
    return data;
}

function decodeArrayBuffer(res) {
    if (res.status === 200) {
        const data = npy(res.data);
        res.data = data.data;
        res.shape = data.shape;
    } else {
        res.data = new TextDecoder("utf-8").decode(res.data);
    }
    return res;
}

async function checkStatus() {
    let res = await req.get("/status");
    return res.status;
}

async function getFigure() {
    return await req.get("/getFigure", {
        responseType: "stream",
    });
}

async function getFileStatus() {
    return await req.get("/filestatus");
}

async function getData(filename, channels, pre_data = 'Raw', config = {}) {
    let res = await req.get(`/data/${filename}`, {
        params: {
            channels: channels,
            pre_data: pre_data,
            ...config
        },
        responseType: "arraybuffer",
        paramsSerializer: (params) => {
            return Qs.stringify(params, {arrayFormat: "repeat"});
        },
    });
    return decodeArrayBuffer(res);
}

async function postData(filename, file, uploadProgress) {
    return await req.post(`/data/${filename}`, file, {
        onUploadProgress: uploadProgress,
    });
}

async function deleteData(filename) {
    return await req.delete(`/data/${filename}`)
}

async function getFileList(pre_data = "") {
    return await req.get("/filelist", {
        params: {
            pre_data: pre_data,
        },
    });
}

async function getFilter(filename, channels, preData, config = {}) {
    let res = await req.get(`/filter/${filename}`, {
        params: delEmptyItems({
            channels: channels,
            pre_data: preData,
            ...config
        }),
        responseType: "arraybuffer",
        paramsSerializer: (params) => {
            return Qs.stringify(params, {arrayFormat: "repeat"});
        },
    });
    return decodeArrayBuffer(res);
}

async function postFilter(filename, channels, method, low, high, preData) {
    return await req.post(
        `/filter/${filename}`,
        delEmptyItems({
            channels: channels,
            method: method,
            low: low,
            high: high,
            pre_data: preData
        })
    );
}

async function getICA(filename, pre_data = "", config = {}) {
    let res = await req.get(`/ica/${filename}`, {
        params: {pre_data: pre_data, ...config},
        responseType: "arraybuffer",
    });
    return decodeArrayBuffer(res);
}

async function postICA(filename, pre_data = "") {
    return await req.post(`/ica/${filename}`, {
        pre_data: pre_data,
    });
}

async function getPSD(filename, pre_data = "", config = {}) {
    let res = await req.get(`/psd/${filename}`, {
        params: {pre_data: pre_data, ...config},
        responseType: "arraybuffer",
    });
    return decodeArrayBuffer(res);
}

async function postPSD(filename, pre_data = "") {
    return await req.post(`/psd/${filename}`, {
        pre_data: pre_data,
    });
}

async function getDE(filename, pre_data = "", config = {}) {
    let res = await req.get(`/de/${filename}`, {
        params: {pre_data: pre_data, ...config},
        responseType: "arraybuffer",
    });
    return decodeArrayBuffer(res);
}

async function postDE(filename, pre_data = "") {
    return await req.post(`/de/${filename}`, {
        pre_data: pre_data,
    });
}

async function getFrequency(filename, channels, pre_data = "", config = {}) {
    let res = await req.get(`/frequency/${filename}`, {
        params: delEmptyItems({pre_data: pre_data, channels: channels, ...config}),
        responseType: "arraybuffer",
    });
    return decodeArrayBuffer(res);
}

async function postFrequency(filename, channels, pre_data = "", config = {}) {
    return await req.post(`/frequency/${filename}`, delEmptyItems({
        pre_data: pre_data,
        channels: channels,
        ...config
    }));
}

async function getTimeFrequency(filename, channels, pre_data = "", config = {}) {
    let res = await req.get(`/timefrequency/${filename}`, {
        params: {pre_data: pre_data, channels: channels, ...config},
        responseType: "arraybuffer",
    });
    return decodeArrayBuffer(res);
}

async function postTimeFrequency(filename, channels, pre_data = "") {
    return await req.post(`/timefrequency/${filename}`, {
        pre_data: pre_data,
        channels: channels,
    });
}

async function download(type, filename, onDownloadProgress, pre_data = "", config = {}) {
    return await req.get(`/${type}/${filename}`, {
        params: delEmptyItems({
            // channels: channels,
            pre_data: pre_data,
            ...config
        }),
        paramsSerializer: (params) => {
            return Qs.stringify(params, {arrayFormat: "repeat"});
        },
        onDownloadProgress: onDownloadProgress,
        responseType: "blob",
    });
}

async function getPreData(filename, feature_ext = '') {
    return await req.get(`/predata/${filename}`, {
        params: delEmptyItems({
            feature_ext: feature_ext
        })
    })
}

async function getTaskStatus(task_id) {
    return await req.get(`/task${task_id ? '/' + task_id : ''}`)
}

async function getAllTaskStatus() {
    return await getTaskStatus()
}

async function getTaskData(taskId, filename, fileType, onDownloadProgress) {
    return await req.get(`/task/${taskId}/${filename}`, {
        params: {file_type: fileType},
        onDownloadProgress: onDownloadProgress,
        responseType: "blob",
    });
}

async function postTask(task) {
    return await req.post('/task', task)
}

export async function deleteTask(taskId) {
    return await req.delete(`/task/${taskId}`)
}


async function getFileTreeList() {
    return await req.get('/filetreelist')
}

async function getReference(filename, channels, pre_data, config = {}) {
    return await req.get(`/reference/${filename}`, {
        params: delEmptyItems({
            channels: channels,
            pre_data: pre_data,
            ...config
        })
    })
}

async function postReference(filename, channels, pre_data, config = {}) {
    return await req.post(`/reference/${filename}`, {
        channels: channels,
        pre_data: pre_data,
        ...config
    })
}

async function getResample(filename, channels, pre_data, config = {}) {
    return await req.get(`/resample/${filename}`, {
        params: delEmptyItems({
            channels: channels,
            pre_data: pre_data,
            ...config
        })
    })
}

async function postResample(filename, pre_data, config = {}) {
    return await req.post(`/resample/${filename}`, {
        pre_data: pre_data,
        ...config
    })
}

async function getPlugin() {
    return await req.get('/plugin')
}

async function delPlugin(plugin) {
    return await req.delete(`/plugin/${plugin}`)
}


async function postPluginHandler(filename, channels, pre_data, config = {},) {
    return await req.post(`/pluginhandler/${config.plugin}/${filename}`, {
        channels: channels,
        pre_data: pre_data,
        ...config
    })
}

async function getComments(piplineId) {
    return await req.get(`/comments/${piplineId}`)
}

async function postComments(piplineId, data) {
    return await req.post(`/comments/${piplineId}`, {data})
}

export {
    checkStatus,
    getData,
    postData,
    deleteData,
    getFileList,
    getFileStatus,
    getFilter,
    postFilter,
    getICA,
    postICA,
    getPSD,
    postPSD,
    getDE,
    postDE,
    getFrequency,
    postFrequency,
    getTimeFrequency,
    postTimeFrequency,
    download,
    getPreData,
    getTaskStatus,
    getAllTaskStatus,
    getTaskData,
    postTask,
    getFileTreeList,
    getReference,
    postReference,
    getResample,
    postResample,
    getPlugin,
    postPluginHandler,
    delPlugin,
    getComments,
    postComments
};
