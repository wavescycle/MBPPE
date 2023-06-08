from http.client import BAD_REQUEST
from flask import Flask, request, send_file, jsonify, abort, make_response
from flask_restful import Resource, Api
from flask_cors import CORS
from marshmallow import ValidationError, EXCLUDE
from scipy.io import loadmat
from process import butter_filter, power_spectrum, de, time_frequence, frequence, ica
from customSchema import DataSchema, FilterSchema, BasicSchema
import numpy as np
import io
import load
import copy

app = Flask(__name__)
api = Api(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

RAW = dict()
RAW_FILTER = dict()
RAW_FREQ = dict()
FILETYPE = ""
ALLOWED_EXTENSIONS = {'mat', 'npz', 'xlsx'}


def transformData(RAW):
    return getattr(load, FILETYPE)(RAW)


def allowed_file(filename):
    global FILETYPE
    if '.' in filename:
        FILETYPE = filename.rsplit('.', 1)[1].lower()
    return FILETYPE in ALLOWED_EXTENSIONS


def streamData(data, aixs=True):
    if (aixs):
        xAixs = np.arange(0, data.shape[1])
        data = np.vstack([xAixs, data])
    bytestream = io.BytesIO()
    np.save(bytestream, data)
    bytestream.seek(0)
    return bytestream

class BaseParams():
    def __init__(self):
        if request.method == 'GET':
            params = request.args
        else:
            params = request.json
        try:
            params = BasicSchema(unknown=EXCLUDE).load(params)
            filename = self.filename
            self.channels = params['channels']
            self.start = params['start']
            self.end = params['end']
            if params['isFilter']:
                self.storage = RAW_FILTER[filename]
                self.source = RAW_FILTER[filename]['filter']
            else:
                self.storage = RAW[filename]
                self.source = RAW[filename]['raw']
        except ValidationError as e:
            abort(BAD_REQUEST, str(e.messages))


class Status(Resource):
    def get(self):
        return 'OK'


class FileList(Resource):
    def get(self):
        params = request.args
        try:
            params = BasicSchema(unknown=EXCLUDE).load(params)
        except ValidationError as e:
            abort(BAD_REQUEST, str(e.messages))
        self.chennels = params['channels']
        if params['isFilter']:
            data = RAW_FILTER.keys()
        else:
            data = RAW.keys()
        return jsonify(list(data))
        '''
        isProcess = params['isProcess']
        if isProcess:
            if params['isFilter']: return jsonify(list(RAW_FILTER.keys()))
            else: return jsonify(list(RAW.keys()))
        else:
            # Match global variables by string
            # e.g {"isHeatMap":True,"isPSD":False,"isFilter":True,"isDe":False} to RAW_FILTER_HEATMAP
            variabel_name = 'RAW'
            isFilter = ''
            method = ''
            for k, v in params.items():
                if v:
                    if k == 'isFilter': isFilter = '_FILTER'
                    else:
                        method = k.replace('is', '_').upper()
            variabel_name = variabel_name + isFilter + method
            return jsonify(list(globals()[variabel_name].keys()))
        '''


'''
      {
        Filename: "2016-05-03",
        SampleRate: "200Hz",
        Filter: "False",
      },
'''


class FileStatus(Resource):
    def get(self):
        fileStatus = list()
        for k in RAW.keys():
            fileStatus.append({
                'Filename': k,
                'SampleRate': RAW_FREQ[k],
                'Filter': k in RAW_FILTER.keys()
            })
        return jsonify(fileStatus)


class Data(Resource):
    def get(self, filename):
        data = request.args
        try:
            data = DataSchema(unknown=EXCLUDE).load(data, partial=False)
        except ValidationError as e:
            abort(BAD_REQUEST, str(e.messages))
        channels = data['channels']
        choosedData = RAW[filename]['raw'][channels]
        return send_file(streamData(choosedData, True),
                         mimetype="application/octet-stream")

    def post(self, filename):
        freq = request.form['freq']
        file = request.files['file']
        if file and allowed_file(filename):
            # read file use stream
            RAW[filename] = dict()
            RAW[filename]['raw'] = transformData(loadmat(file.stream))
            RAW_FREQ[filename] = int(freq)
            return 'CREATED', 201
        else:
            return 'Not support file', 400


class Filter(Resource):
    def _handle(self, filename):
        # pick data with channels
        raw = copy.deepcopy(RAW[filename]['raw'])
        # filter data
        cutoff = list(filter(lambda it: it is not None, [self.low, self.high]))
        if filename not in RAW_FILTER:
            RAW_FILTER[filename] = dict()
        freq = RAW_FREQ[filename]
        RAW_FILTER[filename]['filter'] = butter_filter(raw,
                                                       btype=self.method,
                                                       cutoff=cutoff,
                                                       fs=freq)
        return True

    def get(self, filename):
        params = request.args
        channels = params.getlist('channels', type=int)
        if filename in RAW_FILTER:
            data = RAW_FILTER[filename]['filter'][channels]
            return send_file(streamData(data),
                             mimetype="application/octet-stream")
        else:
            abort(BAD_REQUEST, 'You need do filter first')

    def post(self, filename):
        params = request.json
        try:
            params = FilterSchema(unknown=EXCLUDE).load(params)
            self.method = params['method']
            # self.channels = params['channels']
            self.low = params['low']
            self.high = params['high']
        except ValidationError as e:
            abort(BAD_REQUEST, str(e.messages))

        if self._handle(filename):
            return 'OK'
        else:
            return 'Bad request', 400


class ICA(Resource):
    def _handle(self):
        raw = self.source
        self.storage = ica(raw)

    def get(self, filename):
        self.filename = filename
        BaseParams.__init__(self)
        if 'ica' not in self.storage:
            self._handle()
        return send_file(streamData(self.storage['ica'], False),
                         mimetype="application/octet-stream")

    def post(self, filename):
        self.filename = filename
        BaseParams.__init__(self)
        self._handle()
        return 'OK'


class PSD(Resource):
    '''
    if request.method == 'GET':
        params = request.args
    else:
        params = request.json
    try:
        params = BasicSchema(unknown=EXCLUDE).load(params)
        self.filename = filename
        if params['isFilter']:
            self.storage = RAW_FILTER[filename]
            self.source = RAW_FILTER[filename]['filter']
        else:
            self.storage = RAW[filename]
            self.source = RAW[filename]['raw']
    except ValidationError as e:
        abort(BAD_REQUEST, str(e.messages))
    '''
    def _handle(self):
        raw = copy.deepcopy(self.source)
        freq = RAW_FREQ[self.filename]
        self.storage['psd'] = power_spectrum(raw, freq)

    def get(self, filename):
        self.filename = filename
        BaseParams.__init__(self)
        if 'psd' not in self.storage:
            self._handle()
        return send_file(streamData(self.storage['psd'], False),
                         mimetype="application/octet-stream")

    def post(self, filename):
        self.filename = filename
        BaseParams.__init__(self)
        self._handle()
        return 'OK'


class DE(Resource):
    def _handle(self):
        raw = copy.deepcopy(self.source)
        freq = RAW_FREQ[self.filename]
        self.storage['de'] = de(raw, fs=freq, win=freq)

    def get(self, filename):
        self.filename = filename
        BaseParams.__init__(self)
        if 'de' not in self.storage:
            self._handle()
        return send_file(streamData(self.storage['de'], False),
                         mimetype="application/octet-stream")

    def post(self, filename):
        self.filename = filename
        BaseParams.__init__(self)
        self._handle()
        return 'OK'


class Frequence(Resource):
    def _handle(self):
        raw = copy.deepcopy(self.source)
        freq = RAW_FREQ[self.filename]
        self.storage['frequence'] = frequence(raw,
                                              self.channels,
                                              self.start,
                                              self.end,
                                              fs=freq)

    def get(self, filename):
        self.filename = filename
        BaseParams.__init__(self)
        self._handle()

        return send_file(streamData(self.storage['frequence'], True),
                         mimetype="application/octet-stream")

    def post(self, filename):
        self.filename = filename
        BaseParams.__init__(self)
        self._handle()
        return 'OK'


class TimeFrequence(Resource):
    def _handle(self):
        raw = copy.deepcopy(self.source)
        freq = RAW_FREQ[self.filename]
        self.storage['timefrequence'], self.maxValue = time_frequence(
            raw, self.channels, self.start, self.end, fs=freq)

    def get(self, filename):
        self.filename = filename
        BaseParams.__init__(self)
        # if 'timefrequence' not in self.storage:
        self._handle()
        response = make_response(
            send_file(streamData(self.storage['timefrequence'], False),
                      mimetype="application/octet-stream"))
        response.headers['MaxValue'] = self.maxValue
        response.headers['Access-Control-Expose-Headers'] = 'MaxValue'
        return response

    def post(self, filename):
        self.filename = filename
        BaseParams.__init__(self)
        self._handle()
        return 'OK'


api.add_resource(Status, '/status')
api.add_resource(Data, '/data/<string:filename>')
api.add_resource(FileList, '/filelist')
api.add_resource(FileStatus, '/filestatus')
api.add_resource(Filter, '/filter/<string:filename>')
api.add_resource(ICA, '/ica/<string:filename>')
api.add_resource(PSD, '/psd/<string:filename>')
api.add_resource(DE, '/de/<string:filename>')
api.add_resource(Frequence, '/frequence/<string:filename>')
api.add_resource(TimeFrequence, '/timefrequence/<string:filename>')

'''
TODO: [x] filter pick channels
'''
if __name__ == '__main__':
    app.run()
