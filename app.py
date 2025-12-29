from flask import Flask, render_template, request, jsonify, session
import random
import csv
import json
import os
import re

app = Flask(__name__)
app.secret_key = 'hangman_survival_secret_key'

# 確保路徑在雲端環境正確
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, 'vocabulary.csv')
LEADERBOARD_FILE = os.path.join(BASE_DIR, 'leaderboard.json')

def load_questions():
    questions = []
    if not os.path.exists(CSV_FILE):
        return []
    with open(CSV_FILE, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                clean_row = {k.strip().lower(): v.strip() for k, v in row.items() if k and v}
                if 'target' in clean_row and 'sentence' in clean_row:
                    questions.append(clean_row)
            except: continue
    return questions

def save_score(name, score):
    leaderboard = []
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, 'r', encoding='utf-8') as f:
                leaderboard = json.load(f)
        except: leaderboard = []
    leaderboard.append({'name': name, 'score': score})
    leaderboard = sorted(leaderboard, key=lambda x: x['score'], reverse=True)[:10]
    with open(LEADERBOARD_FILE, 'w', encoding='utf-8') as f:
        json.dump(leaderboard, f, ensure_ascii=False, indent=4)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    session['player_name'] = data.get('name', 'Explorer')
    session['score'] = 0
    return jsonify({"status": "success", "player_name": session['player_name']})

# 雙路由設計：確保舊版 JS 與新版都能跑通
@app.route('/get_word')
@app.route('/api/get_question')
def get_word():
    questions = load_questions()
    if not questions: return jsonify({"error": "CSV error"}), 500
    q = random.choice(questions)
    target = q['target']
    masked_sentence = re.sub(re.escape(target), "___", q['sentence'], flags=re.IGNORECASE)
    return jsonify({
        "word": target.upper().strip(),
        "hint": f"<b>Definition:</b> {q.get('hint', 'No hint')}<br><br><b>Context:</b> {masked_sentence}"
    })

@app.route('/update_score', methods=['POST'])
def update_score():
    if 'player_name' not in session: return jsonify({"status": "error"}), 401
    save_score(session['player_name'], request.json.get('final_score', 0))
    lb = []
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, 'r', encoding='utf-8') as f:
            lb = json.load(f)
    return jsonify({"status": "success", "leaderboard": lb})

if __name__ == '__main__':
    # 重要：Render 必須使用環境變數 PORT
    port = int(os.environ.get("PORT", 5000))
    # 重要：必須綁定 0.0.0.0 才能從外部連線
    app.run(host='0.0.0.0', port=port, debug=False)