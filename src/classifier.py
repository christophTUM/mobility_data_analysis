from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import helpers as h
#import gis_extraction as gis
import joblib
import pandas as pd
from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import GridSearchCV
import numpy as np


def train(n_iter=100, cv=3) -> None:
    """Train and save model via k-fold cross validation, return confusion matrices."""

    print("- Starting training of model -")
    # Import necessary dataframes and create train/test labels
    data_df, tracks_df = h.get_dataframes()
    features, labels, label_names = h.get_features_labels(input_features=h.INPUT_FEATURES, tracks_df=tracks_df)

    x_train, x_test, y_train, y_test = train_test_split(
        features,
        labels,
        test_size=0.3,
        random_state=42,
    )

    # k-fold Cross Validation
    n_estimators = [int(x) for x in np.linspace(start=200, stop=3000, num=10)]
    max_features = [3, 4, 5, 6, 7]
    max_depth = [int(x) for x in np.linspace(10, 110, num=11)]
    max_depth.append(None)
    min_samples_split = [2, 5, 10]
    min_samples_leaf = [1, 2, 4]
    bootstrap = [True]

    # Random grid for RandomizedSearchCV
    random_grid = {'n_estimators': n_estimators,
                   'max_features': max_features,
                   'max_depth': max_depth,
                   'min_samples_split': min_samples_split,
                   'min_samples_leaf': min_samples_leaf,
                   'bootstrap': bootstrap}

    combinations = (len(n_estimators) * len(max_features) * len(max_depth) * len(min_samples_split) *
                    len(min_samples_leaf) * len(bootstrap))
    print(f"\n-- Starting RandomizedSearchCV with {combinations} possible combinations. --")

    # Use the random grid to search for best hyperparameters
    rf = RandomForestClassifier()
    rf_random = RandomizedSearchCV(estimator=rf, param_distributions=random_grid, n_iter=n_iter, cv=cv, verbose=0,
                                   random_state=42, n_jobs=-1)

    print(f"--- Fitting {cv} fold for each of {n_iter} candidates, totalling {cv * n_iter} "
          f"fits. This may take some while. ---")
    rf_random.fit(x_train, np.ravel(y_train))

    print("-- Finished RandomizedSearchCV. --")
    rf_params = rf_random.best_params_

    # Random grid for GridSearchCV
    param_grid = {
        'bootstrap': [rf_params["bootstrap"]],
        'max_depth': [int(x) for x in np.linspace(start=rf_params["max_depth"] - 20, stop=rf_params["max_depth"] + 20,
                                                  num=4) if x > 0],
        'max_features': [int(x) for x in np.linspace(start=rf_params["max_features"] - 1,
                                                     stop=rf_params["max_features"] + 1, num=3) if x > 0],
        'min_samples_leaf': [int(x) for x in np.linspace(start=rf_params["min_samples_leaf"] - 1,
                                                         stop=rf_params["min_samples_leaf"] + 1, num=3) if x > 0],
        'min_samples_split': [int(x) for x in np.linspace(start=rf_params["min_samples_split"] - 2,
                                                          stop=rf_params["min_samples_split"] + 2, num=3) if x > 0],
        'n_estimators': [int(x) for x in np.linspace(start=rf_params["n_estimators"] - 1000,
                                                     stop=rf_params["n_estimators"] + 1000, num=4) if x > 0],
    }

    combinations = (len(param_grid["bootstrap"]) * len(param_grid["max_depth"]) * len(param_grid["max_features"]) *
                    len(param_grid["min_samples_leaf"]) * len(param_grid["min_samples_split"]) *
                    len(param_grid["n_estimators"]))
    print(f"\n-- Starting GridSearchCV with {combinations} possible combinations. --")

    # Use the random grid to search for best hyperparameters
    grid_search = GridSearchCV(estimator=rf, param_grid=param_grid,
                               cv=3, n_jobs=-1, verbose=0)

    print(f"--- Fitting {cv} fold for each of {combinations} candidates, totalling {cv * combinations} "
          f"fits. This may take some while. ---")
    grid_search.fit(x_train, np.ravel(y_train))
    print("-- Finished GridSearchCV. Assigned best model as final trained model. --")

    # Final trained model from best grid search model.
    rf = grid_search.best_estimator_
    print_model_params(rf.get_params())
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


def print_model_params(params: dict) -> None:
    print("\n-- The parameters for the final model are: --")
    for key in params:
        print(key + ":", params[key])


if __name__ == "__main__":
    train(n_iter=200, cv=3)
