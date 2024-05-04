from flask import Flask, request, jsonify, session, make_response
from flask_cors import CORS

import sqlite3

from flask_session import Session

import db_agent

app = Flask(__name__)
app.config['SECRET_KEY'] = 'this_is_a_secret_key'  # Ensure you have a strong secret key
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = 'session_files'  # Optional: Specify a directory for session files
app.config['SESSION_PERMANENT'] = False  # Sessions are not permanent and will be cleared after the browser closes
Session(app)
CORS(app, supports_credentials=True)

def init_db():
    conn = sqlite3.connect('health_info.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS health_info (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        health_condition TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()


@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        print(response)
        return response
    data = request.get_json()
    user_input = data.get('message', '')
    print('user_input is ' + user_input)
    is_name_exist, name_response = db_agent.check_for_name(user_input)
    is_age_exist, age_response = db_agent.check_for_age(user_input)
    is_health_exist, health_condition = db_agent.check_for_health_condition(user_input)
    if 'name' not in session:
        print('yo you are not in session la')
        if is_name_exist:
            session['name'] = name_response
            print(session['name'])
        else:
            response = jsonify({"responseText": "What is your name?"})
            app.session_interface.save_session(app, session, response)
            return make_response(response, 200)
    else:
        print('yo you are in session la')
    if 'age' not in session:
        if is_age_exist:
            session['age'] = age_response
        else:
            response = jsonify({"responseText": "What is your age?"})
            app.session_interface.save_session(app, session, response)
            return make_response(response, 200)
    if 'health_condition' not in session:
        if is_health_exist:
            session['health_condition'] = health_condition
        else:
            response = jsonify({"responseText": "What is your health condition?"})
            app.session_interface.save_session(app, session, response)
            return make_response(response, 200)
    keys_to_check = ['name', 'age', 'health_condition']
    if all(key in session for key in keys_to_check):
        sql = f"INSERT INTO health_info (name, age, health_condition) VALUES ('{session['name']}', {session['age']}, '{session['health_condition']}');"
        session.clear()  # Clear session after collecting all data
        execute_sql(sql)
        response = jsonify({"responseText": "thank you for providing this information"})
        app.session_interface.save_session(app, session, response)

        return make_response(response, 200)
    else:
        response = jsonify({"responseText": "All information has been collected"})
        app.session_interface.save_session(app, session, response)

    return make_response(response, 200)


def execute_sql(sql):
    conn = sqlite3.connect('health_info.db')
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()
    print('sql executed ' + sql)


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0')
