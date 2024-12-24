import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn import svm
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pandas as pd
import numpy as np
import pickle

df = pd.read_csv("stroke_prediction2.csv")

# Create new columns 'rural' and 'urban' based on 'Residence_type'
df['Rural'] = np.where(df['Residence_type'] == 'Rural', 1, 0)
df['Urban'] = np.where(df['Residence_type'] == 'Urban', 1, 0)

df['Male'] = np.where(df['gender'] == 'Male', 1, 0)
df['Female'] = np.where(df['gender'] == 'Female', 1, 0)

df['Yes'] = np.where(df['ever_married'] == 'Yes', 1, 0)
df['No'] = np.where(df['ever_married'] == 'No', 1, 0)


#work_type (0 for Private, 1 for Self-employed, 2 for children, 3 for Govt_job, 4 for Never_worked)

df['Private'] = np.where(df['work_type'] == 'Private', 1,0)
df['Self-employed'] = np.where(df['work_type'] == 'Self-employed', 1, 0)
df['children'] = np.where(df['work_type'] == 'childern', 1, 0)
df['Govt_job'] = np.where(df['work_type'] == 'Govt_job', 1,0)
df['Never_worked'] = np.where(df['work_type'] == 'Never_worked', 1,0)


#smoking_status (0 for formerly smoked, 1 for never smoked, 2 for smokes)
df['formerly smoked'] = np.where(df['smoking_status'] == 'formerly smoked', 1, 0)
df['never smoked'] = np.where(df['smoking_status'] == 'never smoked', 1, 0)
df['smokes'] = np.where(df['smoking_status'] == 'smokes', 1, 0)

df = df.drop(['gender', 'work_type', 'Residence_type', 'smoking_status', 'ever_married'], axis=1)

# Separate target and features
target = df["stroke"]
train = df.drop("stroke", axis=1)

test_size=0.20
X_train, X_test, Y_train, Y_test = train_test_split(train, target, test_size=test_size, random_state=42)

#logistic regression
logistic_model = LogisticRegression(max_iter=1000, random_state=42)
logistic_model.fit(X_train, Y_train)
y_pred_logistic = logistic_model.predict(X_test)
accuracy_logistic = accuracy_score(Y_test, y_pred_logistic)

#random forest
random_forest_model = RandomForestClassifier(random_state=42)
random_forest_model.fit(X_train, Y_train)
y_pred_rf = random_forest_model.predict(X_test)
accuracy_rf = accuracy_score(Y_test, y_pred_rf)

# SVM
svm_model = svm.SVC(probability=True, random_state=42)

svm_model.fit(X_train, Y_train)
y_pred_svm = svm_model.predict(X_test)
accuracy_svm = accuracy_score(Y_test, y_pred_svm)

# Save the SVM model
filename = 'models/svm_model.sav'
pickle.dump(svm_model, open(filename, 'wb'))