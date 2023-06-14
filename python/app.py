from http.client import BAD_REQUEST
from flask import Flask, request, send_file, jsonify, abort, make_response
from flask_restful import Resource, Api
from flask_cors import CORS
from marshmallow import ValidationError, EXCLUDE, Schema
from scipy.io import loadmat
from process import butter_filter, power_spectrum, de, time_frequence, frequence, ica
from customSchema import DataSchema, FilterSchema, BasicSchema
from utils import get_data
import numpy as np
import io
import load
import copy

app = Flask(__name__)
api = Api(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
'''
 {
    'Pre_Process': {'Raw': None, 'Filter': None, 'ICA': None, 'Filter_ICA': None},
    'Feature_Ext': {
        'Raw': {'PSD': None, 'DE': None, 'Freq': None, 'Time_Freq': None},
        'Filter': {'PSD': None, 'DE': None, 'Freq': None, 'Time_Freq': None},
        'ICA': {'PSD': None, 'DE': None, 'Freq': None, 'Time_Freq': None},
        'Filter_ICA': {'PSD': None, 'DE': None, 'Freq': None, 'Time_Freq': None}
    },
    'Info': {'sample_rate': 200}
}
'''
DATA_STORAGE_TEMPLATE = {
    'Pre_Process': {},
    'Feature_Ext': {},
    'Info': {'sample_rate': 200}
}
DATA_STORAGE = dict()
ALLOWED_EXTENSIONS = {'mat', 'npz', 'xlsx'}


def transform_data(raw, file_type):
    return getattr(load, file_type)(raw)


def allowed_file(filename):
    if '.' in filename:
        file_type = filename.rsplit('.', 1)[1].lower()
        return file_type in ALLOWED_EXTENSIONS, file_type
    else:
        return False, None


def stream_data(data, axis=True):
    if axis:
        xAxis = np.arange(0, data.shape[1])
        data = np.vstack([xAxis, data])
    bytestream = io.BytesIO()
    np.save(bytestream, data)
    bytestream.seek(0)
    return bytestream


def init_data(schema=Schema, storage_type="Raw", storage_path='Pre_Process', source_path='Pre_Process'):
    def decorator(fuc):
        def wrapper(*args, filename):
            if request.method == 'GET':
                params = request.args
            else:
                params = request.json

            try:
                if schema != Schema:
                    params = schema(unknown=EXCLUDE).load(params)
            except ValidationError as e:
                abort(BAD_REQUEST, str(e.messages))

            DATA_STORAGE.setdefault(filename, copy.deepcopy(DATA_STORAGE_TEMPLATE))

            if params:
                pre_data = params.get('pre_data', 'Raw')
            else:
                pre_data = 'Raw'

            info = DATA_STORAGE[filename]['Info']
            storage = DATA_STORAGE[filename][storage_path]
            source = DATA_STORAGE[filename][source_path]

            modify_source_type = modify_storage_type = pre_data

            if request.method == 'POST' and storage_path == 'Pre_Process':
                modify_storage_type = f"{pre_data}_{storage_type}" if pre_data != 'Raw' else storage_type

            if storage_path == 'Feature_Ext':
                # modify_storage_type = pre_data
                storage.setdefault(modify_storage_type, {})
                storage[modify_storage_type].setdefault(storage_type, None)
            else:
                # modify_storage_type = f"{pre_data}_{storage_type}" if pre_data != 'Raw' else storage_type
                storage.setdefault(modify_storage_type, None)

            source.setdefault(modify_source_type, None)

            return fuc(*args, filename=filename, info=info, storage=storage, modify_storage_type=modify_storage_type,
                       source=source[modify_source_type],
                       params=params)

        return wrapper

    return decorator


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


class Status(Resource):
    def get(self):
        return 'OK'


class FileList(Resource):
    def get(self):
        params = request.args
        try:
            BasicSchema(unknown=EXCLUDE).load(params)
        except ValidationError as e:
            abort(BAD_REQUEST, str(e.messages))

        data = DATA_STORAGE.keys()
        return jsonify(list(data))


class FileStatus(Resource):
    def get(self):
        file_status = list()
        for k in DATA_STORAGE.keys():
            file_status.append({
                'Filename': k
            })
        return jsonify(file_status)


class Data(Resource):

    @init_data(DataSchema)
    def get(self, **kwargs):
        data, is_none = get_data(**kwargs)

        print(data)

        return send_file(stream_data(data, True), mimetype="application/octet-stream")

    @init_data()
    def post(self, **kwargs):
        freq = request.form['freq']
        file = request.files['file']
        filename = kwargs['filename']
        storage = kwargs['storage']
        storage_type = kwargs['modify_storage_type']
        info = kwargs['info']
        is_allowed, file_type = allowed_file(filename)
        if file and is_allowed:
            # read file use stream
            storage[storage_type] = transform_data(loadmat(file.stream), file_type)
            info['sample_rate'] = int(freq)
            return 'CREATED', 201
        else:
            return 'Not support file', 400


class Filter(Resource):
    @init_data(FilterSchema, storage_type='Filter')
    def get(self, **kwargs):
        data, is_none = get_data(**kwargs)

        if is_none:
            abort(BAD_REQUEST, 'You need do filter first')
        else:
            return send_file(stream_data(data), mimetype="application/octet-stream")

    @init_data(FilterSchema, storage_type='Filter')
    def post(self, **kwargs):
        source = kwargs['source']
        storage = kwargs['storage']
        info = kwargs['info']
        params = kwargs['params']
        storage_type = kwargs['modify_storage_type']

        print(storage_type)

        method = params['method']
        low = params['low']
        high = params['high']

        raw = copy.deepcopy(source)
        # filter data
        cutoff = list(filter(lambda it: it is not None, [low, high]))
        storage[storage_type] = butter_filter(raw, btype=method, cutoff=cutoff, fs=info['sample_rate'])

        return 'OK'


class ICA(Resource):

    @init_data(BasicSchema, storage_type='ICA')
    def get(self, **kwargs):
        data, is_none = get_data(**kwargs)

        if is_none:
            abort(BAD_REQUEST, 'You need do ICA first')
        else:
            return send_file(stream_data(data, False), mimetype="application/octet-stream")

    @init_data(BasicSchema, storage_type='ICA')
    def post(self, **kwargs):
        source = kwargs['source']
        storage = kwargs['storage']
        storage_type = kwargs['modify_storage_type']
        storage[storage_type] = ica(copy.deepcopy(source))
        return 'OK'


class PSD(Resource):

    @init_data(BasicSchema, storage_path="Feature_Ext", storage_type='PSD')
    def get(self, **kwargs):
        data, is_none = get_data(feature_ext="PSD", **kwargs)

        if is_none:
            abort(BAD_REQUEST, 'You need do PSD first')
        else:
            return send_file(stream_data(data, False), mimetype="application/octet-stream")

    @init_data(BasicSchema, storage_path="Feature_Ext", storage_type='PSD')
    def post(self, **kwargs):
        source = kwargs['source']
        storage = kwargs['storage']
        info = kwargs['info']
        storage_type = kwargs['modify_storage_type']

        raw = copy.deepcopy(source)
        freq = info['sample_rate']
        storage[storage_type]['PSD'] = power_spectrum(raw, freq)
        return 'OK'


class DE(Resource):

    @init_data(BasicSchema, storage_path="Feature_Ext", storage_type='DE')
    def get(self, **kwargs):
        data, is_none = get_data(feature_ext="DE", **kwargs)

        if is_none:
            abort(BAD_REQUEST, 'You need do DE first')
        else:
            return send_file(stream_data(data, False), mimetype="application/octet-stream")

    @init_data(BasicSchema, storage_path="Feature_Ext", storage_type='DE')
    def post(self, **kwargs):
        source = kwargs['source']
        storage = kwargs['storage']
        info = kwargs['info']
        storage_type = kwargs['modify_storage_type']

        raw = copy.deepcopy(source)
        freq = info['sample_rate']
        storage[storage_type]['DE'] = de(raw, fs=freq, win=freq)
        return 'OK'


class Frequence(Resource):

    @init_data(BasicSchema, storage_path="Feature_Ext", storage_type='Freq')
    def get(self, **kwargs):
        data, is_none = get_data(feature_ext="Freq", **kwargs)

        if is_none:
            abort(BAD_REQUEST, 'You need do Frequence first')
        else:
            return send_file(stream_data(data, True), mimetype="application/octet-stream")

    @init_data(BasicSchema, storage_path="Feature_Ext", storage_type='Freq')
    def post(self, **kwargs):
        source = kwargs['source']
        storage = kwargs['storage']
        info = kwargs['info']
        params = kwargs['params']
        storage_type = kwargs['modify_storage_type']

        channels = params['channels']
        start = params['start']
        end = params['end']

        raw = copy.deepcopy(source)
        freq = info['sample_rate']
        storage[storage_type]['Freq'] = frequence(raw, channels, start, end, fs=freq)
        return 'OK'


class TimeFrequence(Resource):

    @init_data(BasicSchema, storage_path="Feature_Ext", storage_type='Time_Freq')
    def get(self, **kwargs):
        data, is_none = get_data(feature_ext="Time_Freq", **kwargs)
        info = kwargs['info']

        if is_none:
            abort(BAD_REQUEST, 'You need do Time_Freq first')

        response = make_response(
            send_file(stream_data(data, False), mimetype="application/octet-stream"))
        response.headers['MaxValue'] = info['maxValue']
        response.headers['Access-Control-Expose-Headers'] = 'MaxValue'
        return response

    @init_data(BasicSchema, storage_path="Feature_Ext", storage_type='Time_Freq')
    def post(self, **kwargs):
        source = kwargs['source']
        storage = kwargs['storage']
        info = kwargs['info']
        params = kwargs['params']
        storage_type = kwargs['modify_storage_type']

        channels = params['channels']
        start = params['start']
        end = params['end']

        raw = copy.deepcopy(source)
        freq = info['sample_rate']
        storage[storage_type]['Time_Freq'], info['maxValue'] = time_frequence(raw, channels, start, end, fs=freq)
        return 'OK'


@app.after_request
def after_request_func(response):
    # url = request.url
    # method = request.method
    # white_list = ['data', 'filter', 'ica', 'psd', 'de', 'frequence', 'timefrequence']
    #
    # if method == 'GET' or method == 'POST':
    #     for word in white_list:
    #         if word in url:
    #             print(DATA_STORAGE)

    return response


api.add_resource(Status, '/status')
api.add_resource(PreData, '/predata/<string:filename>')
api.add_resource(Data, '/data/<string:filename>')
api.add_resource(FileList, '/filelist')
api.add_resource(FileStatus, '/filestatus')
api.add_resource(Filter, '/filter/<string:filename>')
api.add_resource(ICA, '/ica/<string:filename>')
api.add_resource(PSD, '/psd/<string:filename>')
api.add_resource(DE, '/de/<string:filename>')
api.add_resource(Frequence, '/frequence/<string:filename>')
api.add_resource(TimeFrequence, '/timefrequence/<string:filename>')

if __name__ == '__main__':
    app.debug = True
    app.run()
