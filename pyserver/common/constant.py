'''
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
DATA_STORAGE = dict()
TASKS = {}
COMMENTS = {}
