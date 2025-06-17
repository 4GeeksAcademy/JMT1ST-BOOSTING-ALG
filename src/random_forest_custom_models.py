# Imports
import pandas as pd 
import numpy as np 
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.tree import DecisionTreeClassifier
from collections import Counter
import numpy as np
from sklearn.metrics import *
import pandas as pd
from numpy.random import choice, seed
from imblearn.metrics import specificity_score
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os 


class RandomForestBootstrap:

    def __init__(self, n_estimators, random_state, max_depth, min_samples_leaf, max_features, X, y):
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.max_depth = max_depth
        self.min_samples_leaf = min_samples_leaf
        self.max_features = max_features
        self.X = X
        self.y = y
        self.estimators = []

    def get_bootstrap_datasets(self):
        seed(self.random_state)

        idxs = [choice(len(self.X), len(self.X), replace=True) for _ in range(self.n_estimators)]
        feature_idxs = [choice(self.X.shape[1], self.max_features, replace=False) for _ in range(self.n_estimators)]

        return feature_idxs, [
            (self.X[idxs[i], :][:, feature_idxs[i]], self.y[idxs[i]])
            for i in range(self.n_estimators)
        ]

    def fit(self):
        feature_idxs, data_sets = self.get_bootstrap_datasets()

        for i, data in enumerate(data_sets):
            X, y = data
            tree = DecisionTreeClassifier(
                max_depth=self.max_depth,
                min_samples_leaf=self.min_samples_leaf,
                max_features=self.max_features,
                random_state=self.random_state
            ).fit(X, y)
            self.estimators.append((feature_idxs[i], tree))

    def predict(self, X):
        if isinstance(X, np.ndarray):
            X_df = pd.DataFrame(X)
        else:
            X_df = X.copy()

        predictions = np.vstack([
            model.predict(X_df.iloc[:, feature_idxs])
            for feature_idxs, model in self.estimators
        ])

        majority_votes = [
            Counter(predictions[:, i]).most_common(1)[0][0]
            for i in range(predictions.shape[1])
        ]

        return majority_votes