from flask import Flask, render_template, request
from planner_model import generate_study_plan

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    subjects = request.form['subjects']
    difficulty = request.form['difficulty']
    scores = request.form['scores']
    total_hours = int(request.form['hours'])
    focus = [int(request.form['morning']), int(request.form['afternoon']), int(request.form['night'])]

    df, suggestions = generate_study_plan(subjects, total_hours, difficulty, scores, focus)

    return render_template(
        'index.html',
        tables=[df.to_html(classes='data', index=False)],
        suggestions=suggestions
    )

if __name__ == '__main__':
    app.run(debug=True)
