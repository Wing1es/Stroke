import pickle
import pandas as pd
import sys
import json

# Load the saved SVM model
filename = 'models/svm_model.sav'
loaded_model = pickle.load(open(filename, 'rb'))

# Read the input data from stdin
input_data = json.loads(sys.stdin.read())

# Convert the input data into a pandas DataFrame (ensure columns match the model's training data)
new_data = pd.DataFrame({
    'age': [input_data['age']],
    'hypertension': [input_data['hypertension']],
    'heart_disease': [input_data['heart_disease']],
    'avg_glucose_level': [input_data['avg_glucose_level']],
    'bmi': [input_data['bmi']],
    'Rural': [input_data['Rural']],
    'Urban': [input_data['Urban']],
    'Male': [input_data['Male']],
    'Female': [input_data['Female']],
    'Yes': [input_data['Yes']],
    'No': [input_data['No']],
    'Private': [input_data['Private']],
    'Self-employed': [input_data['Self_employed']],
    'children': [input_data['children']],
    'Govt_job': [input_data['Govt_job']],
    'Never_worked': [input_data['Never_worked']],
    'formerly smoked': [input_data['formerly_smoked']],
    'never smoked': [input_data['never_smoked']],
    'smokes': [input_data['smokes']]
})

# Make predictions
predictions = loaded_model.predict(new_data)
probabilities = loaded_model.predict_proba(new_data)
average_probability = probabilities[0][1]

if average_probability < 0.3:
    rainbow_level = "Low Risk"
elif average_probability < 0.6:
    rainbow_level = "Moderate Risk"
elif average_probability < 0.8:
    rainbow_level = "High Risk"
else:
    rainbow_level = "Very High Risk"

result = {
    "average_probability": average_probability,
    "percentage_risk": average_probability * 100,
    "rainbow_level": rainbow_level
}

# Output the result as JSON
print(json.dumps(result))
