from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import helpers as h
import gis_extraction as g


# Get Features and labels
INPUT_FEATURES = ["mean_speed", "max_speed", "mean_accel", "max_accel", "bus_count", "sub_count"]
data_df, tracks_df = h.get_dataframes()
tracks_df = g.main(data_df, tracks_df)
features, labels, label_names = h.get_features_labels(input_features=INPUT_FEATURES,
                                                      data_df=data_df, tracks_df=tracks_df)

print(tracks_df)
X_train, X_test, y_train, y_test = train_test_split(
    features,
    labels,
    test_size=0.3,
    random_state=42,
)


# Initialize RFC, train and predict with RFC
clf = RandomForestClassifier(n_estimators=100, max_depth=4, max_features=2, random_state=0)
clf.fit(X=X_train, y=y_train.values.ravel())
importance_list = clf.feature_importances_
prediction = clf.predict(X_test)

# Statistics
h.print_statistics(features, y_true=y_test, y_pred=prediction, importance=importance_list, label_names=label_names)