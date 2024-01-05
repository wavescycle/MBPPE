from pyserver.common.decorator import init_channels, init_data
from pyserver.common.customSchema import SampleSchema
from pyserver.common.utils import stream_data, get_data
from flask import send_file
from flask_restful import Resource
import copy
from .methods import resample


class Resample(Resource):
    @init_data(SampleSchema, storage_type='Sample')
    @init_channels('Sample')
    def get(self, **kwargs):
        """
        Get Resample data
        """
        data, is_none = get_data(**kwargs)
        need_axis = kwargs['params']['need_axis']
        sample_rate = kwargs['info']['sample_rate']
        file_type = kwargs['params']['file_type']

        return send_file(stream_data(data, need_axis, sample_rate, file_type=file_type),
                         mimetype="application/octet-stream")

    @init_data(SampleSchema, storage_type='Sample')
    @init_channels('Sample')
    def post(self, **kwargs):
        """
        Resample the data
        """
        source = kwargs['source']
        storage = kwargs['storage']
        info = kwargs['info']
        params = kwargs['params']
        storage_type = kwargs['modify_storage_type']

        raw = copy.deepcopy(source)
        channels = params['channels']
        # filter data
        storage[storage_type] = resample(raw[channels], fs=info['sample_rate'], new_fs=params['new_fs'],
                                         **params['advance_params'])
        return 'OK'
