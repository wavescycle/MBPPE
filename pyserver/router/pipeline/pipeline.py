from flask import jsonify, abort, request, current_app, send_file
from flask_restful import Resource
from functools import wraps
from .methods import decode_async_task
from pyserver.common.constant import TASKS, DATA_STORAGE
from pyserver.common.utils import stream_data
import uuid
import threading

'''
# filter, ICA, PSD, DE, Freq, Time-Freq
# API
{
    'filename': Array<string>,
    'channels': Array<number>,
    'tasks': [
        {
            'seq': number,
            'task':{
                'method': string
                'info': {
                    ''
                }
            }
        }
    ]
}
'''

'''
{
    "task_id":{
        "task_info":[
            {"method": "string", "seq": "number"},
        ],
        "status_info":[
            {"filename": "string", "status": Enum<Status>},
        ],
        "data":[
            {"filename": ndArray},
        ],
        "current_task":{
            "filename": "string", "progress": "number"
        }
    }
}
'''


def async_api(wrapped_function):
    @wraps(wrapped_function)
    def new_function(*args, **kwargs):
        def task_call(flask_app, environ):
            # Create a request context similar to that of the original request
            # so that the task can have access to flask.g, flask.request, etc.
            with flask_app.request_context(environ):
                wrapped_function(*args, **kwargs)

        # Assign an id to the asynchronous task
        # task_id = uuid.uuid4().hex
        # task_id = '408a43a133ba420c9d4b3e9b6bf090e9'
        # Record the task, and then launch it
        t = threading.Thread(target=task_call, args=(current_app._get_current_object(),
                                                     request.environ))
        t.start()

        # Return a 202 response, with a link that the client can use to
        # obtain task status
        return 'accepted', 202

    return new_function


class Task(Resource):
    def get(self, task_id=None, filename=None):
        """
        Return status about an asynchronous task. If this request returns a 202
        status code, it means that task hasn't finished yet. Else, the response
        from the task is returned.
        """
        """
        task  get all task status
        task/task_id get special task status
        task/task_id/filename get task data
        """
        if task_id is None:
            return jsonify(
                [{'task_id': t_id, **{key: value for key, value in t_value.items() if key != 'data'}} for t_id, t_value
                 in TASKS.items()])

        task = TASKS.get(task_id)
        if task is None:
            abort(400)

        if filename is None:
            return jsonify({key: value for key, value in task.items() if key != 'data'})

        file_type = request.args.get("file_type")
        return send_file(stream_data(task['data'][filename], False, file_type=file_type),
                         mimetype="application/octet-stream")

    @async_api
    def post(self):
        """
        Creating pipeline tasks
        """
        # perform some intensive processing
        task_id = uuid.uuid4().hex
        # task_id = '187acda6aa0447739a37ae74f63dfc4a'
        body = request.json
        TASKS[task_id] = {}

        decode_async_task(TASKS[task_id], body, DATA_STORAGE)
        return True

    def delete(self, task_id):
        del TASKS[task_id]
        return 'Ok'
