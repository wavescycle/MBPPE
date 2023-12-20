import traceback
from enum import Enum
from copy import deepcopy
from .buildIn import *


class Status(Enum):
    """
    Pipeline Task Status
    """
    SUCCESS = 1
    PROCESS = 2
    ERROR = 3
    WAIT = 4


def decode_async_task(task_storage, task_info, data_storage):
    """
    Parses the parameters of a pipeline task and executes the task sequence step-by-step.
    """
    filenames = task_info['filenames']
    channels = task_info['channels']
    tasks = sorted(task_info['tasks'], key=lambda x: x['seq'])
    # # initialize the task_storage with the tasks, status information, data, channels, and current task
    task_storage['task_info'] = tasks
    task_storage['status_info'] = [{'filename': filename, 'status': Status.WAIT.name} for filename in filenames]
    task_storage['data'] = {}
    task_storage['channels'] = channels
    task_storage['current_task'] = {'filename': None, 'progress': 0, 'sum_progress_percent': 0,
                                    'status': Status.PROCESS.name}
    sum_steps = len(filenames) * len(tasks)
    current_steps = 0
    # iterate over each filename
    for filename in filenames:
        task_params = {'sample_rate': data_storage[filename]['Info']['sample_rate']}
        task_storage['current_task']['filename'] = filename
        task_storage['current_task']['progress'] = 0
        data = deepcopy(data_storage[filename]['Pre_Process']['Raw'][channels])

        # find the index of the current filename in the status_info
        current_status_index = 0
        for index, value in enumerate(task_storage['status_info']):
            if value['filename'] == filename:
                current_status_index = index
                break

        task_storage['status_info'][current_status_index]['status'] = Status.PROCESS.name

        try:
            # iterate over each task
            for task in tasks:
                current_steps += 1
                method = task['task']['method'].lower()
                info = task['task']['info']
                # set the status of the current task to PROCESS
                task_storage['current_task']['status'] = Status.PROCESS.name
                # update the progress of the current task
                task_storage['current_task']['progress'] = task['seq']
                # call the method of the current task and store the result in the data
                task_storage['data'][filename] = globals()[f'async_{method}'](data, info, **task_params)
                # calculate the sum_progress_percent
                task_storage['current_task']['sum_progress_percent'] = int((current_steps / sum_steps) * 100)
                task_storage['current_task']['status'] = Status.SUCCESS.name

            task_storage['status_info'][current_status_index]['status'] = Status.SUCCESS.name
        except Exception as e:
            traceback.print_exc()
            task_storage['status_info'][current_status_index]['status'] = Status.ERROR.name
            task_storage['current_task']['status'] = Status.ERROR.name
