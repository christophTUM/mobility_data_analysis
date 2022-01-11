from sklearn.ensemble import RandomForestClassifier
import helpers as h
import gis_extraction as g
import joblib
import pandas as pd
import import_script # Jannis' Script


# TODO Modifiy once scripts are merged
# Load Random Forest Model and Tracks Dataframe
rf = joblib.load(h.SAVE_PATH_MODEL)
X_predict = import_script.tracks_df[h.INPUT_FEATURES]

# Statistics
prediction = rf.predict(X_predict)
X_predict["modality"] = prediction

X_predict.to_csv("data/tracks_modalities.csv")
