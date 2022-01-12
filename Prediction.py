import helpers as h
import joblib
import pandas as pd


def predict(kpi_dict: dict):

    kpi_df = pd.DataFrame([kpi_dict])
    kpi_df = kpi_df[h.INPUT_FEATURES]
    #kpi_list = []
    #for feature in h.INPUT_FEATURES:
    #    kpi_list.append(kpi_dict[feature])


    # Load Random Forest Model and Tracks Dataframe
    rf = joblib.load(h.SAVE_PATH_MODEL)
    predicted_modality = rf.predict(kpi_df)

    if predicted_modality == 0:
        predicted_modality = "car"
    elif predicted_modality == 1:
        predicted_modality = "pedestrian"
    else:
        predicted_modality = "still"

    return predicted_modality  # TODO Return string not int
