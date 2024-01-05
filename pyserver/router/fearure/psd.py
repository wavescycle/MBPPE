from pyserver.common.decorator import init_channels, init_data
from pyserver.common.customSchema import BasicSchema
from pyserver.common.utils import stream_data, get_data
from flask import send_file, abort
from flask_restful import Resource
from .methods import power_spectrum
import copy


class PSD(Resource):

    @init_data(BasicSchema, storage_path="Feature_Ext", storage_type='PSD')
    def get(self, **kwargs):
        """
        Get PSD data
        """
        data, is_none = get_data(feature_ext="PSD", **kwargs)
        file_type = kwargs['params']['file_type']
        if is_none:
            abort(400, 'You need do PSD first')
        else:
            return send_file(stream_data(data, False, file_type=file_type), mimetype="application/octet-stream")

    @init_data(BasicSchema, storage_path="Feature_Ext", storage_type='PSD')
    def post(self, **kwargs):
        """
        PSD analysis of data
        """
        source = kwargs['source']
        storage = kwargs['storage']
        info = kwargs['info']
        storage_type = kwargs['modify_storage_type']

        raw = copy.deepcopy(source)
        freq = info['sample_rate']
        params = kwargs['params']
        storage[storage_type]['PSD'] = power_spectrum(raw, freq, **params['advance_params'])
        return 'OK'
