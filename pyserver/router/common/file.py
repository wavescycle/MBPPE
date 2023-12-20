from flask_restful import Resource
from flask import jsonify, abort, request
from marshmallow import ValidationError, EXCLUDE
from pyserver.common.customSchema import BasicSchema
from pyserver.common.constant import DATA_STORAGE


class FileList(Resource):
    def get(self):
        params = request.args
        try:
            BasicSchema(unknown=EXCLUDE).load(params)
        except ValidationError as e:
            abort(400, str(e.messages))

        data = DATA_STORAGE.keys()
        return jsonify(list(data))


class FileTreeList(Resource):
    def get(self):
        file_trees = []
        for k, v in DATA_STORAGE.items():
            temp = {
                'filename': k,
                'sample_rate': v['Info']['sample_rate'],
                'data_type':
                    {'Pre_Process': list(v['Pre_Process'].keys())}
            }
            new_dict = {}
            for outer_key, inner_dict in v['Feature_Ext'].items():
                for inner_key, value in inner_dict.items():
                    if value is not None:  # Ignore None values
                        new_dict.setdefault(inner_key, []).append(outer_key)

            temp['data_type']['Feature_Ext'] = new_dict
            file_trees.append(temp)
        return jsonify(file_trees)


class FileStatus(Resource):
    def get(self):
        file_status = list()
        for k in DATA_STORAGE.keys():
            file_status.append({
                'Filename': k
            })
        return jsonify(file_status)
