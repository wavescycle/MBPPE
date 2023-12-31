from pyserver.common.decorator import init_channels, init_data
from pyserver.common.customSchema import FilterSchema
from pyserver.common.utils import stream_data, get_data
from flask import send_file, abort
from flask_restful import Resource
import copy
from .methods import filters


class Filter(Resource):
    @init_data(FilterSchema, storage_type='Filter')
    @init_channels('Filter')
    def get(self, **kwargs):
        """
        Get filter Data
        """
        data, is_none = get_data(**kwargs)
        need_axis = kwargs['params']['need_axis']
        sample_rate = kwargs['info']['sample_rate']
        file_type = kwargs['params']['file_type']
        if is_none:
            abort(400, 'You need do filter first')
        else:
            return send_file(stream_data(data, need_axis, sample_rate, file_type=file_type),
                             mimetype="application/octet-stream")

    @init_data(FilterSchema, storage_type='Filter')
    @init_channels('Filter')
    def post(self, **kwargs):
        """
        Filtering of data
        """
        source = kwargs['source']
        storage = kwargs['storage']
        info = kwargs['info']
        params = kwargs['params']
        storage_type = kwargs['modify_storage_type']

        method = params['method']

        raw = copy.deepcopy(source)
        channels = params['channels']
        filter_type = params['filter_type']
        # filter data
        storage[storage_type] = filters(raw[channels], btype=method, low=params['low'], high=params['high'],
                                        fs=info['sample_rate'], filter_type=filter_type, **params['advance_params'])
        return 'OK'
