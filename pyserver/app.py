"""
This file is used to accept requests and assign routes
"""
# Import flask and cors
from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS

# Import router modules
from pyserver.router.common import Data, PreData, Comments, FileList, FileTreeList
from pyserver.router.preprocess import Filter, ICA, Resample, Reference
from pyserver.router.fearure import PSD, DE, Frequency, TimeFrequency
from pyserver.router.plugin import Plugin, PluginHandler
from pyserver.router.pipline import Task
# import auth
from pyserver.common.utils import auth

app = Flask(__name__)
api = Api(app)

# Enable CORS
cors = CORS(app, resources={r"/*": {"origins": "*"}})


@app.before_request
def before_request_func():
    # Authenticate the request
    api_key = request.headers.get('api-key')
    req_path = request.path
    req_method = request.method
    return auth(req_path, req_method, api_key)


# Data Methods
# Get data types that have been processed
api.add_resource(PreData, '/predata/<string:filename>')
# For uploading and fetching data
api.add_resource(Data, '/data/<string:filename>')

# File Methods
# Get a list containing the names of all files that have been uploaded
api.add_resource(FileList, '/filelist')
# Get more detailed information about the file, including its name and the corresponding processing method
api.add_resource(FileTreeList, '/filetreelist')

# Build-in Methods
# Filtering/Independent Component Analysis/Reference/Resample/
# Power Spectral Density/Differential Entropy/Frequency/Time-Frequency data by file name
api.add_resource(Filter, '/filter/<string:filename>')
api.add_resource(ICA, '/ica/<string:filename>')
api.add_resource(Reference, '/reference/<string:filename>')
api.add_resource(Resample, '/resample/<string:filename>')
api.add_resource(PSD, '/psd/<string:filename>')
api.add_resource(DE, '/de/<string:filename>')
api.add_resource(Frequency, '/frequency/<string:filename>')
api.add_resource(TimeFrequency, '/timefrequency/<string:filename>')

# pipeline
# Get the pipeline task list, task details, and data processed by the pipeline
api.add_resource(Task, '/task', '/task/<string:task_id>', '/task/<string:task_id>/<string:filename>')

# Plugin
# Get and submit plugins
api.add_resource(Plugin, '/plugin', '/plugin/<string:plugin>')
# Processing data with plugins
api.add_resource(PluginHandler, '/pluginhandler/<string:plugin>/<string:filename>')

# Comments
api.add_resource(Comments, '/comments/<string:pipeline_id>')

if __name__ == '__main__':
    app.debug = True
    app.run()
