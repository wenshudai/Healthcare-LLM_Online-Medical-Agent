from flask import Flask, request, jsonify, session, make_response, send_from_directory
import os
from flask_cors import CORS

import sqlite3

from flask_session import Session

import db_agent


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Ensure you have a strong secret key
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = 'session_files'  # Optional: Specify a directory for session files
app.config['SESSION_PERMANENT'] = False  # Sessions are not permanent and will be cleared after the browser closes
Session(app)
CORS(app, supports_credentials=True)





# todo replace the context placeholder age, sympton, age with the real value

def set_context(name, symptoms, age, context):
    return context

def get_context(context):
    return context

def delete_db():
    conn = sqlite3.connect('health_info.db')
    cursor = conn.cursor()

    cursor.execute("VACUUM")
    conn.commit()

    print("Database has been vacuumed.")

    cursor.close()
    conn.close()


def init_db():
    conn = sqlite3.connect('health_info.db')

    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS health_info (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        dob DATE NOT NULL,
        health_condition TEXT
    )
    ''')
    conn.commit()
    conn.close()


@app.route('/')
def index():
    return send_from_directory(os.getcwd(), 'index.html')


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
    if_dob_exist, dob = db_agent.check_for_dob(user_input)
    user_registered = None
    if 'name' in session and 'dob' in session:
        user_registered = check_user_registered_before(session['name'], session['dob'])
    if user_registered is not None:
        # response = jsonify({"responseText": "Thank you for coming back" + str(user_registered)})
        session['health_condition'] = user_registered[4]
        session['dob'] = user_registered[3]
        session['name'] = user_registered[1]
        session['age'] = user_registered[2]
        # app.session_interface.save_session(app, session, response)
        # return make_response(response, 200)
    if 'name' not in session:
        print('health condition is not in session')
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
    if 'dob' not in session:
        print('health condition is not in session')
        if if_dob_exist:
            session['dob'] = dob
            print(session['dob'])
        else:
            response = jsonify({"responseText": "What is your date of birth?"})
            app.session_interface.save_session(app, session, response)
            return make_response(response, 200)
    if 'age' not in session:
        print('health condition is not in session')
        if is_age_exist:
            session['age'] = age_response
            print(session['age'])
        else:
            response = jsonify({"responseText": "What is your age?"})
            app.session_interface.save_session(app, session, response)
            return make_response(response, 200)
    if 'health_condition' not in session:
        print('health condition is not in session')
        if is_health_exist:
            session['health_condition'] = health_condition
        else:
            response = jsonify({"responseText": "What is your health condition?"})
            app.session_interface.save_session(app, session, response)
            return make_response(response, 200)
    # keys_to_check = ['name', 'age', 'dob', 'health_condition']
    print(user_registered)

    if user_registered is not None:
        age = session['age']
        name = session['name']
        symptoms = session['health_condition']
        context = [{'role': 'system', 'content': f"""
        You are a medical robot, providing medical consultation services to patients. 
        First, you should get the patient's name and age and symptoms which is {name}, {age}, {symptoms}
        then you should give advice based on that answer. Confirm whether the patient needs to add anything else. 
        You need to inform the patient about the possible diseases related to their symptoms, 
        whether they can take any medication on their own, or if they should seek immediate medical attention, 
        and which department they should visit. 
        You should also advise the patient on how to prevent diseases. 
        Finally, offer your well wishes. 
        Please ensure that your responses are casual and friendly, and make sure they are logical.
        """}]
        print({session['health_condition']})
        current_context = set_context(age, name, symptoms, get_context(context))
        current_context.append({'role': 'user', 'content': f"{session['health_condition']}"})
        print(current_context)
        message = 'Thank for coming back, your health condition is ' + session['health_condition']
        query_response = get_completion_from_messages(current_context)
        response = jsonify({"responseText": message + query_response})
        return make_response(response, 200)
    else:
        sql = f"INSERT INTO health_info (name, age, dob, health_condition) VALUES ('{session['name']}', {session['age']},'{session['dob']}','{session['health_condition']}');"
        execute_sql(sql)
        response = jsonify({"responseText": "thank you for providing this information"})
        app.session_interface.save_session(app, session, response)

        return make_response(response, 200)


def check_user_registered_before(name, dob):
    sql = "SELECT * FROM health_info WHERE name = ? AND dob = ?"
    # [name, dob, age, heath_condition] = sql.
    query_res = execute_sql_with_res(sql, (name, dob))
    if query_res:
        return query_res[0]
    return None


def execute_sql(sql):
    conn = sqlite3.connect('health_info.db')
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()
    print('sql executed ' + sql)


def execute_sql_with_res(sql, placeholders):
    conn = sqlite3.connect('health_info.db')
    cursor = conn.cursor()
    cursor.execute(sql, placeholders)
    results = cursor.fetchall()
    # print('sql executed ' + sql + 'placeholders ' + placeholders)
    # Print results

    # Clean up
    cursor.close()
    conn.close()
    if results:
        return results
    else:
        print('no result found')
        return None


def describe_table(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    info = cursor.fetchall()
    cursor.close()
    return info

def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content


if __name__ == '__main__':
    delete_db()
    init_db()
    app.run(debug=True, host='0.0.0.0', port=8000)
    # sql = "SELECT * FROM health_info WHERE name = ? AND dob = ?"
    # res = execute_sql_with_res(sql, ('shiva', '1993-03-25'))
    # sql = "SELECT * FROM health_info"
    # res = execute_sql_with_res(sql, ())

    # print(res)
    # sql = f"Describe health_info"
    # res = execute_sql_with_res(sql)
    # conn = sqlite3.connect('health_info.db')
    # cursor = conn.cursor()
    # cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    # print(cursor.fetchall())  # This will print all table names
    # cursor.close()
    # conn.close()
    # print(res)