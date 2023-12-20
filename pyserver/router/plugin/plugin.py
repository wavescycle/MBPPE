from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from pyserver.common.decorator import init_data, init_channels
from pyserver.common.customSchema import PluginSchema
from .manager import PM
import os
import base64
import sys
import importlib
import copy


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
            if not os.path.exists('./pluginstorage'):
                os.makedirs('./pluginstorage')
            file.save(os.path.join('./pluginstorage', filename))
            sys.path.insert(0, './pluginstorage')
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
            abort(400, 'Error Plugin Type')
        return 200
