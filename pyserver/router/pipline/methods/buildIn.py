from copy import deepcopy
from marshmallow import EXCLUDE
from pyserver.common.customSchema import AsyncFilterSchema, AsyncRefSchema, SampleSchema, AsyncFreqSchema, \
    AsyncPluginSchema
from pyserver.router.plugin.manager import PM
from pyserver.router.preprocess.methods import fir_filter, ica, resample, re_reference
from pyserver.router.fearure.methods import power_spectrum, de, frequency, time_frequency

"""
Read the parameters needed for asynchronous execution and execute the built-in methods
"""


def async_filter(data, info, **kwargs):
    info = AsyncFilterSchema().load(info)
    low = info.get('low')
    high = info.get('high')
    method = info['method']
    return fir_filter(data, btype=method, low=low, high=high, fs=kwargs['sample_rate'])


def async_ica(data, info, **kwargs):
    return ica(data)


def async_psd(data, info, **kwargs):
    return power_spectrum(data, kwargs['sample_rate'])


def async_de(data, info, **kwargs):
    freq = kwargs['sample_rate']
    return de(data, fs=freq, win=freq)


def async_freq(data, info, **kwargs):
    freq = kwargs['sample_rate']
    info = AsyncFreqSchema(unknown=EXCLUDE).load(info)
    return frequency(data, None, fs=freq, iter_freq=info.get('band_list'))


def async_time_freq(data, info, **kwargs):
    freq = kwargs['sample_rate']
    channels = slice(None)
    return time_frequency(data, channels, fs=freq)


def async_reference(data, info, **kwargs):
    info = AsyncRefSchema(unknown=EXCLUDE).load(info)
    return re_reference(data, mode=info.get('mode'), channel=info.get('ref_ch'))


def async_resample(data, info, **kwargs):
    info = SampleSchema(unknown=EXCLUDE).load(info)
    return resample(data, kwargs['sample_rate'], info['new_fs'])


def async_plugin(data, info, **kwargs):
    info = AsyncPluginSchema(unknown=EXCLUDE).load(info)
    plugin_type, plugin = info['plugin'].split('$')
    plugin_params = info['plugin_params']
    if plugin_type == 'Feature_Ext':
        return PM.get_plugin(plugin).extract(data, plugin_params, **kwargs)
    elif plugin_type == 'Pre_Process':
        return PM.get_plugin(plugin).process(data, plugin_params, **kwargs)
