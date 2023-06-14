from marshmallow import Schema, fields, pre_load
from marshmallow.validate import OneOf


class DataSchema(Schema):
    channels = fields.List(fields.Int, required=True, data_key="channels")
    # isFilter = fields.Boolean(data_key="isFilter", missing=False)
    # isPSD = fields.Boolean(data_key="isPSD", missing=False)
    # isHeatMap = fields.Boolean(data_key="isHeatMap", missing=False)
    # isDe = fields.Boolean(data_key="isDe", missing=False)
    isProcess = fields.Boolean(data_key="isProcess", missing=False)
    start = fields.Int(data_key="start", missing=0)
    end = fields.Int(data_key="end", missing=10)
    pre_data = fields.String(data_key="pre_data", missing='Raw')
    method = fields.String(data_key="method", missing="")

    @pre_load
    def preload(self, value, **kwargs):
        channels = value.getlist("channels", type=int)
        value = value.to_dict()
        value['channels'] = channels
        return value


class FilterSchema(Schema):
    method = fields.Str(data_key="method", validate=OneOf((['low', 'high', 'band'])))
    low = fields.Float(data_key="low", missing=None)
    high = fields.Float(data_key="high", missing=None)
    channels = fields.List(fields.Int, required=True, data_key="channels")

    @pre_load
    def preload(self, value, **kwargs):
        try:
            channels = value.getlist("channels", type=int)
            value = value.to_dict()
            value['channels'] = channels
        except AttributeError as e:
            pass
        return value


class BasicSchema(Schema):
    isFilter = fields.Boolean(data_key="isFilter", missing=False)
    isICA = fields.Boolean(data_key="isICA", missing=False)
    channels = fields.List(fields.Int, data_key="channels", missing=[])
    start = fields.Int(data_key="start", missing=0)
    end = fields.Int(data_key="end", missing=10)
    pre_data = fields.String(data_key="pre_data", missing='Raw')
