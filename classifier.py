from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import helpers as h


# Get Features and labels
INPUT_FEATURES = ["mean_speed", "max_speed", "mean_accel", "max_accel"]
data_df, track_df = h.get_dataframes()
features, labels, label_names = h.get_features_labels(input_features=INPUT_FEATURES, data_df=data_df, track_df=track_df)


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
