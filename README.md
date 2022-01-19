# Mobility Data Analysis Script for TUM

## Installation
```
git clone git@github.com:christophTUM/mobility_data_analysis.git
```
## Folder structure
```
├── data
│   ├── mod (helpers folder for data processing)
│   ├── model
│   │   ├── rf_model.joblib
│   ├── results (has to be created by user)
│       ├── all_data.csv
│       ├── all_track.csv
│       ├── all_modalities.csv
│   └── tracks (has to be created by user)
│       ├── (input tracks for classification)
├── src
│   ├── classifier.py
│   ├── client.py
│   ├── gis_extraction.py
│   ├── helpers.py
│   ├── main.py
│   ├── server.py
│   ├── utilities_analysis.py
│   └── utilities_scanner.py
├── LICENSE.txt
└── README.md
```