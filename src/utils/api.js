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

async function getData(filename, channels, pre_data = 'Raw') {
    let res = await req.get(`/data/${filename}`, {
        params: {
            channels: channels,
            pre_data: pre_data
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

async function getFilter(filename, channels, preData) {
    let res = await req.get(`/filter/${filename}`, {
        params: delEmptyItems({
            channels: channels,
            pre_data: preData
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

async function getICA(filename, pre_data = "") {
    let res = await req.get(`/ica/${filename}`, {
        params: {pre_data: pre_data},
        responseType: "arraybuffer",
    });
    return decodeArrayBuffer(res);
}

async function postICA(filename, pre_data = "") {
    return await req.post(`/ica/${filename}`, {
        pre_data: pre_data,
    });
}

async function getPSD(filename, pre_data = "") {
    let res = await req.get(`/psd/${filename}`, {
        params: {pre_data: pre_data},
        responseType: "arraybuffer",
    });
    return decodeArrayBuffer(res);
}

async function postPSD(filename, pre_data = "") {
    return await req.post(`/psd/${filename}`, {
        pre_data: pre_data,
    });
}

async function getDE(filename, pre_data = "") {
    let res = await req.get(`/de/${filename}`, {
        params: {pre_data: pre_data},
        responseType: "arraybuffer",
    });
    return decodeArrayBuffer(res);
}

async function postDE(filename, pre_data = "") {
    return await req.post(`/de/${filename}`, {
        pre_data: pre_data,
    });
}

async function getFrequency(filename, channels = 0, pre_data = "", start = null, end = null) {
    let res = await req.get(`/frequency/${filename}`, {
        params: delEmptyItems({pre_data: pre_data, channels: channels, start: start, end: end}),
        responseType: "arraybuffer",
    });
    return decodeArrayBuffer(res);
}

async function postFrequency(filename, channels, pre_data = "") {
    return await req.post(`/frequency/${filename}`, {
        pre_data: pre_data,
        channels: channels,
        start,
        end,
    });
}

async function getTimeFrequency(filename, channels = 0, pre_data = "", start = 0, end = 10) {
    let res = await req.get(`/timefrequency/${filename}`, {
        params: {pre_data: pre_data, channels: channels, start: start, end: end},
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

async function download(type, filename, onDownloadProgress, pre_data = "", channels = [], need_axis = false) {
    return await req.get(`/${type}/${filename}`, {
        params: delEmptyItems({
            channels: channels,
            pre_data: pre_data,
            need_axis: need_axis
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

async function getTaskData(task_id, filename, onDownloadProgress) {
    return await req.get(`/task/${task_id}/${filename}`, {
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
    getFileTreeList
};
