import request from "./request";
import { URL, PORT } from "../config/config.json";
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
async function getData(filename, channels) {
  let res = await req.get(`/data/${filename}`, {
    params: { channels: channels },
    responseType: "arraybuffer",
    paramsSerializer: (params) => {
      return Qs.stringify(params, { arrayFormat: "repeat" });
    },
  });
  return decodeArrayBuffer(res);
}
async function postData(filename, file, uploadProgress) {
  return await req.post(`/data/${filename}`, file, {
    onUploadProgress: uploadProgress,
  });
}

async function getFileList(isFilter = false) {
  return await req.get("/filelist", {
    params: {
      isFilter: isFilter,
    },
  });
}

async function getFilter(filename, channels) {
  let res = await req.get(`/filter/${filename}`, {
    params: delEmptyItems({
      channels: channels,
    }),
    responseType: "arraybuffer",
    paramsSerializer: (params) => {
      return Qs.stringify(params, { arrayFormat: "repeat" });
    },
  });
  return decodeArrayBuffer(res);
}
async function postFilter(filename, channels, method, low, high) {
  return await req.post(
    `/filter/${filename}`,
    delEmptyItems({
      channels: channels,
      method: method,
      low: low,
      high: high,
    })
  );
}
async function getICA(filename, isFilter = false) {
  let res = await req.get(`/ica/${filename}`, {
    params: { isFilter: isFilter },
    responseType: "arraybuffer",
  });
  return decodeArrayBuffer(res);
}
async function postICA(filename, isFilter = false) {
  return await req.post(`/ica/${filename}`, {
    isFilter: isFilter,
  });
}
async function getPSD(filename, isFilter = false) {
  let res = await req.get(`/psd/${filename}`, {
    params: { isFilter: isFilter },
    responseType: "arraybuffer",
  });
  return decodeArrayBuffer(res);
}
async function postPSD(filename, isFilter = false) {
  return await req.post(`/psd/${filename}`, {
    isFilter: isFilter,
  });
}
async function getDE(filename, isFilter = false) {
  let res = await req.get(`/de/${filename}`, {
    params: { isFilter: isFilter },
    responseType: "arraybuffer",
  });
  return decodeArrayBuffer(res);
}
async function postDE(filename, isFilter = false) {
  return await req.post(`/de/${filename}`, {
    isFilter: isFilter,
  });
}
async function getFrequence(filename, channels = 0, isFilter = false, start = 0, end = 10) {
  let res = await req.get(`/frequence/${filename}`, {
    params: { isFilter: isFilter, channels: channels, start: start, end: end },
    responseType: "arraybuffer",
  });
  return decodeArrayBuffer(res);
}
async function postFrequence(filename, channels, isFilter = false) {
  return await req.post(`/freqfrequence/${filename}`, {
    isFilter: isFilter,
    channels: channels,
    start,
    end,
    isFilter: false,
  });
}
async function getTimeFrequence(filename, channels = 0, isFilter = false, start = 0, end = 10) {
  let res = await req.get(`/timefrequence/${filename}`, {
    params: { isFilter: isFilter, channels: channels, start: start, end: end },
    responseType: "arraybuffer",
  });
  return decodeArrayBuffer(res);
}

async function postTimeFrequence(filename, channels, isFilter = false) {
  return await req.post(`/timefrequence/${filename}`, {
    isFilter: isFilter,
    channels: channels,
    start,
    end,
    isFilter: false,
  });
}
async function download(type, filename, onDownloadProgress, isFilter = false, channels = []) {
  return await req.get(`/${type}/${filename}`, {
    params: delEmptyItems({
      channels: channels,
      isFilter: isFilter,
    }),
    paramsSerializer: (params) => {
      return Qs.stringify(params, { arrayFormat: "repeat" });
    },
    onDownloadProgress: onDownloadProgress,
    responseType: "blob",
  });
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
};
