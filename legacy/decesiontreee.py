import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
from sklearn.tree import DecisionTreeClassifier, export_graphviz
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from graphviz import Source
import numpy as np
import pandas as pd

# Load the dataset
heartdata = pd.read_csv("heart.csv")

# Define features and target
X = heartdata.drop(columns='target')
y = heartdata['target']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=2)

# Define a function to train and evaluate a model
def train_and_evaluate(model, X_train, X_test, y_train, y_test):
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    return accuracy, f1, cm

# Define a function to visualize a decision tree
def visualize_decision_tree(model, X):
    dot_data = export_graphviz(model, out_file=None, feature_names=X.columns, class_names=['0', '1'], filled=True, rounded=True, special_characters=True)
    graph = Source(dot_data)
    plt.figure(figsize=(15,10))
    plt.axis('off')
    plt.imshow(graph.render(format='png'))
    plt.show()

# Define a pipeline with a decision tree classifier and hyperparameter tuning
dt_pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('dt', DecisionTreeClassifier())
])

dt_param_grid = {
    'dt__max_depth': [3, 5, 10],
    'dt__min_samples_split': [2, 5, 10],
    'dt__min_samples_leaf': [1, 5, 10]
}

dt_grid_search = GridSearchCV(dt_pipeline, dt_param_grid, cv=5, scoring='f1_macro')
dt_grid_search.fit(X_train, y_train)

# Train and evaluate a decision tree classifier
dt = DecisionTreeClassifier(**dt_grid_search.best_params_)
accuracy_dt, f1_dt, cm_dt = train_and_evaluate(dt, X_train, X_test, y_train, y_test)
print("Decision Tree accuracy:", accuracy_dt)
print("Decision Tree F1 score:", f1_dt)
print("Decision Tree confusion matrix:")
print(cm_dt)

# Visualize the decision tree
visualize_decision_tree(dt, X)

# Define a pipeline with a random forest classifier and hyperparameter tuning
rf_pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('rf', RandomForestClassifier())
])

rf_param_grid = {
    'rf__n_estimators': [10, 50, 100],
    'rf__max_depth': [3, 5, 10],
    'rf__min_samples_split': [2, 5, 10],
    'rf__min_samples_leaf': [1, 5, 10]
}

rf_grid_search = GridSearchCV(rf_pipeline, rf_param_grid, cv=5, scoring='f1_macro')
rf_grid_search.fit(X_train, y_train)

# Train and evaluate a random forest classifier
rf = RandomForestClassifier(**rf_grid_search.best_params_)
accuracy_rf, f1_rf, cm_rf = train_and_evaluate(rf, X_train, X_test, y_train, y_test)
print("Random Forest accuracy:", accuracy_rf)
print("Random Forest F1 score:", f1_rf)
print("Random Forest confusion matrix:")
print(cm_rf)

# Define a pipeline with a logistic regression model and hyperparameter tuning
lr_pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('lr', LogisticRegression())
])

lr_param_grid = {
    'lr__C': [0.1, 1, 10],
    'lr__penalty': ['l1', 'l2']
}

lr_grid_search = GridSearchCV(lr_pipeline, lr_param_grid, cv=5, scoring='f1_macro')
lr_grid_search.fit(X_train, y_train)

# Train and evaluate a logistic regression model
lr = LogisticRegression(**lr_grid_search.best_params_)
accuracy_lr, f1_lr, cm_lr = train_and_evaluate(lr, X_train, X_test, y_train, y_test)
print("Logistic Regression accuracy:", accuracy_lr)
print("Logistic Regression F1 score:", f1_lr)
print("Logistic Regression confusion matrix:")
print(cm_lr)

# Plot the ROC curve for the models
y_pred_dt_proba = dt.predict_proba(X_test)[:, 1]
y_pred_rf_proba = rf.predict_proba(X_test)[:, 1]
y_pred_lr_proba = lr.predict_proba(X_test)[:, 1]

from sklearn.metrics import roc_auc_score, roc_curve

auc_dt = roc_auc_score(y_test, y_pred_dt_proba)
auc_rf = roc_auc_score(y_test, y_pred_rf_proba)
auc_lr = roc_auc_score(y_test, y_pred_lr_proba)

fpr_dt, tpr_dt, _ = roc_curve(y_test, y_pred_dt_proba)
fpr_rf, tpr_rf, _ = roc_curve(y_test, y_pred_rf_proba)
fpr_lr, tpr_lr, _ = roc_curve(y_test, y_pred_lr_proba)

plt.figure(figsize=(10, 8))
plt.plot(fpr_dt, tpr_dt, label='Decision Tree (AUC = {:.3f})'.format(auc_dt))
plt.plot(fpr_rf, tpr_rf, label='Random Forest (AUC = {:.3f})'.format(auc_rf))
plt.plot(fpr_lr, tpr_lr, label='Logistic Regression (AUC = {:.3f})'.format(auc_lr))
plt.plot([0, 1], [0, 1], 'k--')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve')
plt.legend()
plt.show()# Define a function to train and evaluate a model
def train_and_evaluate(model, X_train, X_test, y_train, y_test):
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    return accuracy, f1, cm

# Define a function to visualize a decision tree
def visualize_decision_tree(model, X):
    dot_data = export_graphviz(model, out_file=None, feature_names=X.columns, class_names=['0', '1'], filled=True, rounded=True, special_characters=True)
    graph = Source(dot_data)
    plt.figure(figsize=(15,10))
    plt.axis('off')
    plt.imshow(graph.render(format='png'))
    plt.show()

# Train and evaluate a decision tree classifier
dt = DecisionTreeClassifier()
accuracy_dt, f1_dt, cm_dt = train_and_evaluate(dt, X_train, X_test, y_train, y_test)
print("Decision Tree accuracy:", accuracy_dt)
print("Decision Tree F1 score:", f1_dt)
print("Decision Tree confusion matrix:")
print(cm_dt)

# Visualize the decision tree
visualize_decision_tree(dt, X)

# Train and evaluate a random forest classifier
rf = RandomForestClassifier()
accuracy_rf, f1_rf, cm_rf = train_and_evaluate(rf, X_train, X_test, y_train, y_test)
print("Random Forest accuracy:", accuracy_rf)
print("Random Forest F1 score:", f1_rf)
print("Random Forest confusion matrix:")
print(cm_rf)

# Train and evaluate a logistic regression model
lr = LogisticRegression()
accuracy_lr, f1_lr, cm_lr = train_and_evaluate(lr, X_train, X_test, y_train, y_test)
print("Logistic Regression accuracy:", accuracy_lr)
print("Logistic Regression F1 score:", f1_lr)
print("Logistic Regression confusion matrix:")
print(cm_lr)
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
from sklearn.tree import DecisionTreeClassifier, export_graphviz
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from graphviz import Source

# Load the dataset
heartdata = pd.read_csv("heart.csv")

# Define features and target
X = heartdata.drop(columns='target')
y = heartdata['target']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=2)

# Initialize and train a Decision Tree Classifier
dt = DecisionTreeClassifier()
dt.fit(X_train, y_train)

# Make predictions and evaluate the model
y_pred_dt = dt.predict(X_test)
acc_dt = accuracy_score(y_test, y_pred_dt)
f1_dt = f1_score(y_test, y_pred_dt)
cm_dt = confusion_matrix(y_test, y_pred_dt)

# Print the evaluation metrics
print("Decision Tree accuracy:", acc_dt)
print("Decision Tree F1 score:", f1_dt)
print("Decision Tree confusion matrix:")
print(cm_dt)

# Visualize the Decision Tree
dot_data = export_graphviz(dt, out_file=None, feature_names=X.columns, class_names=['0', '1'], filled=True, rounded=True, special_characters=True)
graph = Source(dot_data)

# Display the Decision Tree
plt.figure(figsize=(15,10))
plt.axis('off')
plt.imshow(graph.render(format='png'))
plt.show()# Define a function to train and evaluate a model
def train_and_evaluate(model, X_train, X_test, y_train, y_test):
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    return accuracy, f1, cm

# Define a function to visualize a decision tree
def visualize_decision_tree(model, X):
    dot_data = export_graphviz(model, out_file=None, feature_names=X.columns, class_names=['0', '1'], filled=True, rounded=True, special_characters=True)
    graph = Source(dot_data)
    plt.figure(figsize=(15,10))
    plt.axis('off')
    plt.imshow(graph.render(format='png'))
    plt.show()

# Train and evaluate a decision tree classifier
dt = DecisionTreeClassifier()
accuracy_dt, f1_dt, cm_dt = train_and_evaluate(dt, X_train, X_test, y_train, y_test)
print("Decision Tree accuracy:", accuracy_dt)
print("Decision Tree F1 score:", f1_dt)
print("Decision Tree confusion matrix:")
print(cm_dt)

# Visualize the decision tree
visualize_decision_tree(dt, X)

# Train and evaluate a random forest classifier
rf = RandomForestClassifier()
accuracy_rf, f1_rf, cm_rf = train_and_evaluate(rf, X_train, X_test, y_train, y_test)
print("Random Forest accuracy:", accuracy_rf)
print("Random Forest F1 score:", f1_rf)
print("Random Forest confusion matrix:")
print(cm_rf)

# Train and evaluate a logistic regression model
lr = LogisticRegression()
accuracy_lr, f1_lr, cm_lr = train_and_evaluate(lr, X_train, X_test, y_train, y_test)
print("Logistic Regression accuracy:", accuracy_lr)
print("Logistic Regression F1 score:", f1_lr)
print("Logistic Regression confusion matrix:")
print(cm_lr)# Define a function to train and evaluate a model
def train_and_evaluate(model, X_train, X_test, y_train, y_test):
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    return accuracy, f1, cm

# Define a function to visualize a decision tree
def visualize_decision_tree(model, X):
    dot_data = export_graphviz(model, out_file=None, feature_names=X.columns, class_names=['0', '1'], filled=True, rounded=True, special_characters=True)
    graph = Source(dot_data)
    plt.figure(figsize=(15,10))
    plt.axis('off')
    plt.imshow(graph.render(format='png'))
    plt.show()

# Train and evaluate a decision tree classifier
dt = DecisionTreeClassifier()
accuracy_dt, f1_dt, cm_dt = train_and_evaluate(dt, X_train, X_test, y_train, y_test)
print("Decision Tree accuracy:", accuracy_dt)
print("Decision Tree F1 score:", f1_dt)
print("Decision Tree confusion matrix:")
print(cm_dt)

# Visualize the decision tree
visualize_decision_tree(dt, X)

# Train and evaluate a random forest classifier
rf = RandomForestClassifier()
accuracy_rf, f1_rf, cm_rf = train_and_evaluate(rf, X_train, X_test, y_train, y_test)
print("Random Forest accuracy:", accuracy_rf)
print("Random Forest F1 score:", f1_rf)
print("Random Forest confusion matrix:")
print(cm_rf)

# Train and evaluate a logistic regression model
lr = LogisticRegression()
accuracy_lr, f1_lr, cm_lr = train_and_evaluate(lr, X_train, X_test, y_train, y_test)
print("Logistic Regression accuracy:", accuracy_lr)
print("Logistic Regression F1 score:", f1_lr)
print("Logistic Regression confusion matrix:")
print(cm_lr)
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
from sklearn.tree import DecisionTreeClassifier, export_graphviz
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from graphviz import Source
import numpy as np
import pandas as pd

# Load the dataset
heartdata = pd.read_csv("heart.csv")

# Define features and target
X = heartdata.drop(columns='target')
y = heartdata['target']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=2)

# Define a function to train and evaluate a model
def train_and_evaluate(model, X_train, X_test, y_train, y_test):
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    return accuracy, f1, cm

# Define a function to visualize a decision tree
def visualize_decision_tree(model, X):
    dot_data = export_graphviz(model, out_file=None, feature_names=X.columns, class_names=['0', '1'], filled=True, rounded=True, special_characters=True)
    graph = Source(dot_data)
    plt.figure(figsize=(15,10))
    plt.axis('off')
    plt.imshow(graph.render(format='png'))
    plt.show()

# Define a pipeline with a decision tree classifier and hyperparameter tuning
dt_pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('dt', DecisionTreeClassifier())
])

dt_param_grid = {
    'dt__max_depth': [3, 5, 10],
    'dt__min_samples_split': [2, 5, 10],
    'dt__min_samples_leaf': [1, 5, 10]
}

dt_grid_search = GridSearchCV(dt_pipeline, dt_param_grid, cv=5, scoring='f1_macro')
dt_grid_search.fit(X_train, y_train)

# Train and evaluate a decision tree classifier
dt = DecisionTreeClassifier(**dt_grid_search.best_params_)
accuracy_dt, f1_dt, cm_dt = train_and_evaluate(dt, X_train, X_test, y_train, y_test)
print("Decision Tree accuracy:", accuracy_dt)
print("Decision Tree F1 score:", f1_dt)
print("Decision Tree confusion matrix:")
print(cm_dt)

# Visualize the decision tree
visualize_decision_tree(dt, X)

# Define a pipeline with a random forest classifier and hyperparameter tuning
rf_pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('rf', RandomForestClassifier())
])

rf_param_grid = {
    'rf__n_estimators': [10, 50, 100],
    'rf__max_depth': [3, 5, 10],
    'rf__min_samples_split': [2, 5, 10],
    'rf__min_samples_leaf': [1, 5, 10]
}

rf_grid_search = GridSearchCV(rf_pipeline, rf_param_grid, cv=5, scoring='f1_macro')
rf_grid_search.fit(X_train, y_train)

# Train and evaluate a random forest classifier
rf = RandomForestClassifier(**rf_grid_search.best_params_)
accuracy_rf, f1_rf, cm_rf = train_and_evaluate(rf, X_train, X_test, y_train, y_test)
print("Random Forest accuracy:", accuracy_rf)
print("Random Forest F1 score:", f1_rf)
print("Random Forest confusion matrix:")
print(cm_rf)

# Define a pipeline with a logistic regression model and hyperparameter tuning
lr_pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('lr', LogisticRegression())
])

lr_param_grid = {
    'lr__C': [0.1, 1, 10],
    'lr__penalty': ['l1', 'l2']
}

lr_grid_search = GridSearchCV(lr_pipeline, lr_param_grid, cv=5, scoring='f1_macro')
lr_grid_search.fit(X_train, y_train)

# Train and evaluate a logistic regression model
lr = LogisticRegression(**lr_grid_search.best_params_)
accuracy_lr, f1_lr, cm_lr = train_and_evaluate(lr, X_train, X_test, y_train, y_test)
print("Logistic Regression accuracy:", accuracy_lr)
print("Logistic Regression F1 score:", f1_lr)
print("Logistic Regression confusion matrix:")
print(cm_lr)
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
from sklearn.tree import DecisionTreeClassifier, export_graphviz
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report
from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve
import matplotlib.pyplot as plt
from graphviz import Source
import numpy as np
import pandas as pd

# Load the dataset
heartdata = pd.read_csv("heart.csv")

# Define features and target
X = heartdata.drop(columns='target')
y = heartdata['target']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=2)

# Define a function to train and evaluate a model
def train_and_evaluate(model, X_train, X_test, y_train, y_test):
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    return accuracy, f1, cm

# Define a function to visualize a decision tree
def visualize_decision_tree(model, X):
    dot_data = export_graphviz(model, out_file=None, feature_names=X.columns, class_names=['0', '1'], filled=True, rounded=True, special_characters=True)
    graph = Source(dot_data)
    plt.figure(figsize=(15,10))
    plt.axis('off')
    plt.imshow(graph.render(format='png'))
    plt.show()

# Define a function to perform hyperparameter tuning
def hyperparameter_tuning(model, X_train, y_train, param_grid):
    grid_search = GridSearchCV(model, param_grid, cv=5, scoring='f1_macro')
    grid_search.fit(X_train, y_train)
    return grid_search.best_params_, grid_search.best_score_

# Train and evaluate a decision tree classifier
dt = DecisionTreeClassifier()
accuracy_dt, f1_dt, cm_dt = train_and_evaluate(dt, X_train, X_test, y_train, y_test)
print("Decision Tree accuracy:", accuracy_dt)
print("Decision Tree F1 score:", f1_dt)
print("Decision Tree confusion matrix:")
print(cm_dt)

# Visualize the decision tree
visualize_decision_tree(dt, X)

# Perform hyperparameter tuning for the decision tree classifier
param_grid_dt = {'max_depth': [3, 5, 10], 'min_samples_split': [2, 5, 10]}
best_params_dt, best_score_dt = hyperparameter_tuning(dt, X_train, y_train, param_grid_dt)
print("Best parameters for Decision Tree:", best_params_dt)
print("Best score for Decision Tree:", best_score_dt)

# Train and evaluate a random forest classifier
rf = RandomForestClassifier()
accuracy_rf, f1_rf, cm_rf = train_and_evaluate(rf, X_train, X_test, y_train, y_test)
print("Random Forest accuracy:", accuracy_rf)
print("Random Forest F1 score:", f1_rf)
print("Random Forest confusion matrix:")
print(cm_rf)

# Perform hyperparameter tuning for the random forest classifier
param_grid_rf = {'n_estimators': [10, 50, 100], 'max_depth': [3, 5, 10]}
best_params_rf, best_score_rf = hyperparameter_tuning(rf, X_train, y_train, param_grid_rf)
print("Best parameters for Random Forest:", best_params_rf)
print("Best score for Random Forest:", best_score_rf)

# Train and evaluate a logistic regression model
lr = LogisticRegression()
accuracy_lr, f1_lr, cm_lr = train_and_evaluate(lr, X_train, X_test, y_train, y_test)
print("Logistic Regression accuracy:", accuracy_lr)
print("Logistic Regression F1 score:", f1_lr)
print("Logistic Regression confusion matrix:")
print(cm_lr)

# Perform hyperparameter tuning for the logistic regression model
param_grid_lr = {'C': [0.1, 1, 10]}
best_params_lr, best_score_lr = hyperparameter_tuning(lr, X_train, y_train, param_grid_lr)
print("Best parameters for Logistic Regression:", best_params_lr)
print("Best score for Logistic Regression:", best_score_lr)

# Plot the ROC curve for the models
y_pred_dt_proba = dt.predict_proba(X_test)[:, 1]
y_pred_rf_proba = rf.predict_proba(X_test)[:, 1]
y_pred_lr_proba = lr.predict_proba(X_test)[:, 1]

fpr_dt, tpr_dt, _ = roc_curve(y_test, y_pred_dt_proba)
fpr_rf, tpr_rf, _ = roc_curve(y_test, y_pred_rf_proba)
fpr_lr, tpr_lr, _ = roc_curve(y_test, y_pred_lr_proba)

plt.figure(figsize=(10, 8))
plt.plot(fpr_dt, tpr_dt, label='Decision Tree')
plt.plot(fpr_rf, tpr_rf, label='Random Forest')
plt.plot(fpr_lr, tpr_lr, label='Logistic Regression')
plt.plot([0, 1], [0, 1], 'k--')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve')
plt.legend()
plt.show()
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
from sklearn.tree import DecisionTreeClassifier, export_graphviz
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from graphviz import Source
import numpy as np
import pandas as pd

# Load the dataset
heartdata = pd.read_csv("heart.csv")

# Define features and target
X = heartdata.drop(columns='target')
y = heartdata['target']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=2)

# Define a function to train and evaluate a model
def train_and_evaluate(model, X_train, X_test, y_train, y_test):
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    return accuracy, f1, cm

# Define a function to visualize a decision tree
def visualize_decision_tree(model, X):
    dot_data = export_graphviz(model, out_file=None, feature_names=X.columns, class_names=['0', '1'], filled=True, rounded=True, special_characters=True)
    graph = Source(dot_data)
    plt.figure(figsize=(15,10))
    plt.axis('off')
    plt.imshow(graph.render(format='png'))
    plt.show()

# Train and evaluate a decision tree classifier
dt = DecisionTreeClassifier()
accuracy_dt, f1_dt, cm_dt = train_and_evaluate(dt, X_train, X_test, y_train, y_test)
print("Decision Tree accuracy:", accuracy_dt)
print("Decision Tree F1 score:", f1_dt)
print("Decision Tree confusion matrix:")
print(cm_dt)

# Visualize the decision tree
visualize_decision_tree(dt, X)

# Train and evaluate a random forest classifier
rf = RandomForestClassifier()
accuracy_rf, f1_rf, cm_rf = train_and_evaluate(rf, X_train, X_test, y_train, y_test)
print("Random Forest accuracy:", accuracy_rf)
print("Random Forest F1 score:", f1_rf)
print("Random Forest confusion matrix:")
print(cm_rf)

# Train and evaluate a logistic regression model
lr = LogisticRegression()
accuracy_lr, f1_lr, cm_lr = train_and_evaluate(lr, X_train, X_test, y_train, y_test)
print("Logistic Regression accuracy:", accuracy_lr)
print("Logistic Regression F1 score:", f1_lr)
print("Logistic Regression confusion matrix:")
print(cm_lr)
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression

heartdata = pd.read_csv("heart.csv")

X = heartdata.drop(columns='target')
y = heartdata['target']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=2)

dt = DecisionTreeClassifier()
dt.fit(X_train, y_train)

y_pred_dt = dt.predict(X_test)
acc_dt = accuracy_score(y_test, y_pred_dt)
print("Decision Tree accuracy:", acc_dt)

from sklearn.metrics import f1_score, confusion_matrix

f1_dt = f1_score(y_test, y_pred_dt)
print("Decision Tree F1 score:", f1_dt)

cm_dt = confusion_matrix(y_test, y_pred_dt)
print("Decision Tree confusion matrix:")
print(cm_dt)

from sklearn.tree import export_graphviz
from graphviz import Source
import matplotlib.pyplot as plt

dot_data = export_graphviz(dt, out_file=None, feature_names=X.columns, class_names=['0', '1'], filled=True, rounded=True, special_characters=True)
graph = Source(dot_data)

plt.figure(figsize=(15,10))
plt.axis('off')
plt.imshow(graph.render(format='png'))
plt.show()
