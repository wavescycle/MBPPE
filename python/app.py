import json
from scipy.io import savemat
from http.client import BAD_REQUEST
from werkzeug.exceptions import HTTPException, InternalServerError
from flask import Flask, request, send_file, jsonify, abort, make_response, url_for, current_app
from flask_restful import Resource, Api
from flask_cors import CORS
from marshmallow import ValidationError, EXCLUDE, Schema
from process import fir_filter, power_spectrum, de, time_frequency, frequency, ica, re_reference, resample
from customSchema import DataSchema, FilterSchema, BasicSchema, RefSchema, SampleSchema, PluginSchema
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
import os
import sys
from plugin import PM
import importlib
from enum import Enum
import urllib.parse
import base64

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
TASKS = {}
COMMENTS = {}


def transform_data(raw, file_type, format_mode):
    return getattr(load, file_type)(raw, format_mode)


def allowed_file(filename):
    if '.' in filename:
        file_type = filename.rsplit('.', 1)[1].lower()
        return file_type in ALLOWED_EXTENSIONS, file_type
    else:
        return False, None


def stream_data(data, axis=True, unit=1, file_type="npy"):
    if axis:
        xAxis = np.arange(0, data.shape[1]) / unit
        data = np.vstack([xAxis, data])
    bytestream = io.BytesIO()
    if file_type == 'mat':
        data = {'DATA': data}
        savemat(bytestream, data)
    else:
        np.save(bytestream, data)
    bytestream.seek(0)
    return bytestream


def init_data(schema=Schema, storage_type="Raw", storage_path='Pre_Process', source_path='Pre_Process'):
    def decorator(fuc):
        def wrapper(*args, **kwargs):
            temp_storage_type = storage_type
            temp_storage_path = storage_path
            temp_source_path = source_path
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
                print(params)
                pre_data = params.get('pre_data', 'Raw')
                temp_storage_path = params.get('storage_path', storage_path)
            else:
                pre_data = 'Raw'

            info = DATA_STORAGE[filename]['Info']
            print(temp_storage_path)
            storage = DATA_STORAGE[filename][temp_storage_path]
            source = DATA_STORAGE[filename][temp_source_path]

            if temp_storage_type == 'Plugin':
                temp_storage_path = params['plugin_type']
                temp_storage_type = kwargs['plugin']
                if params['plugin_type'] != 'Visualization':
                    storage = DATA_STORAGE[filename][temp_storage_path]

            modify_source_type = modify_storage_type = pre_data

            if request.method == 'POST' and temp_storage_path == 'Pre_Process':
                modify_storage_type = f"{pre_data}_{temp_storage_type}" if pre_data != 'Raw' else temp_storage_type

            if temp_storage_path == 'Feature_Ext':
                # modify_storage_type = pre_data
                storage.setdefault(modify_storage_type, {})
                storage[modify_storage_type].setdefault(temp_storage_type, None)
            else:
                # modify_storage_type = f"{pre_data}_{storage_type}" if pre_data != 'Raw' else storage_type
                storage.setdefault(modify_storage_type, None)

            source.setdefault(modify_source_type, None)

            return fuc(*args, info=info, storage=storage, modify_storage_type=modify_storage_type,
                       source=source[modify_source_type],
                       params=params, **kwargs)

        return wrapper

    return decorator


def init_channels(method):
    def decorator(func):
        def wrapper(*args, **kwargs):
            nonlocal method
            params = kwargs['params']
            filename = kwargs['filename']
            channels = params.get("channels")
            channel_path = DATA_STORAGE[filename]['Channels']
            if method == 'Plugin':
                method = kwargs['plugin']

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


class Reference(Resource):
    @init_data(RefSchema, storage_type='Ref')
    @init_channels('Ref')
    def get(self, **kwargs):
        data, is_none = get_data(**kwargs)
        need_axis = kwargs['params']['need_axis']
        sample_rate = kwargs['info']['sample_rate']
        file_type = kwargs['params']['file_type']
        return send_file(stream_data(data, need_axis, sample_rate, file_type=file_type),
                         mimetype="application/octet-stream")

    @init_data(RefSchema, storage_type='Ref')
    @init_channels('Ref')
    def post(self, **kwargs):
        source = kwargs['source']
        storage = kwargs['storage']
        params = kwargs['params']
        storage_type = kwargs['modify_storage_type']
        channels = kwargs['channels']

        raw = copy.deepcopy(source)
        storage[storage_type] = re_reference(raw[channels], mode=params['mode'], channel=params['ref_ch'])


class Resample(Resource):
    @init_data(SampleSchema, storage_type='Sample')
    @init_channels('Sample')
    def get(self, **kwargs):
        data, is_none = get_data(**kwargs)
        need_axis = kwargs['params']['need_axis']
        sample_rate = kwargs['info']['sample_rate']
        file_type = kwargs['params']['file_type']

        return send_file(stream_data(data, need_axis, sample_rate, file_type=file_type),
                         mimetype="application/octet-stream")

    @init_data(SampleSchema, storage_type='Sample')
    @init_channels('Sample')
    def post(self, **kwargs):
        source = kwargs['source']
        storage = kwargs['storage']
        info = kwargs['info']
        params = kwargs['params']
        storage_type = kwargs['modify_storage_type']

        raw = copy.deepcopy(source)
        # filter data
        storage[storage_type] = resample(raw, fs=info['sample_rate'], new_fs=params['new_fs'])
        return 'OK'


class Filter(Resource):
    @init_data(FilterSchema, storage_type='Filter')
    @init_channels('Filter')
    def get(self, **kwargs):
        data, is_none = get_data(**kwargs)
        need_axis = kwargs['params']['need_axis']
        sample_rate = kwargs['info']['sample_rate']
        file_type = kwargs['params']['file_type']
        if is_none:
            abort(BAD_REQUEST, 'You need do filter first')
        else:
            return send_file(stream_data(data, need_axis, sample_rate, file_type=file_type),
                             mimetype="application/octet-stream")

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
        channels = kwargs['channels']
        # filter data
        storage[storage_type] = fir_filter(raw[channels], btype=method, low=params['low'], high=params['high'],
                                           fs=info['sample_rate'])
        return 'OK'


class ICA(Resource):

    @init_data(BasicSchema, storage_type='ICA')
    def get(self, **kwargs):
        data, is_none = get_data(**kwargs)
        need_axis = kwargs['params']['need_axis']
        sample_rate = kwargs['info']['sample_rate']
        file_type = kwargs['params']['file_type']
        if is_none:
            abort(BAD_REQUEST, 'You need do ICA first')
        else:
            return send_file(stream_data(data, need_axis, sample_rate, file_type=file_type),
                             mimetype="application/octet-stream")

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
        file_type = kwargs['params']['file_type']
        if is_none:
            abort(BAD_REQUEST, 'You need do PSD first')
        else:
            return send_file(stream_data(data, False, file_type=file_type), mimetype="application/octet-stream")

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
        sample_rate = kwargs['info']['sample_rate']
        file_type = kwargs['params']['file_type']
        if is_none:
            abort(BAD_REQUEST, 'You need do DE first')
        else:
            return send_file(stream_data(data, need_axis, sample_rate, file_type=file_type),
                             mimetype="application/octet-stream")

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
        sample_rate = kwargs['info']['sample_rate']
        file_type = kwargs['params']['file_type']
        if need_axis and len(data.shape) > 2:
            data = data[0]

        if is_none:
            abort(BAD_REQUEST, 'You need do Frequency first')
        else:
            band_list = kwargs['info']['band_list']

            response = make_response(
                send_file(stream_data(data, need_axis, sample_rate, file_type=file_type),
                          mimetype="application/octet-stream"))
            response.headers['BandList'] = json.dumps(band_list)
            response.headers['Access-Control-Expose-Headers'] = 'BandList'
            return response

    @init_data(BasicSchema, storage_path="Feature_Ext", storage_type='Freq')
    @init_channels('Freq')
    def post(self, **kwargs):
        source = kwargs['source']
        storage = kwargs['storage']
        info = kwargs['info']
        params = kwargs['params']
        storage_type = kwargs['modify_storage_type']

        channels = params['channels']
        band_list = params['band_list']
        raw = copy.deepcopy(source)
        freq = info['sample_rate']
        if band_list is None:
            info['band_list'] = ['Delta', 'Theta', 'Alpha', 'Beta', 'Gamma']
        else:
            info['band_list'] = [item['name'] for item in json.loads(band_list.replace('\'', "\""))]
        storage[storage_type]['Freq'] = frequency(raw, channels, fs=freq, iter_freq=band_list)
        return 'OK'


class TimeFrequency(Resource):

    @init_data(BasicSchema, storage_path="Feature_Ext", storage_type='Time_Freq')
    @init_channels('Time_Freq')
    def get(self, **kwargs):
        data, is_none = get_data(feature_ext="Time_Freq", **kwargs)
        info = kwargs['info']
        params = kwargs['params']
        need_axis = params['need_axis']
        file_type = params['file_type']
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

        response = make_response(
            send_file(stream_data(data_fragment, need_axis, fs, file_type=file_type),
                      mimetype="application/octet-stream"))

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

        file_type = request.args.get("file_type")
        return send_file(stream_data(task['data'][filename], False, file_type=file_type),
                         mimetype="application/octet-stream")

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


class Plugin(Resource):
    def get(self):
        plugins = PM.list_plugin()
        return jsonify(list(plugins))

    def post(self):
        if 'file' not in request.files:
            return 'No file'
        file = request.files['file']
        if file:
            filename = file.filename
            basename, extension = os.path.splitext(filename)
            file.save(os.path.join('./plugins', filename))
            sys.path.insert(0, './plugins')
            module = importlib.import_module(basename)
            PM.register(basename, module)
        return str(PM.list_plugin())

    def delete(self, plugin):
        PM.del_plugin(plugin)
        return 'ok'


class PluginHandler(Resource):
    def get(self, plugin):
        pass

    @init_data(PluginSchema, 'Plugin')
    @init_channels('Plugin')
    def post(self, **kwargs):
        info = kwargs['info']
        source = kwargs['source']
        storage = kwargs['storage']
        storage_type = kwargs['modify_storage_type']
        params = kwargs['params']
        plugin_type = params['plugin_type']
        plugin_params = params['plugin_params']
        plugin_name = kwargs['plugin']
        channels = params['channels']

        raw = copy.deepcopy(source)
        plugin = PM.get_plugin(plugin_name)

        if plugin_type == 'Pre_Process':
            storage[storage_type] = plugin.process(raw[channels], plugin_params, info)
        elif plugin_type == 'Feature_Ext':
            storage[storage_type][plugin_name] = plugin.extract(raw[channels], plugin_params, info)
        elif plugin_type == 'Visualization':
            plt = plugin.visualization(raw[channels], plugin_params, info=None)
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            # Create a data URI
            datauri = 'data:image/png;base64,' + base64.b64encode(buf.read()).decode()
            buf.close()
            return {'data': datauri}
        else:
            abort(BAD_REQUEST, 'Error Plugin Type')
        return 200


class Comments(Resource):
    def get(self, pipeline_id):
        return COMMENTS.get(pipeline_id, [])

    def post(self, pipeline_id):
        params = request.json
        COMMENTS.setdefault(pipeline_id, [])
        COMMENTS[pipeline_id].append(params['data'])
        return COMMENTS[pipeline_id], 201


@app.after_request
def after_request_func(response):
    # url = request.url
    # method = request.method
    # white_list = ['data', 'filter', 'ica', 'psd', 'de', 'frequency', 'timefrequency']
    #
    # if request.method == 'GET' or request.method == 'POST':
    #     print(DATA_STORAGE)
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
api.add_resource(Reference, '/reference/<string:filename>')
api.add_resource(Resample, '/resample/<string:filename>')
api.add_resource(Plugin, '/plugin', '/plugin/<string:plugin>')
api.add_resource(PluginHandler, '/pluginhandler/<string:plugin>/<string:filename>')
api.add_resource(Comments, '/comments/<string:pipeline_id>')

if __name__ == '__main__':
    # app.debug = True
    app.run()
