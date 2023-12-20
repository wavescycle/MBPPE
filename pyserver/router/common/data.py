from pyserver.common.decorator import init_channels, init_data
from pyserver.common.utils import stream_data, get_data
from pyserver.common.customSchema import DataSchema
from pyserver.common.constant import DATA_STORAGE
from flask import send_file, jsonify, request
from flask_restful import Resource
import numpy as np
from scipy.io import loadmat
import pickle

ALLOWED_EXTENSIONS = {'mat', 'npz', 'xlsx'}


class PreData(Resource):
    def get(self, filename):
        params = request.args
        feature_ext = params.get('feature_ext')

        if feature_ext is None:
            pre_data = DATA_STORAGE[filename]['Pre_Process']
            pre_data_keys = [k for k, v in pre_data.items() if v is not None]
        else:
            try:
                pre_data = DATA_STORAGE[filename]['Feature_Ext']
                pre_data_keys = [key for key, values in pre_data.items() if values.get(feature_ext) is not None]
            except KeyError as e:
                pre_data_keys = []
        return jsonify(pre_data_keys)


class Data(Resource):

    @init_data(DataSchema)
    @init_channels(None)
    def get(self, **kwargs):
        data, is_none = get_data(**kwargs)
        need_axis = kwargs['params']['need_axis']
        sample_rate = kwargs['info']['sample_rate']
        file_type = kwargs['params']['file_type']
        return send_file(stream_data(data, need_axis, sample_rate, file_type=file_type),
                         mimetype="application/octet-stream")

    @init_data()
    def post(self, **kwargs):
        freq = request.form['freq']
        format_mode = request.form['format']
        plugin = request.form['plugin']
        file = request.files['file']
        filename = kwargs['filename']
        storage = kwargs['storage']
        storage_type = kwargs['modify_storage_type']
        info = kwargs['info']
        is_allowed, file_type = allowed_file(filename)
        if file and is_allowed:
            # read file use stream
            if plugin:
                params = request.form['plugin_params']
                storage[storage_type] = PM.get_plugin(plugin).reader(file.stream, params, info)
            else:
                storage[storage_type] = transform_data(file.stream, file_type, format_mode)
            info['sample_rate'] = int(freq)
            return 'CREATED', 201
        else:
            return 'Not support file', 400

    def delete(self, filename):
        del DATA_STORAGE[filename]
        return 'Ok'


def transform_data(raw, file_type, format_mode):
    return getattr(Load, file_type)(raw, format_mode)


def allowed_file(filename):
    if '.' in filename:
        file_type = filename.rsplit('.', 1)[1].lower()
        return file_type in ALLOWED_EXTENSIONS, file_type
    else:
        return False, None


class Load:
    @staticmethod
    def mat(file, mode='truncate'):
        data = loadmat(file)

        for e in ['__header__', '__version__', '__globals__']:
            del data[e]

        if mode == 'truncate':
            return truncate(data)
        else:
            return pad(data, mode)

    @staticmethod
    def npz(file):
        return pickle.loads(file["data"]).values()

    @staticmethod
    def xlsx(file):
        for table in file.sheet():
            nrows = table.nrows
            return np.array([x for j in range(nrows) for x in table.row_values(j)])


def truncate(data):
    min_len = np.min([v.shape[1] for v in data.values()])
    return np.hstack([v[:, :min_len] for v in data.values()])


def pad(data, mode):
    max_len = np.max([v.shape[1] for v in data.values()])
    padded = [np.pad(v, ((0, 0), (0, max_len - v.shape[1])), mode) for v in data.values()]
    return np.hstack(padded)
