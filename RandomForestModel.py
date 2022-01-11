from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import helpers as h
import gis_extraction as gis
import joblib


# Add GIS Info to tracks_df and get features and labels
data_df, tracks_df = h.get_dataframes()  # Später von Jannis bekommen
tracks_df = gis.main(data_df, tracks_df)
features, labels, label_names = h.get_features_labels(input_features=h.INPUT_FEATURES,
                                                      data_df=data_df, tracks_df=tracks_df)


X_train, X_test, y_train, y_test = train_test_split(
    features,
    labels,
    test_size=0.3,
    random_state=42,
)


# Initialize RFC and train model
rf = RandomForestClassifier(n_estimators=100, max_depth=4, max_features=2, random_state=0)
rf.fit(X=X_train, y=y_train.values.ravel())
importance_list = rf.feature_importances_


# Statistics
prediction = rf.predict(X_test)
h.print_statistics(features, y_true=y_test, y_pred=prediction, importance=importance_list, label_names=label_names)


# Save model of random forest
joblib.dump(rf, h.SAVE_PATH_MODEL)
