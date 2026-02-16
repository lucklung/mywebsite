from flask import Flask, render_template, request
from google import genai
import json
import re

app = Flask(__name__)

# Securely load API key from file
with open("apikey.txt", "r") as f:
    api_key = f.read().strip()

client = genai.Client(api_key=api_key)

# Jinja2 filter for color styling
@app.template_filter('get_color_class')
def get_color_class(score):
    try:
        score = int(score)
    except:
        return 'bg-secondary'
    if score <= 5:
        return 'bg-danger'
    elif score <= 10:
        return 'bg-warning'
    elif score <= 15:
        return 'bg-info'
    else:
        return 'bg-success'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/blogs')
def blogs():
    return render_template('blogs.html')    

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/fun')
def fun():
    return render_template('fun.html')

@app.route('/students')
def students():
    return render_template('students.html')

@app.route('/teachers')
def teachers():
    return render_template('teachers.html')

@app.route('/yeah')
def yeah():
    return render_template('yeah.html')

@app.route('/aimirror')
def aimirror():
    placeholder_scores = {
        "purpose_intent": "--",
        "autonomy_integrity": "--",
        "social_impact_harm": "--",
        "clarity_specificity": "--",
        "alignment_ai_ethics": "--",
        "total_score": "--"
    }
    return render_template('aimirror.html', scores=placeholder_scores)

@app.route('/evaluate', methods=['POST'])
def evaluate():
    prompt = request.form['prompt']

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f'''Analyze the following user prompt using the five ethical scoring criteria.

**CRITERIA:**
1.  **Purpose & Intent (Max 20 pts)** – Is the prompt aimed at learning, curiosity, or productivity (vs cheating or harm)?
2.  **Autonomy & Integrity (Max 20 pts)** – Does it respect the user's own role (not "do it for me" but "help me understand")?
3.  **Social Impact / Harm (Max 20 pts)** – Could the output cause harm, spread misinformation, or promote bias?
4.  **Clarity & Specificity (Max 20 pts)** – Is the prompt well-defined and constructive for AI to answer responsibly?
5.  **Alignment with AI Ethics (Max 20 pts)** – Does it reflect responsible AI use (transparency, fairness, accountability)?

**TASK:**
1.  **SCORE** – Assign a score (0–20) for each category.
2.  **EXPLANATION** – Give 1–2 short student-friendly sentences for why each score was given.
3.  **TOTAL SCORE** – Sum of all five.
4.  **OVERALL FEEDBACK** – Suggest improvements in a short paragraph.

**OUTPUT FORMAT (ONLY JSON):**
{{
  "scores": {{
    "purpose_intent": [score],
    "autonomy_integrity": [score],
    "social_impact_harm": [score],
    "clarity_specificity": [score],
    "alignment_ai_ethics": [score],
    "total_score": [total score]
  }},
  "explanations": {{
    "purpose_intent": "[short explanation]",
    "autonomy_integrity": "[short explanation]",
    "social_impact_harm": "[short explanation]",
    "clarity_specificity": "[short explanation]",
    "alignment_ai_ethics": "[short explanation]"
  }},
  "feedback": "[overall suggestion paragraph]"
}}

**USER PROMPT TO EVALUATE:**
{prompt}
'''
    )

    try:
        results = json.loads(re.search(r'{.*}', response.text, re.DOTALL).group())
        scores = results['scores']
        feedback = results['feedback']
        explanations = results['explanations']
        return render_template('aimirror.html', scores=scores, feedback=feedback, explanations=explanations)
    except Exception as e:
        print("Error:", e)
        message = 'Not able to process request. Try again.'
        placeholder_scores = {
            "purpose_intent": "--",
            "autonomy_integrity": "--",
            "social_impact_harm": "--",
            "clarity_specificity": "--",
            "alignment_ai_ethics": "--",
            "total_score": "--"
        }
        return render_template('aimirror.html', message=message, scores=placeholder_scores)

if __name__ == "__main__":
    app.run(debug=True)
