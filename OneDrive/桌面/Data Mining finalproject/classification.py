from dataset import GeneDataset
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import numpy as np
def classifier_controller(name):
    name = name.lower()
    if name == "svm":
        return SVC(kernel="linear", probability=True, C=1.0, random_state=40)
    elif name == "logreg":
        return LogisticRegression(max_iter=5000, solver="lbfgs", penalty="l2", C=1.0, n_jobs=-1)
    elif name == "rf":
        return RandomForestClassifier(n_estimators=300, max_depth=None, n_jobs=-1, random_state=40)
    
def train_and_evaluation(model_name="svm", var_threshold=0.0, cv=5):
    ds = GeneDataset(var_threshold=var_threshold)
    x_train, y_train = ds.get_train()
    X_test, y_test = ds.get_test()
    
    clf = classifier_controller(model_name)
    scores = cross_val_score(clf, x_train, y_train, cv=cv, scoring="accuracy") # baseline score(only in train data)
    print(f"[{model_name}] CV acc = {scores.mean():.4f} ± {scores.std():.4f}")

    clf.fit(x_train, y_train)
    y_pred = clf.predict(X_test)
    acc  = accuracy_score(y_test, y_pred)
    print("\nTest Classification Report:")
    print(f"[{model_name}] Test overall accuracy = {acc:.4f}\n")
    print(classification_report(y_test, y_pred))
    print(confusion_matrix(y_test, y_pred))
    return clf

if __name__ == "__main__":
    for name in ["svm", "logreg", "rf"]:
        print("="*60)
        print(name+':')
        train_and_evaluation(model_name=name, var_threshold=0.0)