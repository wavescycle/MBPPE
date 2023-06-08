import axios from "axios";

class request {
  constructor(URL, PORT) {
    this._request = axios.create({
      baseURL: `${URL}:${PORT}`,
      // timeout: 5000,
    });
  }
  async get(api, config = { params: {} }) {
    config.params = { ...config.params, t: new Date().getTime() };
    try {
      return await this._request.get(api, config);
    } catch (err) {
      console.log(err.response);
      return {
        status: err?.response?.status,
        data: err?.response?.data,
      };
    }
  }

  async post(api, data = {}, config = {}) {
    try {
      return await this._request.post(api, data, config);
    } catch (err) {
      console.log(err.response);
      return { status: err?.response?.status, data: err?.response?.data };
    }
  }
}

export default request;
