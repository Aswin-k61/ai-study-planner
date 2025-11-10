import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import joblib
import os

# Load dataset
df = pd.read_csv("datasets/StudentsPerformance.csv")

# Encode categorical columns
le = LabelEncoder()
for col in ['gender', 'race/ethnicity', 'parental level of education', 'lunch', 'test preparation course']:
    df[col] = le.fit_transform(df[col])

# Input features
X = df[['gender', 'race/ethnicity', 'parental level of education', 'lunch', 'test preparation course']]

# Targets
targets = {
    "math": "math score",
    "reading": "reading score",
    "writing": "writing score"
}

# Create folder
os.makedirs("models", exist_ok=True)

for name, target in targets.items():
    y = df[target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LinearRegression()
    model.fit(X_train, y_train)
    joblib.dump(model, f"models/{name}_model.pkl")
    print(f"✅ {name.capitalize()} model trained and saved successfully!")

print("🎓 All subject models ready!")
