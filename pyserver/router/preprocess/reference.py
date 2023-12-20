from pyserver.common.decorator import init_channels, init_data
from pyserver.common.customSchema import RefSchema
from pyserver.common.utils import stream_data, get_data
from flask import send_file
from flask_restful import Resource
import copy
from .methods import re_reference


class Reference(Resource):
    @init_data(RefSchema, storage_type='Ref')
    @init_channels('Ref')
    def get(self, **kwargs):
        """
        Get Reference data
        """
        data, is_none = get_data(**kwargs)
        need_axis = kwargs['params']['need_axis']
        sample_rate = kwargs['info']['sample_rate']
        file_type = kwargs['params']['file_type']
        return send_file(stream_data(data, need_axis, sample_rate, file_type=file_type),
                         mimetype="application/octet-stream")

    @init_data(RefSchema, storage_type='Ref')
    @init_channels('Ref')
    def post(self, **kwargs):
        """
        Reference to the data
        """
        source = kwargs['source']
        storage = kwargs['storage']
        params = kwargs['params']
        storage_type = kwargs['modify_storage_type']
        channels = params['channels']

        raw = copy.deepcopy(source)
        storage[storage_type] = re_reference(raw[channels], mode=params['mode'], channel=params['ref_ch'])
