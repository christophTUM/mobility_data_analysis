import pandas as pd
from sklearn import tree
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
import pandas as pd
import numpy as np

file = pd.read_csv("data/20211219_01_all_data.csv")
file = file[["modality", "speed_rolling_median"]]

le = preprocessing.LabelEncoder()
le.fit(file["modality"].values)
file["modality_numbers"] = le.transform(file["modality"].values)

X_train, X_test, y_train, y_test = train_test_split(
    file[["speed_rolling_median"]],
    file[["modality_numbers"]],
    test_size=0.3,
    random_state=42,
)


clf = tree.DecisionTreeClassifier()
clf.fit(X=X_train, y=y_train)
#clf.feature_importances_
score = clf.score(X=X_test, y=y_test)
prediction = clf.predict(X_test)

print(score)
print(prediction)
print(y_test)
