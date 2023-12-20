"""
This file for managing comments associated with a specific pipeline.
"""
from flask import request
from flask_restful import Resource
from pyserver.common.constant import COMMENTS


class Comments(Resource):
    def get(self, pipeline_id):
        """
        Retrieves the comments associated with a given pipeline_id
        """
        return COMMENTS.get(pipeline_id, [])

    def post(self, pipeline_id):
        """
        Adds a new comment to the list of comments associated with a given pipeline_id
        """
        params = request.json
        COMMENTS.setdefault(pipeline_id, [])
        COMMENTS[pipeline_id].append(params['data'])
        return COMMENTS[pipeline_id], 201
