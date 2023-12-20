from flask import Flask
from flask_restful import Resource, Api
from flask_cors import CORS
from pyserver.router.common import Data, PreData, Comments, FileList, FileStatus, FileTreeList
from pyserver.router.preprocess import Filter, ICA, Resample, Reference
from pyserver.router.fearure import PSD, DE, Frequency, TimeFrequency
from pyserver.router.plugin import Plugin, PluginHandler
from pyserver.router.pipline import Task

app = Flask(__name__)
api = Api(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

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
    app.debug = True
    app.run()
