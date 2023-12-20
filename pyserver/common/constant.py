"""
This file defines constants for temporary storage of generated data
"""
'''
DATA_STORAGE data structure
{ 
  filename1 : DATA_STORAGE_TEMPLATE,
  filename2 : DATA_STORAGE_TEMPLATE,
}
'''
DATA_STORAGE = dict()

'''
DATA_STORAGE_TEMPLATE data structure
 {
    'Pre_Process': {'Raw': None, 'Filter': None, 'ICA': None, 'Filter_ICA': None},
    'Feature_Ext': {
        'Raw': {'PSD': None, 'DE': None, 'Freq': None, 'Time_Freq': None},
        'Filter': {'PSD': None, 'DE': None, 'Freq': None, 'Time_Freq': None},
        'ICA': {'PSD': None, 'DE': None, 'Freq': None, 'Time_Freq': None},
        'Filter_ICA': {'PSD': None, 'DE': None, 'Freq': None, 'Time_Freq': None}
    },
    Channels: {

    }
    'Info': {'sample_rate': 200}
}
'''
DATA_STORAGE_TEMPLATE = {
    'Pre_Process': {},
    'Feature_Ext': {},
    'Channels': {},
    'Info': {'sample_rate': 200}
}
'''
Pipeline Tasks data structure
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
TASKS = {}
'''
COMMENTS data structure
{
    "taskId": [
        {
            "title": "xxx", 
            "comment": "xxx", 
            "date": "xxxx"
        }
    ]
}
'''
COMMENTS = {}
