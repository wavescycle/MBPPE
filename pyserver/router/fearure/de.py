from pyserver.common.decorator import init_channels, init_data
from pyserver.common.customSchema import BasicSchema
from pyserver.common.utils import stream_data, get_data
from flask import send_file, abort
from flask_restful import Resource
from .methods import de
import copy


class DE(Resource):

    @init_data(BasicSchema, storage_path="Feature_Ext", storage_type='DE')
    def get(self, **kwargs):
        """
        Get Differential Entropy Data
        """
        data, is_none = get_data(feature_ext="DE", **kwargs)
        need_axis = kwargs['params']['need_axis']
        sample_rate = kwargs['info']['sample_rate']
        file_type = kwargs['params']['file_type']
        if is_none:
            abort(400, 'You need do DE first')
        else:
            return send_file(stream_data(data, need_axis, sample_rate, file_type=file_type),
                             mimetype="application/octet-stream")

    @init_data(BasicSchema, storage_path="Feature_Ext", storage_type='DE')
    def post(self, **kwargs):
        """
        Differential entropy analysis of data
        """
        source = kwargs['source']
        storage = kwargs['storage']
        info = kwargs['info']
        storage_type = kwargs['modify_storage_type']

        raw = copy.deepcopy(source)
        freq = info['sample_rate']
        storage[storage_type]['DE'] = de(raw, fs=freq, win=freq)
        return 'OK'
