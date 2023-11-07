# MBPPE

A new modular EEG processing platform designed to facilitate pre-processing, feature extraction, and visualization of
EEG signals. This system automates batch processing through the creation of customized workflows and offers the
flexibility of personal offline usage or private deployment.

## Quick Start

0. Test ENV

During development, I used Node.js > 16.5 and Python 3.11.4 as the base environment. You can download Nodejs from the
following [link](https://nodejs.org/en).

> You may need restart compute to update Node Env.

1. Install dependencies

```
cd MBPPE

# Install Python Env
pip install -r requirements.txt

# Install Node Env
npm i
```

2. Start APP

You can choose one of the following two methods to run the code.

```
# Dev with Client [Offline Mode]
npm run dev

# Dev with Broswer [Online Mode]
npm run preview
python ./python/app.py
```

## User guide

![dashboard](./demo/dashboard.png)

Users can select modules according to their own needs.

1. Dashboard: Used to display the data information that has been processed in the current system.
2. Data Upload: Users can upload EEG data files in batches.
3. Pre Process: Preprocessing methods.
4. Analyse: Feature extraction methods.
5. Visualisation: Used for data visualization.
6. Pipeline: Used for creating batch task sequences for multiple tasks.
7. Plugin: Plugin methods, used for users to upload custom methods to meet more complex scenarios.