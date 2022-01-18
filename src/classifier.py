from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import helpers as h
import gis_extraction as gis
import joblib
import pandas as pd
from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import GridSearchCV
import numpy as np


def train() -> None:
    """Train and save model, return confusion matrices."""

    print("---- Starting training of model ----")
    # Add GIS Info to tracks_df and get features and labels
    data_df, tracks_df = h.get_dataframes()
    features, labels, label_names = h.get_features_labels(input_features=h.INPUT_FEATURES, tracks_df=tracks_df)

    x_train, x_test, y_train, y_test = train_test_split(
        features,
        labels,
        test_size=0.3,
        random_state=42,
    )

    # k-fold Cross Validation
    print("--- Starting RandomizedSearchCV ---")
    n_estimators = [int(x) for x in np.linspace(start=200, stop=3000, num=10)]
    max_features = ['auto', 'sqrt', 4, 5, 6]
    max_depth = [int(x) for x in np.linspace(10, 110, num=11)]
    max_depth.append(None)
    min_samples_split = [2, 5, 10]
    min_samples_leaf = [1, 2, 4]
    bootstrap = [True, False]

    # Create the random grid
    random_grid = {'n_estimators': n_estimators,
                   'max_features': max_features,
                   'max_depth': max_depth,
                   'min_samples_split': min_samples_split,
                   'min_samples_leaf': min_samples_leaf,
                   'bootstrap': bootstrap}

    combinations = (len(n_estimators) * len(max_features) * len(max_depth) * len(min_samples_split) *
                    len(min_samples_leaf) * len(bootstrap))
    print(f"-- Number of possible combinations: {combinations} --")

    # Use the random grid to search for best hyperparameters
    rf = RandomForestClassifier()
    n_iter = 100
    cv = 3
    rf_random = RandomizedSearchCV(estimator=rf, param_distributions=random_grid, n_iter=n_iter, cv=cv, verbose=0,
                                   random_state=42, n_jobs=-1)

    print(f"-- Fitting {cv} fold for each of {n_iter} candidates, totalling {cv * n_iter} "
          f"fits. This may take some while --")
    rf_random.fit(x_train, np.ravel(y_train))

    print("-- Finished fitting. These are the best parameters that were found: --")
    print(rf_random.best_params_)

    print("-- Starting GridSearchCV. Remember to change parameters! --")
    param_grid = {
        'bootstrap': [True],
        'max_depth': [80, 90, 100, 110],
        'max_features': [2, 3],
        'min_samples_leaf': [3, 4, 5],
        'min_samples_split': [8, 10, 12],
        'n_estimators': [100, 200, 300, 1000]
    }

    combinations = (len(param_grid["bootstrap"]) * len(param_grid["max_depth"]) * len(param_grid["max_features"]) *
                    len(param_grid["min_samples_leaf"]) * len(param_grid["min_samples_split"]) *
                    len(param_grid["n_estimators"]))
    print(f"-- Number of possible combinations: {combinations} --")

    # Instantiate the grid search model
    grid_search = GridSearchCV(estimator=rf, param_grid=param_grid,
                               cv=3, n_jobs=-1, verbose=0)

    print(f"-- Fitting {cv} fold for each of {combinations} candidates, totalling {cv * combinations} "
          f"fits. This may take some while --")
    grid_search.fit(x_train, np.ravel(y_train))
    rf = grid_search.best_estimator_
    print("-- Finished fitting. Assigned best model as final trained model. --")

    # Initialize RFC and train model
    #rf = RandomForestClassifier(n_estimators=800, max_depth=50, max_features="sqrt", random_state=0, min_samples_leaf=2,
                                #min_samples_split=2)
    #rf.fit(X=x_train, y=y_train.values.ravel())
    importance_list = rf.feature_importances_

    # Statistics
    prediction = rf.predict(x_test)
    h.print_statistics(features, y_true=y_test, y_pred=prediction, importance=importance_list, label_names=label_names)

    # Save model of random forest
    joblib.dump(rf, h.SAVE_PATH_MODEL)


def predict(kpi_dict: dict) -> str:
    """predicts modality with loaded model and returns it as string."""

    kpi_df = pd.DataFrame([kpi_dict])
    kpi_df = kpi_df[h.INPUT_FEATURES]

    rf = joblib.load(h.SAVE_PATH_MODEL)
    predicted_modality = rf.predict(kpi_df)[0]

    # Dictionary for labels from model with label names as values
    label_names = ["car", "pedestrian", "still"]
    labels = rf.classes_
    label_dict = dict(zip(labels, label_names))

    return label_dict[predicted_modality]


if __name__ == "__main__":
    train()
