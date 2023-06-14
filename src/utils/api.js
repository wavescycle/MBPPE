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
    Object.keys(data).forEach((k) => !data[k] && data[k] !== undefined && delete data[k]);
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

async function getFrequence(filename, channels = 0, pre_data = "", start = 0, end = 10) {
    let res = await req.get(`/frequence/${filename}`, {
        params: {pre_data: pre_data, channels: channels, start: start, end: end},
        responseType: "arraybuffer",
    });
    return decodeArrayBuffer(res);
}

async function postFrequence(filename, channels, pre_data = "") {
    return await req.post(`/freqfrequence/${filename}`, {
        pre_data: pre_data,
        channels: channels,
        start,
        end,
    });
}

async function getTimeFrequence(filename, channels = 0, pre_data = "", start = 0, end = 10) {
    let res = await req.get(`/timefrequence/${filename}`, {
        params: {pre_data: pre_data, channels: channels, start: start, end: end},
        responseType: "arraybuffer",
    });
    return decodeArrayBuffer(res);
}

async function postTimeFrequence(filename, channels, pre_data = "") {
    return await req.post(`/timefrequence/${filename}`, {
        pre_data: pre_data,
        channels: channels,
        start,
        end,
    });
}

async function download(type, filename, onDownloadProgress, pre_data = "", channels = []) {
    return await req.get(`/${type}/${filename}`, {
        params: delEmptyItems({
            channels: channels,
            pre_data: pre_data,
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

export {
    checkStatus,
    getData,
    postData,
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
    getFrequence,
    postFrequence,
    getTimeFrequence,
    postTimeFrequence,
    download,
    getPreData
};
