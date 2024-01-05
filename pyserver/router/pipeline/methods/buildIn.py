from copy import deepcopy
from marshmallow import EXCLUDE
from pyserver.common.customSchema import AsyncFilterSchema, AsyncRefSchema, SampleSchema, AsyncFreqSchema, \
    AsyncPluginSchema, AsyncBaseSchema
from pyserver.router.plugin.manager import PM
from pyserver.router.preprocess.methods import filters, ica, resample, re_reference
from pyserver.router.fearure.methods import power_spectrum, de, frequency, time_frequency

"""
Read the parameters needed for asynchronous execution and execute the built-in methods
"""


def async_filter(data, info, **kwargs):
    info = AsyncFilterSchema().load(info)
    low = info.get('low')
    high = info.get('high')
    method = info['method']
    filter_type = info['filter_type']
    advance_params = info['advance_params']
    return filters(data, btype=method, low=low, high=high, fs=kwargs['sample_rate'], filter_type=filter_type,
                   **advance_params)


def async_ica(data, info, **kwargs):
    info = AsyncBaseSchema().load(info)
    advance_params = info['advance_params']
    return ica(data, **advance_params)


def async_psd(data, info, **kwargs):
    info = AsyncBaseSchema().load(info)
    advance_params = info['advance_params']
    return power_spectrum(data, kwargs['sample_rate'], **advance_params)


def async_de(data, info, **kwargs):
    freq = kwargs['sample_rate']
    return de(data, fs=freq, win=freq)


def async_freq(data, info, **kwargs):
    freq = kwargs['sample_rate']
    info = AsyncFreqSchema(unknown=EXCLUDE).load(info)
    advance_params = info['advance_params']
    return frequency(data, None, fs=freq, iter_freq=info.get('band_list'), **advance_params)


def async_time_freq(data, info, **kwargs):
    freq = kwargs['sample_rate']
    channels = slice(None)
    info = AsyncBaseSchema().load(info)
    advance_params = info['advance_params']
    return time_frequency(data, channels, fs=freq, **advance_params)


def async_reference(data, info, **kwargs):
    info = AsyncRefSchema(unknown=EXCLUDE).load(info)
    return re_reference(data, mode=info.get('mode'), channel=info.get('ref_ch'))


def async_resample(data, info, **kwargs):
    info = SampleSchema(unknown=EXCLUDE).load(info)
    advance_params = info['advance_params']
    return resample(data, kwargs['sample_rate'], info['new_fs'], **advance_params)


def async_plugin(data, info, **kwargs):
    info = AsyncPluginSchema(unknown=EXCLUDE).load(info)
    plugin_type, plugin = info['plugin'].split('$')
    plugin_params = info['plugin_params']
    if plugin_type == 'Feature_Ext':
        return PM.get_plugin(plugin).extract(data, plugin_params, **kwargs)
    elif plugin_type == 'Pre_Process':
        return PM.get_plugin(plugin).process(data, plugin_params, **kwargs)
