from process import butter_filter
from enum import Enum
from copy import deepcopy
from process import butter_filter, power_spectrum, de, time_frequence, frequence, ica
import traceback
from customSchema import AsyncFilterSchema


# from app import DATA_STORAGE


class Status(Enum):
    SUCCESS = 1
    PROCESS = 2
    ERROR = 3
    WAIT = 4


def get_data(feature_ext=None, **kwargs):
    storage = kwargs['storage']
    storage_type = kwargs['modify_storage_type']
    params = kwargs['params']
    channels = params['channels']
    data = storage[storage_type]

    if feature_ext is not None:
        data = data[feature_ext]

    if data is None:
        return data, True
    else:
        return data[channels] if len(channels) > 0 else data, False


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


def decode_async_task(task_storage, task_info, data_storage):
    filenames = task_info['filenames']
    channels = task_info['channels']
    tasks = sorted(task_info['tasks'], key=lambda x: x['seq'])

    task_storage['task_info'] = tasks
    task_storage['status_info'] = [{'filename': filename, 'status': Status.WAIT.name} for filename in filenames]
    task_storage['data'] = {}
    task_storage['channels'] = channels
    task_storage['current_task'] = {'filename': None, 'progress': 0, 'sum_progress_percent': 0,
                                    'status': Status.PROCESS.name}
    sum_steps = len(filenames) * len(tasks)
    current_steps = 0
    for filename in filenames:
        task_params = {'sample_rate': data_storage[filename]['Info']['sample_rate']}
        task_storage['current_task']['filename'] = filename
        task_storage['current_task']['progress'] = 0
        data = deepcopy(data_storage[filename]['Pre_Process']['Raw'][channels])

        current_status_index = 0
        for index, value in enumerate(task_storage['status_info']):
            if value['filename'] == filename:
                current_status_index = index
                break

        task_storage['status_info'][current_status_index]['status'] = Status.PROCESS.name

        try:
            for task in tasks:
                current_steps += 1
                method = task['task']['method'].lower()
                info = task['task']['info']

                task_storage['current_task']['status'] = Status.PROCESS.name
                task_storage['current_task']['progress'] = task['seq']
                task_storage['data'][filename] = globals()[f'async_{method}'](data, info, **task_params)
                task_storage['current_task']['sum_progress_percent'] = int((current_steps / sum_steps) * 100)
                task_storage['current_task']['status'] = Status.SUCCESS.name

            task_storage['status_info'][current_status_index]['status'] = Status.SUCCESS.name
        except Exception as e:
            traceback.print_exc()
            task_storage['status_info'][current_status_index]['status'] = Status.ERROR.name
            task_storage['current_task']['status'] = Status.ERROR.name


def async_filter(data, info, **kwargs):
    info = AsyncFilterSchema().load(info)
    low = info.get("low")
    high = info.get("high")
    method = info['method']
    return butter_filter(data, btype=method, low=low, high=high, fs=kwargs['sample_rate'])


def async_ica(data, info, **kwargs):
    return ica(data)


def async_psd(data, info, **kwargs):
    return power_spectrum(data, kwargs['sample_rate'])


def async_de(data, info, **kwargs):
    freq = kwargs['sample_rate']
    return de(data, fs=freq, win=freq)


def async_freq(data, info, **kwargs):
    channels = info['channels']
    start = info['start']
    end = info['end']
    freq = kwargs['sample_rate']
    return frequence(data, channels, start, end, fs=freq)


def async_time_freq(data, info, **kwargs):
    freq = kwargs['sample_rate']
    channels = info['channels']
    start = info['start']
    end = info['end']
    data, _ = time_frequence(data, channels, start, end, fs=freq)
    return data


if __name__ == '__main__':
    TASK_ID = '408a43a133ba420c9d4b3e9b6bf090e9'
    TASKS = {}
    TASKS.setdefault(TASK_ID, {})
    TASK_INFO = {
        "filenames": ["4_20140621.mat", "14_20140627.mat"],
        "channels": [0, 1, 2, 3, 4, 5, 6, 7],
        "tasks": [
            {
                "seq": 1,
                "task": {
                    "method": "filter",
                    "info": {
                        "low": 1,
                        "high": 40,
                        "method": "bandpass"
                    }
                }
            },
            {
                "seq": 2,
                "task": {
                    "method": "ica",
                    "info": {}
                }
            },
            {
                "seq": 3,
                "task": {
                    "method": "psd",
                    "info": {}
                }
            }
        ]
    }

    decode_async_task(TASKS[TASK_ID], TASK_INFO, {})
    print(TASKS)
