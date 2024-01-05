from pyserver.common.decorator import init_channels, init_data
from pyserver.common.customSchema import BasicSchema
from pyserver.common.utils import stream_data, get_data
from flask import send_file, abort, make_response
from flask_restful import Resource
from .methods import time_frequency
import numpy as np
import copy


class TimeFrequency(Resource):

    @init_data(BasicSchema, storage_path="Feature_Ext", storage_type='Time_Freq')
    @init_channels('Time_Freq')
    def get(self, **kwargs):
        """
        Get TimeFrequency Data
        """
        data, is_none = get_data(feature_ext="Time_Freq", **kwargs)
        info = kwargs['info']
        params = kwargs['params']
        need_axis = params['need_axis']
        file_type = params['file_type']
        start = params['start']
        end = params['end']
        fs = info['sample_rate']

        if is_none:
            abort(400, 'You need do Time_Freq first')

        # Calculate the maximum value in a segment for visualization
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
        """
        TimeFrequency analysis of data
        """
        source = kwargs['source']
        storage = kwargs['storage']
        info = kwargs['info']
        params = kwargs['params']
        storage_type = kwargs['modify_storage_type']

        channels = params['channels']
        raw = copy.deepcopy(source)
        freq = info['sample_rate']
        storage[storage_type]['Time_Freq'] = time_frequency(raw, channels, fs=freq, **params['advance_params'])
        return 'OK'
