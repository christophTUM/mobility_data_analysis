from sklearn import preprocessing
from sklearn.metrics import classification_report, ConfusionMatrixDisplay
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Declare file paths and constants.
PORT = 5050
SERVER = "127.0.0.1"
SAVE_PATH_MODEL = "./rf_model.joblib"
ALL_DATA = "data/20220106_01_all_data.csv"
TRACKS = "data/20220106_01_all_tracks.csv"
BUFFER_RADIUS = 50
INPUT_FEATURES = ["track_distance", "mean_speed", "var_speed", "median_speed", "p95_speed", "stoprate", "mean_accel",
                  "median_accel", "p95_accel", "var_accel"]


# Import Dataframes from .csv file TODO Not necessary if scripts are merged
def get_dataframes():
    all_data_df = pd.read_csv(ALL_DATA)

    tracks_df = pd.read_csv(TRACKS)

    tracks_df["time_start"] = tracks_df.time_start.astype('datetime64[ns]')
    tracks_df["time_stop"] = tracks_df.time_stop.astype('datetime64[ns]')
    all_data_df["time"] = all_data_df.time.astype('datetime64[ns]')

    tracks_df[["bus_count", "sub_count"]] = None

    return all_data_df, tracks_df


# Return features and convert labels to number. Only used for training phase.
def get_features_labels(input_features, tracks_df):
    le = preprocessing.LabelEncoder()
    le.fit(tracks_df["modality"].values)
    tracks_df["modality_numbers"] = le.transform(tracks_df["modality"].values)

    features = tracks_df[input_features]
    labels = tracks_df[["modality_numbers"]]

    label_names = np.sort(tracks_df["modality"].unique())

    return features, labels, label_names


# Calculate and print statistics. Only used for training phase.
def print_statistics(features, y_true, y_pred, importance, label_names):
    cols = features.columns.values
    importance_list = list(sorted(zip(cols, importance), key=lambda x: x[1], reverse=True))
    report = classification_report(y_true=y_true, y_pred=y_pred, target_names=label_names, output_dict=True)
    report_df = pd.DataFrame(report).round(2)
    report_df = report_df.drop(columns=["accuracy", "macro avg", "weighted avg"])
    report_df = report_df.drop("support", axis=0)

    print("\n----- Statistics -----")
    print(report_df)

    print("\n----- Normalized importance of features -----")
    for pair in importance_list:
        print("%s: %.2f" % (pair[0], pair[1]))

    disp = ConfusionMatrixDisplay.from_predictions(y_true, y_pred, display_labels=label_names)
    disp.plot()
    plt.show()
