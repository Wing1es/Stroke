import sys
import json
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Load the dataset
def load_and_preprocess_data(file_path):
    df = pd.read_csv(file_path)

    # Encode binary columns
    binary_cols = ['gender', 'ever_married', 'Residence_type']
    label_encoder = LabelEncoder()
    for col in binary_cols:
        df[col] = label_encoder.fit_transform(df[col])

    # Encode multi-class columns
    multi_cols = ['work_type', 'smoking_status']
    df = pd.get_dummies(df, columns=multi_cols, drop_first=True)

    # Separate features and target
    X = df.drop('stroke', axis=1)
    y = df['stroke']
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    # Scale numerical features
    scaler = StandardScaler()
    numerical_features = ['avg_glucose_level', 'bmi']
    X_train[numerical_features] = scaler.fit_transform(X_train[numerical_features])
    X_test[numerical_features] = scaler.transform(X_test[numerical_features])

    return X_train, X_test, y_train, y_test, scaler, X.columns

# Train models
def train_models(X_train, y_train):
    logistic_model = LogisticRegression(max_iter=1000, random_state=42)
    logistic_model.fit(X_train, y_train)

    random_forest_model = RandomForestClassifier(random_state=42)
    random_forest_model.fit(X_train, y_train)

    svm_model = SVC(probability=True, random_state=42)
    svm_model.fit(X_train, y_train)

    return logistic_model, random_forest_model, svm_model

# Function to predict stroke risk
def predict_stroke(input_data, models, scaler, feature_columns):
    logistic_model, random_forest_model, svm_model = models

    # Convert input data to a DataFrame
    input_df = pd.DataFrame([input_data], columns=[ 
        "age", "gender", "ever_married", "Residence_type", 
        "avg_glucose_level", "bmi", "work_type", "smoking_status"
    ])

    # Ensure all columns from the training set are present in input
    for col in feature_columns:
        if col not in input_df:
            input_df[col] = 0

    # Apply the same encoding as during training (one-hot encoding)
    multi_cols = ['work_type', 'smoking_status']
    input_df = pd.get_dummies(input_df, columns=multi_cols, drop_first=True)

    # Ensure that input_df has the same feature columns as the training data
    input_df = input_df.reindex(columns=feature_columns, fill_value=0)

    # Scale numerical features
    numerical_features = ['avg_glucose_level', 'bmi']
    input_df[numerical_features] = scaler.transform(input_df[numerical_features])

    # Predict probabilities from all models
    probability_rf = random_forest_model.predict_proba(input_df)[0][1]
    probability_logistic = logistic_model.predict_proba(input_df)[0][1]
    probability_svm = svm_model.predict_proba(input_df)[0][1]

    # Calculate average probability
    average_probability = (probability_rf + probability_logistic + probability_svm) / 3

    # Calculate percentage risk
    percentage_risk = average_probability * 100

    # Rainbow level based on the probability
    if average_probability < 0.2:
        rainbow_level = "Red (Very Low Risk)"
    elif average_probability < 0.3:
        rainbow_level = "Orange (Low Risk)"
    elif average_probability < 0.4:
        rainbow_level = "Yellow (Moderate Risk)"
    elif average_probability < 0.6:
        rainbow_level = "Green (Moderate-High Risk)"
    elif average_probability < 0.9:
        rainbow_level = "Blue (High Risk)"
    else:
        rainbow_level = "Violet (Very High Risk)"

    # Return the result with both average probability and percentage risk
    result = {
        "average_probability": average_probability,
        "percentage_risk": percentage_risk,  # Add the risk percentage
        "rainbow_level": rainbow_level
    }
    
    # Return the result
    return result


# Main execution
if __name__ == "__main__":
    try:
        # Load and preprocess data
        X_train, X_test, y_train, y_test, scaler, feature_columns = load_and_preprocess_data("stroke_prediction2.csv")

        # Train models
        models = train_models(X_train, y_train)

        # Read JSON input
        input_data = json.load(sys.stdin)

        # Ensure input matches required structure
        formatted_input = [
            input_data["age"],
            input_data["gender"],
            input_data["ever_married"],
            input_data["Residence_type"],
            input_data["avg_glucose_level"],
            input_data["bmi"],
            input_data["work_type"],
            input_data["smoking_status"]
        ]

        # Predict stroke risk
        result = predict_stroke(formatted_input, models, scaler, feature_columns)

        # Output the result as JSON
        print(json.dumps(result))

    except Exception as e:
        # Catch any errors and print them as JSON to stderr
        error_message = {"error": str(e)}
        print(json.dumps(error_message), file=sys.stderr)
