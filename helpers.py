from sklearn import preprocessing
from sklearn.metrics import classification_report, ConfusionMatrixDisplay
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Declare file paths
ALL_DATA = "data/20211219_01_all_data.csv"
TRACKS = "data/20211214_01_all_tracks.csv"
BUFFER_RADIUS = 25


def get_dataframes():
    all_data_df = pd.read_csv(ALL_DATA)

    tracks_df = pd.read_csv(TRACKS,
                            header=0,
                            usecols=["modality", "time_start", "time_stop", "mean_speed", "max_speed",
                                     "mean_accel", "max_accel"])

    tracks_df["time_start"] = tracks_df.time_start.astype('datetime64[ns]')
    tracks_df["time_stop"] = tracks_df.time_stop.astype('datetime64[ns]')
    all_data_df["time"] = all_data_df.time.astype('datetime64[ns]')

    tracks_df[["bus_count", "sub_count"]] = None

    return all_data_df, tracks_df


def get_features_labels(input_features, data_df, track_df):
    le = preprocessing.LabelEncoder()
    le.fit(data_df["modality"].values)
    le.fit(track_df["modality"].values)
    data_df["modality_numbers"] = le.transform(data_df["modality"].values)
    track_df["modality_numbers"] = le.transform(track_df["modality"].values)

    features = track_df[input_features]
    labels = track_df[["modality_numbers"]]

    label_names = np.sort(track_df["modality"].unique())

    return features, labels, label_names


# Calculate statistics
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

    disp = ConfusionMatrixDisplay.from_predictions(y_true, y_pred)
    disp.plot()
    plt.show()
