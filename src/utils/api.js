import request from "./request";
import {URL, PORT} from "../config/config.json";
import npy from "./npy";
import Qs from "qs";

const req = new request(URL, PORT);

/**
 * This file contains all the APIs for front and back interactions.
 * When designing the interface, we follow the RestfulAPI standard.
 * The get method is used to retrieve data,
 * the post method is used to add and modify data,
 * and delete is used to remove data.
 */

/**
 * @get api, config
 * @post api, data, config
 * @config https://axios-http.com/docs/req_config
 */

// Remove blank items from request parameters
function delEmptyItems(data) {
    Object.keys(data).forEach(
        (key) =>
            (data[key] === null || data[key] === "" || data[key] === undefined) &&
            delete data[key]
    );
    return data;
}

// Convert numpy data to JavaScript array
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

// Common data acquisition methods
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

// Upload local data
async function postData(filename, file, uploadProgress) {
    return await req.post(`/data/${filename}`, file, {
        onUploadProgress: uploadProgress,
    });
}

// Function to make a DELETE request to the server to delete data
async function deleteData(filename) {
    return await req.delete(`/data/${filename}`)
}

// Function to get a list of files from the server
async function getFileList(pre_data = "") {
    return await req.get("/filelist", {
        params: {
            pre_data: pre_data,
        },
    });
}

// built-in method
// Filtering/Independent Component Analysis/Reference/Resample/
// Power Spectral Density/Differential Entropy/Frequency/Time-Frequency
async function getFilter(filename, channels, preData, filterType, config = {}) {
    let res = await req.get(`/filter/${filename}`, {
        params: delEmptyItems({
            channels: channels,
            pre_data: preData,
            filter_type: filterType,
            ...config
        }),
        responseType: "arraybuffer",
        paramsSerializer: (params) => {
            return Qs.stringify(params, {arrayFormat: "repeat"});
        },
    });
    return decodeArrayBuffer(res);
}

async function postFilter(filename, channels, method, low, high, preData, filterType) {
    return await req.post(
        `/filter/${filename}`,
        delEmptyItems({
            channels: channels,
            method: method,
            low: low,
            high: high,
            pre_data: preData,
            filter_type: filterType
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

// Pipeline Task APIs
async function getTaskStatus(task_id) {
    return await req.get(`/task${task_id ? '/' + task_id : ''}`)
}

async function getAllTaskStatus() {
    return await getTaskStatus()
}

// Get the data processed by the pipeline
async function getTaskData(taskId, filename, fileType, onDownloadProgress) {
    return await req.get(`/task/${taskId}/${filename}`, {
        params: {file_type: fileType},
        onDownloadProgress: onDownloadProgress,
        responseType: "blob",
    });
}

// create pipeline task
async function postTask(task) {
    return await req.post('/task', task)
}

// delete pipeline task
export async function deleteTask(taskId) {
    return await req.delete(`/task/${taskId}`)
}


async function getFileTreeList() {
    return await req.get('/filetreelist')
}

// Plugin APis
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

// Comments APIs
async function getComments(piplineId) {
    return await req.get(`/comments/${piplineId}`)
}

async function postComments(piplineId, data) {
    return await req.post(`/comments/${piplineId}`, {data})
}

export {
    getData,
    postData,
    deleteData,
    getFileList,
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
