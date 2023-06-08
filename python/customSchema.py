from marshmallow import Schema, fields, pre_load
from marshmallow.validate import OneOf


class DataSchema(Schema):
    channels = fields.List(fields.Int, required=True, data_key="channels")
    isFilter = fields.Boolean(data_key="isFilter", missing=False)
    isPSD = fields.Boolean(data_key="isPSD", missing=False)
    isHeatMap = fields.Boolean(data_key="isHeatMap", missing=False)
    isDe = fields.Boolean(data_key="isDe", missing=False)
    isProcess = fields.Boolean(data_key="isProcess", missing=False)

    @pre_load
    def preload(self, value, **kwargs):
        channels = value.getlist("channels", type=int)
        value = value.to_dict()
        value['channels'] = channels
        return value


class FilterSchema(Schema):
    # channels = fields.List(fields.Int, required=True, data_key="channels")
    method = fields.Str(required=True,
                        data_key="method",
                        validate=OneOf((['low', 'high', 'band'])))
    low = fields.Float(data_key="low", missing=None)
    high = fields.Float(data_key="high", missing=None)
    '''
    @pre_load
    def preload(self, value, **kwargs):
        if type(value) != dict:
            channels = value.getlist("channels[]", type=int)
        value = value.to_dict()
        value['channels'] = channels
        return value
    filename = fields.Str(required=True)
    @validates_schema()
    def validates(self, data, **kwargs):
        method = data['method']
        if method == 'band':
            if 'high' not in data or 'low' not in data:
                raise ValidationError('Missing field low or high')
        else:
            if method not in data:
                raise ValidationError('Missing field ' + method)
    @validates_schema()
    def validates(self, data, **kwargs):
        if data['low'] == '' or data['high'] == '':
            return None

    '''


class BasicSchema(Schema):
    isFilter = fields.Boolean(data_key="isFilter", missing=False)
    isICA = fields.Boolean(data_key="isICA", missing=False)
    channels = fields.Int(data_key="channels", missing=0)
    start = fields.Int(data_key="start", missing=0)
    end = fields.Int(data_key="end", missing=10)
