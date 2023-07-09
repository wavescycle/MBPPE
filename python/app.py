from http.client import BAD_REQUEST
from werkzeug.exceptions import HTTPException, InternalServerError
from flask import Flask, request, send_file, jsonify, abort, make_response, url_for, current_app
from flask_restful import Resource, Api
from flask_cors import CORS
from marshmallow import ValidationError, EXCLUDE, Schema
from scipy.io import loadmat
from process import butter_filter, power_spectrum, de, time_frequency, frequency, ica
from customSchema import DataSchema, FilterSchema, BasicSchema
from utils import get_data
from functools import wraps
from datetime import datetime
from utils import decode_async_task
import time
import numpy as np
import uuid
import threading
import io
import load
import copy
from enum import Enum

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
    Channels: {
    
    }
    'Info': {'sample_rate': 200}
}
'''
DATA_STORAGE_TEMPLATE = {
    'Pre_Process': {},
    'Feature_Ext': {},
    'Channels': {},
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
        def wrapper(*args, **kwargs):
            if request.method == 'GET':
                params = request.args
            else:
                params = request.json

            try:
                if schema != Schema:
                    params = schema(unknown=EXCLUDE).load(params)
            except ValidationError as e:
                abort(BAD_REQUEST, str(e.messages))
            filename = kwargs['filename']
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


def init_channels(method):
    def decorator(func):
        def wrapper(*args, **kwargs):
            params = kwargs['params']
            filename = kwargs['filename']
            channels = params.get("channels")
            channel_path = DATA_STORAGE[filename]['Channels']

            if request.method == 'POST' and channels is not None:
                storage_type = kwargs.get('modify_storage_type', 'Raw')
                channel_path.setdefault(storage_type, {})
                channel_path[storage_type][method] = channels

            elif request.method == 'GET' and channels is not None:
                pre_data = params.get('pre_data', 'Raw')
                target = method or pre_data

                try:
                    storage_channels = channel_path[pre_data][target]
                except KeyError:
                    storage_channels = channels

                try:
                    new_channels = [storage_channels.index(ch) for ch in channels]
                    params['channels'] = new_channels
                except ValueError as e:
                    abort(BAD_REQUEST, 'Includes unprocessed channels')

            return func(*args, **kwargs)

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


class FileTreeList(Resource):
    def get(self):
        file_trees = []
        # TEST = {
        #     'filename1': {
        #         'Pre_Process': {'Raw': 1, 'Filter': 1},
        #         'Feature_Ext': {
        #             'Raw': {'PSD': 1, 'DE': 1, 'Freq': 1, 'Time_Freq': 1},
        #             'Filter': {'PSD': 1, 'DE': 1, 'Freq': None, 'Time_Freq': None},
        #             'ICA': {'PSD': 1, 'DE': None, 'Freq': None, 'Time_Freq': None},
        #             'Filter_ICA': {'PSD': 1, 'DE': None, 'Freq': None, 'Time_Freq': None}
        #         },
        #         'Info': {'sample_rate': 204}
        #     },
        #     'filename2': {
        #         'Pre_Process': {'Raw': 1, 'Filter': 1},
        #         'Feature_Ext': {
        #             'Raw': {'PSD': 1, 'DE': 1, 'Freq': 1, 'Time_Freq': 1},
        #             'Filter': {'PSD': 1, 'DE': 1, 'Freq': None, 'Time_Freq': None},
        #             'ICA': {'PSD': 1, 'DE': None, 'Freq': None, 'Time_Freq': None},
        #             'Filter_ICA': {'PSD': 1, 'DE': None, 'Freq': None, 'Time_Freq': None}
        #         },
        #         'Info': {'sample_rate': 204}
        #     },
        #     'filename3': {
        #         'Pre_Process': {'Raw': 1, 'Filter': 1},
        #         'Feature_Ext': {
        #             'Raw': {'PSD': 1, 'DE': 1, 'Freq': 1, 'Time_Freq': 1},
        #             'Filter': {'PSD': 1, 'DE': 1, 'Freq': None, 'Time_Freq': None},
        #             'ICA': {'PSD': 1, 'DE': None, 'Freq': None, 'Time_Freq': None},
        #             'Filter_ICA': {'PSD': 1, 'DE': None, 'Freq': None, 'Time_Freq': None}
        #         },
        #         'Info': {'sample_rate': 204}
        #     }
        # }
        for k, v in DATA_STORAGE.items():
            temp = {
                'filename': k,
                'sample_rate': v['Info']['sample_rate'],
                'data_type':
                    {'Pre_Process': list(v['Pre_Process'].keys())}
            }
            new_dict = {}
            for outer_key, inner_dict in v['Feature_Ext'].items():
                for inner_key, value in inner_dict.items():
                    if value is not None:  # Ignore None values
                        new_dict.setdefault(inner_key, []).append(outer_key)

            temp['data_type']['Feature_Ext'] = new_dict
            file_trees.append(temp)
        return jsonify(file_trees)


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
    @init_channels(None)
    def get(self, **kwargs):
        data, is_none = get_data(**kwargs)
        need_axis = kwargs['params']['need_axis']

        return send_file(stream_data(data, need_axis), mimetype="application/octet-stream")

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

    def delete(self, filename):
        del DATA_STORAGE[filename]
        return 'Ok'


class Filter(Resource):
    @init_data(FilterSchema, storage_type='Filter')
    @init_channels('Filter')
    def get(self, **kwargs):
        data, is_none = get_data(**kwargs)
        need_axis = kwargs['params']['need_axis']

        if is_none:
            abort(BAD_REQUEST, 'You need do filter first')
        else:
            return send_file(stream_data(data, need_axis), mimetype="application/octet-stream")

    @init_data(FilterSchema, storage_type='Filter')
    @init_channels('Filter')
    def post(self, **kwargs):
        source = kwargs['source']
        storage = kwargs['storage']
        info = kwargs['info']
        params = kwargs['params']
        storage_type = kwargs['modify_storage_type']

        method = params['method']

        raw = copy.deepcopy(source)
        # filter data
        storage[storage_type] = butter_filter(raw, btype=method, low=params['low'], high=params['high'],
                                              fs=info['sample_rate'])
        return 'OK'


class ICA(Resource):

    @init_data(BasicSchema, storage_type='ICA')
    def get(self, **kwargs):
        data, is_none = get_data(**kwargs)
        need_axis = kwargs['params']['need_axis']

        if is_none:
            abort(BAD_REQUEST, 'You need do ICA first')
        else:
            return send_file(stream_data(data, need_axis), mimetype="application/octet-stream")

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
        need_axis = kwargs['params']['need_axis']

        if is_none:
            abort(BAD_REQUEST, 'You need do PSD first')
        else:
            return send_file(stream_data(data, need_axis), mimetype="application/octet-stream")

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
        need_axis = kwargs['params']['need_axis']

        if is_none:
            abort(BAD_REQUEST, 'You need do DE first')
        else:
            return send_file(stream_data(data, need_axis), mimetype="application/octet-stream")

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


class Frequency(Resource):

    @init_data(BasicSchema, storage_path="Feature_Ext", storage_type='Freq')
    @init_channels('Freq')
    def get(self, **kwargs):
        data, is_none = get_data(feature_ext="Freq", **kwargs)
        need_axis = kwargs['params']['need_axis']

        if need_axis and len(data.shape) > 2:
            data = data[0]

        if is_none:
            abort(BAD_REQUEST, 'You need do Frequency first')
        else:
            return send_file(stream_data(data, need_axis), mimetype="application/octet-stream")

    @init_data(BasicSchema, storage_path="Feature_Ext", storage_type='Freq')
    @init_channels('Freq')
    def post(self, **kwargs):
        source = kwargs['source']
        storage = kwargs['storage']
        info = kwargs['info']
        params = kwargs['params']
        storage_type = kwargs['modify_storage_type']

        channels = params['channels']
        raw = copy.deepcopy(source)
        freq = info['sample_rate']
        storage[storage_type]['Freq'] = frequency(raw, channels, fs=freq)
        return 'OK'


class TimeFrequency(Resource):

    @init_data(BasicSchema, storage_path="Feature_Ext", storage_type='Time_Freq')
    @init_channels('Time_Freq')
    def get(self, **kwargs):
        data, is_none = get_data(feature_ext="Time_Freq", **kwargs)
        info = kwargs['info']
        params = kwargs['params']
        need_axis = params['need_axis']
        start = params['start']
        end = params['end']
        fs = info['sample_rate']

        if is_none:
            abort(BAD_REQUEST, 'You need do Time_Freq first')

        # Visualisation
        if start is not None or end is not None:
            cwt_scales = 20
            scale = fs * cwt_scales
            data_fragment = data[0][start * scale:end * scale]
            max_value = np.max(data_fragment[:, 2])
        else:
            data_fragment = data
            max_value = None

        response = make_response(send_file(stream_data(data_fragment, need_axis), mimetype="application/octet-stream"))

        if max_value is not None:
            response.headers['MaxValue'] = max_value
            response.headers['Access-Control-Expose-Headers'] = 'MaxValue'
        return response

    @init_data(BasicSchema, storage_path="Feature_Ext", storage_type='Time_Freq')
    @init_channels('Time_Freq')
    def post(self, **kwargs):
        source = kwargs['source']
        storage = kwargs['storage']
        info = kwargs['info']
        params = kwargs['params']
        storage_type = kwargs['modify_storage_type']

        channels = params['channels']
        raw = copy.deepcopy(source)
        freq = info['sample_rate']
        storage[storage_type]['Time_Freq'] = time_frequency(raw, channels, fs=freq)
        return 'OK'


TASKS = {}


def async_api(wrapped_function):
    @wraps(wrapped_function)
    def new_function(*args, **kwargs):
        def task_call(flask_app, environ):
            # Create a request context similar to that of the original request
            # so that the task can have access to flask.g, flask.request, etc.
            with flask_app.request_context(environ):
                # try:
                wrapped_function(*args, **kwargs)

                # tasks[task_id]['return_value'] = wrapped_function(*args, **kwargs)
                # except HTTPException as e:
                #     tasks[task_id]['return_value'] = current_app.handle_http_exception(e)
                # except Exception as e:
                #     # The function raised an exception, so we set a 500 error
                #     tasks[task_id]['return_value'] = InternalServerError()
                #     if current_app.debug:
                #         # We want to find out if something happened so reraise
                #         raise
                # finally:
                #     # We record the time of the response, to help in garbage
                #     # collecting old tasks
                #     tasks[task_id]['completion_timestamp'] = datetime.timestamp(datetime.utcnow())
                #
                #     # close the database session (if any)

        # Assign an id to the asynchronous task
        # task_id = uuid.uuid4().hex
        # task_id = '408a43a133ba420c9d4b3e9b6bf090e9'
        # Record the task, and then launch it
        t = threading.Thread(target=task_call, args=(current_app._get_current_object(),
                                                     request.environ))
        t.start()

        # Return a 202 response, with a link that the client can use to
        # obtain task status
        return 'accepted', 202

    return new_function


class Task(Resource):
    def get(self, task_id=None, filename=None):
        """
        Return status about an asynchronous task. If this request returns a 202
        status code, it means that task hasn't finished yet. Else, the response
        from the task is returned.
        """
        """
        task  get all task status
        task/task_id get special task status
        task/task_id/filename get task data
        """
        if task_id is None:
            return jsonify(
                [{'task_id': t_id, **{key: value for key, value in t_value.items() if key != 'data'}} for t_id, t_value
                 in TASKS.items()])

        task = TASKS.get(task_id)
        if task is None:
            abort(BAD_REQUEST)

        if filename is None:
            return jsonify({key: value for key, value in task.items() if key != 'data'})

        return send_file(stream_data(task['data'][filename], False), mimetype="application/octet-stream")

    @async_api
    def post(self):
        # perform some intensive processing
        task_id = uuid.uuid4().hex
        # task_id = '187acda6aa0447739a37ae74f63dfc4a'
        body = request.json
        TASKS[task_id] = {}

        decode_async_task(TASKS[task_id], body, DATA_STORAGE)
        return True

    def delete(self, task_id):
        del TASKS[task_id]
        return 'Ok'


@app.after_request
def after_request_func(response):
    # url = request.url
    # method = request.method
    # white_list = ['data', 'filter', 'ica', 'psd', 'de', 'frequency', 'timefrequency']
    #
    # if request.method == 'GET' or request.method == 'POST':
    #     print(DATA_STORAGE['4_20140621.mat']['Channels'])
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
api.add_resource(Frequency, '/frequency/<string:filename>')
api.add_resource(TimeFrequency, '/timefrequency/<string:filename>')
api.add_resource(Task, '/task', '/task/<string:task_id>', '/task/<string:task_id>/<string:filename>')
api.add_resource(FileTreeList, '/filetreelist')

if __name__ == '__main__':
    app.debug = True
    app.run()
