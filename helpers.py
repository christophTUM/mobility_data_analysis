from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from sklearn.metrics import recall_score, precision_score, classification_report, multilabel_confusion_matrix, ConfusionMatrixDisplay
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# Declare file paths
ALL_DATA = "data/20211219_01_all_data.csv"
TRACKS = "data/20211214_01_all_tracks.csv"
BUFFER_RADIUS = 20


def get_dataframes():
    all_data_df = pd.read_csv(ALL_DATA,
                              header=0,
                              usecols=["modality", "speed_rolling_median"])

    track_df = pd.read_csv(TRACKS,
                           header=0,
                           usecols=["modality", "time_start", "time_stop", "mean_speed", "max_speed",
                                    "mean_accel", "max_accel"])

    return all_data_df, track_df


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
        print(pair[0], ":", pair[1])

    disp = ConfusionMatrixDisplay.from_predictions(y_true, y_pred)
    disp.plot()
    plt.show()
