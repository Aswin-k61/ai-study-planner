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
        # ==========================
    # 🛑 INPUT VALIDATION
    # ==========================
    n_subj = len(subjects)
    n_diff = len(difficulty)
    n_scores = len(scores)

    # All lists must be equal length
    if not (n_subj == n_diff == n_scores):
        raise ValueError(
            f"Input length mismatch: subjects={n_subj}, difficulty={n_diff}, scores={n_scores}. "
            "All three must have the same number of values."
        )

    # Difficulty range validation
    if any(d < 1 or d > 10 for d in difficulty):
        raise ValueError("Difficulty values must be between 1 and 10.")

    # Score range validation
    if any(s < 0 or s > 100 for s in scores):
        raise ValueError("Scores must be between 0 and 100.")
    #focus validation(1-10)
    if len(focus) != 3:
        raise ValueError("Focus must contain Morning, Afternoon, and Evening values.")

    # Convert to integers
    try:
        focus = [int(x) for x in focus]
    except:
        raise ValueError("Focus values must be numeric.")

    # Check range 1–10
    if any(f < 1 or f > 10 for f in focus):
        raise ValueError("Focus levels must be between 1 and 10.")


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
    # ☀️ Focus Period Detection (Primary for all, Secondary for some)
    # ==========================
    focus_times = ['Morning', 'Afternoon', 'Night']
    try:

    # Normalize / validate the incoming focus (accepts list of ints or "1,2,3" string)
    
       if isinstance(focus, str):
           focus_vals = [int(x) for x in focus.split(',') if x.strip()]
       else:
           focus_vals = [int(x) for x in list(focus)]
    except Exception:
       focus_vals = [0, 0, 0]

    # Ensure length 3
    if len(focus_vals) != 3:
        focus_vals = (focus_vals + [0, 0, 0])[:3]

     # If all zeros, choose a safe default order (Afternoon then Morning)
    if sum(focus_vals) == 0:
        top_two_idx = [1, 0]  # Afternoon, Morning
    else:
     # Get indices of top two values (sorted highest-first)
        top_two_idx = np.argsort(focus_vals)[-2:]
        top_two_idx = top_two_idx[np.argsort([focus_vals[i] for i in top_two_idx])[::-1]]

    primary_idx, secondary_idx = int(top_two_idx[0]), int(top_two_idx[1])
    primary_time = focus_times[primary_idx]
    secondary_time = focus_times[secondary_idx]

    # Give every subject the primary time
    data['Best Time'] = primary_time

    # Decide how many subjects should get the secondary time:
    # Option: fraction of subjects (e.g., 0.4 means top 40% by Need get secondary).
    secondary_fraction = 0.4
    num_secondary = max(1, int(np.ceil(len(data) * secondary_fraction)))

    # Choose subjects that need it most (by 'Need' column)
    # Make sure 'Need' exists (it does because allocation ran earlier)
    top_need_subjects = data.sort_values('Need', ascending=False).head(num_secondary).index

    # Append secondary time for those subjects
    for idx in top_need_subjects:
    # If someone already has primary (string), update to "Primary, Secondary"
         data.at[idx, 'Best Time'] = f"{primary_time}, {secondary_time}"

    # Replace the original 'focus' variable with normalized list for later use if needed
    focus = focus_vals
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

# Difficulty factor ensures improvement is NEVER negative
            difficulty_factor = max(1, 10 - row['Difficulty'])

       # Improvement formula (positive, realistic)
            improvement = (
               (predicted / 100) *
               difficulty_factor *
               (row['Allocated Hours'] / total_hours) *20
            )

            data.at[i, 'Predicted Score'] = round(min(100, base + improvement), 1)
        else:
            difficulty_factor = max(1, 10 - row['Difficulty'])
            data.at[i, 'Predicted Score'] = round(min(100, base + difficulty_factor * 1.5), 1)
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