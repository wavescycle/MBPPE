from pyserver.common.decorator import init_channels, init_data
from pyserver.common.customSchema import BasicSchema
from pyserver.common.utils import stream_data, get_data
from flask import send_file, abort, make_response
from flask_restful import Resource
from .methods import frequency
import json
import copy


class Frequency(Resource):

    @init_data(BasicSchema, storage_path="Feature_Ext", storage_type='Freq')
    @init_channels('Freq')
    def get(self, **kwargs):
        """
        Get Differential Entropy Data
        """
        data, is_none = get_data(feature_ext="Freq", **kwargs)
        need_axis = kwargs['params']['need_axis']
        sample_rate = kwargs['info']['sample_rate']
        file_type = kwargs['params']['file_type']
        if need_axis and len(data.shape) > 2:
            data = data[0]

        if is_none:
            abort(400, 'You need do Frequency first')
        else:
            # Add user-defined band to response header for subsequent use
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
        """
        Frequency analysis of data
        """
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
