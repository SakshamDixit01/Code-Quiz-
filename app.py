from flask import Flask , render_template, jsonify, request
import sqlite3

app = Flask(__name__)

DATABASE = "database.db"

def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection

def initialize_database():
    connection = get_db_connection()


    connection.execute(
        """CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            question TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            correct_answer INTEGER NOT NULL,
            explanation TEXT NOT NULL
            
        )"""
    )

    connection.execute ( 
        """ CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_name TEXT NOT NULL,
        category TEXT NOT NULL,
        score INTEGER NOT NULL,
        total_questions INTEGER NOT NULL
        )"""
    )

    count = connection.execute(
        "SELECT COUNT(*) FROM questions").fetchone()[0]

    if count == 0:
        questions = [
            (
                "Python", "What does len([2,4,6]) return ?",
                "2","3","6", 1,
                "The list contains three elements."
            ),
            (
                "Python",
                "Which Keyword defines a function in Python?",
                "function","def","fun",1,
                "The def keyword is used to define a function."
            ),
            (
                "SQL",
                "Which Command retrieves data from a table?",
                "GET", "OPEN" , "SELECT",2,
                "SELECT is used to retrieve data from database tables."

            ),
            (
                "HTML",
                "Which tag creates a hyperlink",
                "<link>" , "<a>", "<href>" , 1,
                "The a tag creates a hyperlink."
            ),
            (
                "JavaScript",
                "Which keyword declares a block - scoped variable",
                "let", "print", "echo", 0,
                "'let' is the correct keyword to declare a block-scoped variable in JavaScript."
            )
        ]

        connection.executemany(
            """ INSERT INTO questions (
            category, question , option_a , option_b , option_c, correct_answer , explanation)
            VALUES (?,?,?,?,?,?,?)""", questions)

    connection.commit()
    connection.close()

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/questions")
def get_questions():
    category = request.args.get("category")


    connection = get_db_connection()

    if category:
        rows = connection.execute(
            """ SELECT id , category , question, option_a,option_b,option_c
            FROM questions 
            """
        ).fetchall()

    connection.close()


    return jsonify([dict(row) for row in rows])

@app.route("/api/check-answer", methods = ["POST"])
def check_answer():
    data = request.get_json(silent=True) or {}

    question_id = data.get("question_id")
    selected_answer = data.get("selected_answer")

    if (
        not isinstance(question_id,int)
        or isinstance(question_id , bool)
        or not isinstance(selected_answer, int)
        or isinstance(selected_answer , bool)
        or selected_answer not in (0,1,2)

    ):
        return jsonify({"error" : "Invalid answer data"}), 400
    connection = get_db_connection()


    question = connection.execute(
        """ SELECT correct_answer , explanation 
            FROM questions
            WHERE id = ?
            """, (question_id,)
    ).fetchone()

    connection.close()

    if question is None :
        return jsonify ({"error" : "Question not found"}), 404

    return jsonify ({
        "correct" : selected_answer == question["correct_answer"], "explanation":question["explanation"]
    })

@app.route("/api/results" , methods = ["POST"])
def save_result():
    data = request.get_json(silent=True) or {}

    player_name = data.get("player_name" , 
                           "Guest")
    category = data.get("category" , "Mixed")
    score = data.get("score")
    total = data.get("total_questions")

    if (
        not isinstance(player_name,str)
        or not isinstance(category,str)
        or not player_name.strip()
        or len(player_name) > 50
        or len(category) > 30
        or type(score) is not int
        or type(total) is not int
        or total <= 0
        or score < 0
        or score > total
    ):
        return jsonify({"error" : "Invalid result data"}), 400

    connection = get_db_connection()

    connection.execute (
        """ INSERT INTO results  (
        player_name , category , score , total_questions)
        VALUES (?,?,?,?)
        """ , (player_name.strip(), category , score ,total))
    connection.commit()
    connection.close()

    return jsonify({"message" : "Result saved successfully"}), 201

@app.route("/api/leaderboard")
def leaderboard (): 
    connection = get_db_connection()

    rows = connection.execute(
        """ SELECT player_name , category , score , total_questions
        FROM results
        ORDER BY (1.0*score/total_questions)
        DESC ,score DESC 
        LIMIT 10"""
    ).fetchall()

    connection.close()

    return jsonify([dict(row) for row in rows])

initialize_database()

if __name__ == "__main__":
    app.run(debug=True)

    
    