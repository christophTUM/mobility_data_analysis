from sklearn import preprocessing
from sklearn.metrics import classification_report, ConfusionMatrixDisplay
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Declare file paths and constants.
#
PORT = 5050
BUFFER_RADIUS = 50
SERVER = "192.168.2.108"
DATA_PATH = 'data/tracks'
DATA_MOD_PATH = Path("data/mod")
DATA_RESULTS = Path("data/results")
FILE_ALL_DATA = Path("data/results/all_data.csv")
FILE_ALL_TRACKS = Path("data/results/all_tracks.csv")
FILE_ALL_MODALITIES = Path("data/results/all_modalities.csv")
#FILE_ALL_DATA = Path("/Users/christoph/Dropbox/MDA_Projekt/Dashboard_presentation/all_data.csv")
#FILE_ALL_TRACKS = Path("/Users/christoph/Dropbox/MDA_Projekt/Dashboard_presentation/all_tracks.csv")
#FILE_ALL_MODALITIES = Path("/Users/christoph/Dropbox/MDA_Projekt/Dashboard_presentation/all_modalities.csv")
FILE_TYPE = ('.csv', '.pkl')
SAVE_PATH_MODEL = Path("data/model/rf_model.joblib")
SAVE_PATH_MATRIX = Path("data/model/")  # Name and file type gets declared later (looping)
INPUT_FEATURES = ["track_distance", "mean_speed", "var_speed", "median_speed", "p85_speed", "stoprate",
                  "p85_accel", "var_accel"]


# Import Dataframes from .csv file
def get_dataframes():
    all_data_df = pd.read_csv(FILE_ALL_DATA)

    tracks_df = pd.read_csv(FILE_ALL_TRACKS)

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
def print_statistics(features, y_true, y_pred, importance, label_names) -> None:
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

    # Create 3 Confusion Matrices with different normalized principles
    normalize_list = [None, "true", "pred"]
    title_list = ["Not_normalized", "Recall", "Precision"]
    dict_normalize = dict(zip(normalize_list, title_list))

    for element in normalize_list:
        disp = ConfusionMatrixDisplay.from_predictions(y_true, y_pred, normalize=element, display_labels=label_names)
        title = dict_normalize[element]
        plt.title(label=title, fontsize=18)

        plt.savefig(SAVE_PATH_MATRIX.joinpath("Confusion_Matrix_" + title + ".eps"), format="eps")
        plt.show()


def lat_lon_2_m(latitude_1, longitude_1, latitude_2, longitude_2):
    # Radius of the earth in m
    radius_earth = 6371009
    d_latitude = np.deg2rad(latitude_2 - latitude_1)
    d_longitude = np.deg2rad(longitude_2 - longitude_1)
    latitude_1 = np.deg2rad(latitude_1)
    latitude_2 = np.deg2rad(latitude_2)
    a = (np.sin(d_latitude / 2)) ** 2 + np.cos(latitude_1) * np.cos(latitude_2) * (np.sin(d_longitude / 2)) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    distance = radius_earth * c
    return distance


def calculate_distance_points(points):
    # initialize distance array
    distance = np.zeros(len(points))
    # loop all points
    for i in range(0, len(points) - 1):
        # calculate distance between two consecutive points using lat_lon_2_km function
        d = lat_lon_2_m(
            points[i].x,
            points[i].y,
            points[i + 1].x,
            points[i + 1].y, )
        # append distance to array
        distance[i + 1] = d
    return distance


if __name__ == "__main__":
    pass
