from pyserver.common.decorator import init_data, init_channels
from pyserver.common.customSchema import BasicSchema
from pyserver.common.utils import stream_data, get_data
from flask import send_file, abort
from flask_restful import Resource
import copy
from .methods import ica


class ICA(Resource):

    @init_data(BasicSchema, storage_type='ICA')
    @init_channels("ICA")
    def get(self, **kwargs):
        """
        Get ICA data
        """
        data, is_none = get_data(**kwargs)
        need_axis = kwargs['params']['need_axis']
        sample_rate = kwargs['info']['sample_rate']
        file_type = kwargs['params']['file_type']
        if is_none:
            abort(400, 'You need do ICA first')
        else:
            return send_file(stream_data(data, need_axis, sample_rate, file_type=file_type),
                             mimetype="application/octet-stream")

    @init_data(BasicSchema, storage_type='ICA')
    @init_channels("ICA")
    def post(self, **kwargs):
        """
        ICA for data
        """
        source = kwargs['source']
        storage = kwargs['storage']
        params = kwargs['params']
        storage_type = kwargs['modify_storage_type']
        channels = params['channels']
        storage[storage_type] = ica(copy.deepcopy(source)[channels], **params['advance_params'])
        return 'OK'
