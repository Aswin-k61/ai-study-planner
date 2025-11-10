import pandas as pd
import numpy as np
import joblib
import os

MODEL_PATHS = {
    "Math": "models/math_model.pkl",
    "Reading": "models/reading_model.pkl",
    "Writing": "models/writing_model.pkl"
}

# Load trained models
models = {}
for key, path in MODEL_PATHS.items():
    if os.path.exists(path):
        models[key] = joblib.load(path)


def generate_study_plan(subjects_str, total_hours, difficulty_str, scores_str, focus):
    subjects = [s.strip().capitalize() for s in subjects_str.split(',')]
    difficulty = [int(x) for x in difficulty_str.split(',')]
    scores = [int(x) for x in scores_str.split(',')]

    data = pd.DataFrame({
        'Subject': subjects,
        'Difficulty': difficulty,
         'Current Score': scores  
    })

    # ==========================
    # 🎯 Allocate Study Hours
    # ==========================
    data['Need'] = (100 - data['Current Score']) * data['Difficulty'] 
    data['Weight'] = data['Need'] / data['Need'].sum()
    data['Allocated Hours'] = (data['Weight'] * total_hours).round(1)

    # ==========================
    # ☀️ Focus Period Detection
    # ==========================
    focus_times = ['Morning', 'Afternoon', 'Night']
    best_focus_time = focus_times[np.argmax(focus)]
    data['Best Time'] = best_focus_time

    # ==========================
    # 🤖 Predict Improvement
    # ==========================
    data['Predicted Score'] = np.nan

    for i, row in data.iterrows():
        subj = row['Subject']
        base = row['Current Score'] 

        # Choose correct model by subject name
        matched_key = None
        for k in models.keys():
            if k.lower() in subj.lower():
                matched_key = k
                break

        if matched_key:
            model = models[matched_key]

            # Build a meaningful feature vector
            # You can tune these numbers to simulate realistic variations
            sample_input = np.array([
                [
                    np.random.randint(0, 2),
                    np.random.randint(0, 5),
                    np.random.randint(0, 6),
                    np.random.randint(0, 2),
                    np.random.randint(0, 2)
                ]
            ])
            predicted = model.predict(sample_input)[0]

            # Scale improvement using difficulty and hours
            improvement = ((predicted / 100) * (6 - row['Difficulty']) * (row['Allocated Hours'] / total_hours) * 15)
            data.at[i, 'Predicted Score'] = round(min(100, base + improvement), 1)
        else:
            data.at[i, 'Predicted Score'] = round(base + (6 - row['Difficulty']) * 1.5, 1)

    # 💡 Suggestions
    suggestions = []
    avg_score = data['Current Score'].mean()
    weak_subjects = data[data['Current Score'] < avg_score]['Subject'].tolist()
    strong_subjects = data[data['Current Score'] >= avg_score]['Subject'].tolist()

    if weak_subjects:
        suggestions.append(f"⚠️ Focus more on {', '.join(weak_subjects)} — below your average.")
    if strong_subjects:
        suggestions.append(f"💪 Revise {', '.join(strong_subjects)} weekly to retain strengths.")
    if total_hours < 10:
        suggestions.append("⏰ Try increasing total study time for consistent results.")
    if np.argmax(focus) == 0:
        suggestions.append("🌅 Morning focus — schedule tough subjects early.")
    elif np.argmax(focus) == 2:
        suggestions.append("🌙 Night focus — ideal for revision sessions.")
    suggestions.append("📖 End each week with a 1-hour summary session.")

    # 🟩 CHANGE 2: Returning “Current Score” column for comparison
    return data[['Subject', 'Difficulty', 'Allocated Hours', 'Best Time', 'Current Score', 'Predicted Score']], suggestions