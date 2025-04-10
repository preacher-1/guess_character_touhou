from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import random
import re
import os
from datetime import timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class GameState(db.Model):
    """
    游戏状态管理
    """
    id = db.Column(db.Integer, primary_key=True)
    questions = db.Column(db.String(1000))
    templates = db.Column(db.String(1000))
    guessed_chars = db.Column(db.String(100))
    solved_questions = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)

class GuessCharacter:
    """
    游戏主程序
    """
    def __init__(self):
        self.ques_guessed = []
        self.ques = []
        self.ques_template = []
        self.ques_dict = dict()
        self.unsolved = 0
        self.solved = set()
        self.original_questions = []  # 保存原始题目

    def check_fully_revealed(self):
        for i, template in enumerate(self.ques_template):
            if i + 1 not in self.solved and '*' not in template:
                self.solved.add(i + 1)
                self.unsolved -= 1
                return True
        return False

    def initialize(self, num_questions):
        self.ques_guessed = []
        self.ques = []
        self.ques_template = []
        self.ques_dict = dict()
        self.unsolved = num_questions
        self.solved = set()
        self.original_questions = []
        
        with open("characters.txt", mode="r", encoding="utf-8") as f:
            source = [line.strip() for line in f.readlines()]
        self.ques.extend(random.sample(source, self.unsolved))
        self.original_questions = self.ques.copy()  # 保存原始题目
        
        for i in range(self.unsolved):
            self.ques_template.append(re.sub(r"\S", "*", self.ques[i]))
            for j in range(len(self.ques[i])):
                ch = self.ques[i][j]
                if ch != " ":
                    if ch in self.ques_dict:
                        self.ques_dict[ch].append((i, j))
                    else:
                        self.ques_dict[ch] = [(i, j)]

    def guess_char(self, char):
        if not char:
            return False

        if char not in self.ques_guessed:
            self.ques_guessed.append(char)
        if char.isalpha():
            chs = (char.lower(), char.upper())
            if not any(map(lambda x: x in self.ques_dict, chs)):
                return False
            for ch in chs:
                if ch in self.ques_dict:
                    for val in self.ques_dict[ch]:
                        i, j = val
                        temp = list(self.ques_template[i])
                        temp[j] = ch
                        self.ques_template[i] = "".join(temp)
                    del self.ques_dict[ch]
            self.check_fully_revealed()  # 检查是否有题目被完全揭示
            return True
        else:
            if char in self.ques_dict:
                for val in self.ques_dict[char]:
                    i, j = val
                    temp = list(self.ques_template[i])
                    temp[j] = char
                    self.ques_template[i] = "".join(temp)
                del self.ques_dict[char]
                self.check_fully_revealed()  # 检查是否有题目被完全揭示
                return True
        return False

    def show_answer(self, num):
        if num > len(self.ques) or num < 1:
            return False
        if num in self.solved:
            return False
        self.ques_template[num - 1] = self.ques[num - 1]
        self.unsolved -= 1
        self.solved.add(num)
        return True

    def get_answers(self):
        return self.original_questions

game = GuessCharacter()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('password') == '07210721':  # 简单密码验证
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        return render_template('admin_login.html', error='密码错误')
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin'))
    return render_template('admin_dashboard.html')

@app.route('/api/game/start', methods=['POST'])
def start_game():
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    num_questions = int(request.json.get('num_questions', 5))
    game.initialize(num_questions)
    return jsonify({
        'templates': game.ques_template,
        'guessed_chars': game.ques_guessed,
        'unsolved': game.unsolved
    })

@app.route('/api/game/guess', methods=['POST'])
def make_guess():
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    char = request.json.get('char')
    success = game.guess_char(char)
    return jsonify({
        'success': success,
        'templates': game.ques_template,
        'guessed_chars': game.ques_guessed,
        'unsolved': game.unsolved
    })

@app.route('/api/game/show', methods=['POST'])
def show_answer():
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    num = int(request.json.get('num'))
    success = game.show_answer(num)
    return jsonify({
        'success': success,
        'templates': game.ques_template,
        'unsolved': game.unsolved
    })

@app.route('/api/game/state')
def get_game_state():
    return jsonify({
        'templates': game.ques_template,
        'guessed_chars': game.ques_guessed,
        'unsolved': game.unsolved,
        'is_game_over': game.unsolved == 0
    })

@app.route('/api/game/answers')
def get_answers():
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify({
        'answers': game.get_answers()
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True) 