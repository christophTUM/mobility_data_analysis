from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import helpers as h
import gis_extraction as gis
import joblib
import pandas as pd


def train() -> None:
    # Add GIS Info to tracks_df and get features and labels
    data_df, tracks_df = h.get_dataframes()
    tracks_df = gis.main(data_df, tracks_df)
    features, labels, label_names = h.get_features_labels(input_features=h.INPUT_FEATURES, tracks_df=tracks_df)

    x_train, x_test, y_train, y_test = train_test_split(
        features,
        labels,
        test_size=0.3,
        random_state=42,
    )

    # Initialize RFC and train model
    rf = RandomForestClassifier(n_estimators=100, max_depth=4, max_features=2, random_state=0)
    rf.fit(X=x_train, y=y_train.values.ravel())
    importance_list = rf.feature_importances_

    # Statistics
    prediction = rf.predict(x_test)
    h.print_statistics(features, y_true=y_test, y_pred=prediction, importance=importance_list, label_names=label_names)

    # Save model of random forest
    joblib.dump(rf, h.SAVE_PATH_MODEL)


def predict(kpi_dict: dict) -> str:

    kpi_df = pd.DataFrame([kpi_dict])
    kpi_df = kpi_df[h.INPUT_FEATURES]

    # Load Random Forest Model and Tracks Dataframe
    rf = joblib.load(h.SAVE_PATH_MODEL)
    predicted_modality = rf.predict(kpi_df)[0]

    # Dictionary for labels from model with label names as values
    label_names = ["car", "pedestrian", "still"]  # h.get_features_labels(h.INPUT_FEATURES, h.get_dataframes()[1])[2]
    labels = rf.classes_
    label_dict = dict(zip(labels, label_names))

    return label_dict[predicted_modality]


if __name__ == "__main__":
    train()
