from marshmallow import Schema, fields, pre_load
from marshmallow.validate import OneOf


class BaseSchema(Schema):
    pre_data = fields.String(data_key="pre_data", missing="Raw")
    need_axis = fields.Boolean(data_key="need_axis", missing=False)
    file_type = fields.String(data_key="file_type", missing="npy")

    @pre_load
    def preload(self, value, **kwargs):
        try:
            channels = value.getlist("channels", type=int)
            value = value.to_dict()
            value["channels"] = channels
        except AttributeError as e:
            pass
        return value


class DataSchema(BaseSchema):
    channels = fields.List(fields.Int, required=True, data_key="channels")
    start = fields.Int(data_key="start", missing=0)
    end = fields.Int(data_key="end", missing=10)
    method = fields.String(data_key="method", missing="")
    plugin = fields.String(data_key="plugin", missing=None)
    storage_path = fields.String(data_key="storage_path", missing=None)
    source_path = fields.String(data_key="source_path", missing=None)
    feature_ext = fields.String(data_key="Feature_Ext", missing=None)


class FilterSchema(BaseSchema):
    method = fields.Str(data_key="method", validate=OneOf((["lowpass", "highpass", "bandpass"])))
    low = fields.Float(data_key="low", missing=None)
    high = fields.Float(data_key="high", missing=None)
    channels = fields.List(fields.Int, required=True, data_key="channels")


class BasicSchema(BaseSchema):
    channels = fields.List(fields.Int, data_key="channels", missing=[])
    start = fields.Int(data_key="start", missing=None)
    end = fields.Int(data_key="end", missing=None)
    band_list = fields.String(data_key="band_list", missing=None)


class RefSchema(BaseSchema):
    channels = fields.List(fields.Int, data_key="channels", missing=[])
    mode = fields.Str(data_key="mode", missing="average")
    ref_ch = fields.List(fields.Int, data_key="ref_ch", missing=[])

    @pre_load
    def preload(self, value, **kwargs):
        try:
            channels = value.getlist("channels", type=int)
            ref_ch = value.getlist("ref_ch", type=int)
            value = value.to_dict()
            value["channels"] = channels
            value["ref_ch"] = ref_ch
        except AttributeError as e:
            pass
        return value


class SampleSchema(BaseSchema):
    new_fs = fields.Int(data_key="new_fs", required=True)


class PluginSchema(BaseSchema):
    channels = fields.List(fields.Int, required=True, data_key="channels")
    plugin_type = fields.Str(data_key="plugin_type", validate=OneOf((["Reader", "Pre_Process", "Feature_Ext"])))
    plugin_params = fields.Str(data_key="plugin_params")


class AsyncFilterSchema(Schema):
    method = fields.Str(data_key="method", validate=OneOf((["lowpass", "highpass", "bandpass"])))
    low = fields.Float(data_key="low", missing=None)
    high = fields.Float(data_key="high", missing=None)


class AsyncRefSchema(Schema):
    mode = fields.Str(data_key="mode", missing="average")
    ref_ch = fields.List(fields.Int, data_key="refChannels", missing=[])


class AsyncFreqSchema(Schema):
    band_list = fields.String(data_key="band_list", missing=None)


class AsyncPluginSchema(Schema):
    plugin = fields.String(data_key="plugin", required=True)
    plugin_params = fields.String(data_key="pluginParams", missing=None)
