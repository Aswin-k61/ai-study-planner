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

    focus = [
        int(request.form.get('morning', 0)),
        int(request.form.get('afternoon', 0)),
        int(request.form.get('night', 0))
    ]

    try:
        df, suggestions = generate_study_plan(subjects, total_hours, difficulty, scores, focus)

        return render_template(
            'index.html',
            tables=[df.to_html(classes='data', index=False)],
            suggestions=suggestions,
            error=None
        )

    except ValueError as e:
        return render_template('index.html', error=str(e))

    except Exception as e:
        print("Unexpected error:", e)
        return render_template('index.html', error="Something went wrong. Try again.")


if __name__ == '__main__':
    app.run(debug=True)
