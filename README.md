# MBPPE

A new modular EEG processing platform designed to facilitate pre-processing, feature extraction, and visualization of
EEG signals. This system automates batch processing through the creation of customized workflows and offers the
flexibility of personal offline usage or private deployment.

## Quick Start

1. Init env

During development, I used Node.js > 16.5 and Python 3.11.4 as the base environment. You can download Nodejs from the
following [link](https://nodejs.org/en).

> You may need restart compute to update Node env.

2. Install dependencies

```
cd MBPPE

# Install Python Env
pip install -r requirements.txt

# Install Node Env
npm i
```

3. Start APP

You can choose one of the following two methods to run the code.

```
# 1. Dev with Client [Offline Mode]
npm run dev

# 2. Dev with Broswer [Online Mode]
npm run preview
python ./python/app.py
```

> The first time you run `npm run dev`, a blank page may appear. This is because the program startup speed is faster
> than the page load time. You can resolve this issue by running the command again.

## Project Structure

The following is the primary structure of MBPPE, which may assist in enhancing your understanding of the code.

```
|   index.html  # Main structure of HTML
|   main.js  # Primary process file for electron handling system-related tasks
|   preload.js # Loads python server prior to app rendering, utilized for Offline Mode
|   
+---python # Server Code
|   |   app.py   # Main file of the Flask application [router adapter]
|   |   customSchema.py  # Custom schema for managing request parameters
|   |   load.py  # Default methods for loading EEG files
|   |   plugin.py  # Manager Plugin file uploaded by user
|   |   process.py  # Inbuilt methods for processing/extracting EEG data
|   |   utils.py  # Utility function library, used in the pipeline
|   |   
|   +---plugins
|           demo.py # Example of a plugin
|        
|           
\---src # Client Code
    |     
    +---config
    |       config.json # Configuration file for custom server and specified EEG data for processing
    |       
    |       
    +---utils # Client utilities
    |       api.js # Functions for backend interface calls [interface Driver]
    |       charts.js # Functions for chart generation
    |       npy.js # Script to convert numpy data to JavaScript array
    |       request.js # Functions for network requests
    |       
    \---views # UI of Client
            BaseCharts.vue # Visualization
            Dashboard.vue # Dashboard 
            Feature.vue # Feature extraction
            Home.vue
            Pipeline.vue # Pipeline
            Plugin.vue # Plugin 
            PreProcess.vue # Pre-processing
            Upload.vue  # Upload EEG data
            
```

## User Guide

![dashboard](./demo/dashboard.png)

Users can select modules according to their own needs.

1. Dashboard: Used to display the data information that has been processed in the current system.
2. Data Upload: Users can upload EEG data files in batches.
3. Pre Process: Preprocess EEG signals in a synchronous manner.
4. Analyse: Extract features from EEG signals in a synchronous manner.
5. Visualisation: Used for data visualization.
6. Pipeline: Used for creating and monitoring batch task sequences for multiple tasks
7. Plugin: Plugin methods, used for users to upload custom methods to meet more complex scenarios.

## Plugin Introduction (**NEW**)

You can write custom plugins as needed to suit complex processing scenarios.

Plugins need to appear in the form of functions, with reader, process, and extract providing three methods of data
reading, preprocessing, and feature extraction respectively. You can provide one or more methods in a plugin, and MBPPE
will automatically call the corresponding methods according to different modules.

Here is a simple example:

```python
'''
data: EEG data
params: User input parameters
kwargs: EEG info, such as sample rate
'''


def reader(data, params, **kwargs):
    print("reader")
    # custom methods
    return data


def process(data, params, **kwargs):
    print("process")
    # custom methods
    return data


def extract(data, params, **kwargs):
    print("feature")
    # custom methods
    return data
```