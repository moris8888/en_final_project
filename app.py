from flask import Flask, render_template, jsonify
import random
import csv # 引入處理 CSV 的模組
import os

app = Flask(__name__)

def load_questions():
    """讀取外部 CSV 題庫"""
    questions = []
    file_path = 'vocabulary.csv'
    
    # 檢查檔案是否存在，避免程式崩潰
    if not os.path.exists(file_path):
        return [{"target": "error", "full_sentence": "CSV file not found.", "hint": "請建立 vocabulary.csv"}]
    
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            questions.append({
                "target": row['target'].strip(),
                "full_sentence": row['sentence'].strip(),
                "hint": row['hint'].strip()
            })
    return questions

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/get_question')
def get_question():
    questions = load_questions()
    # 從讀取進來的清單中隨機選一題
    question = random.choice(questions)
    return jsonify(question)

if __name__ == '__main__':
    app.run(debug=True)