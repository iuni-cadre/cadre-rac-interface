
# Flask app whose primary purpose is to server the frontend

import sys
from os import path
import configparser
import requests
import psycopg2


from flask import Flask, render_template, json, jsonify
from flask_cors import CORS

#make sure the frontend exists before even starting the app
frontend_exists = path.isfile("./frontend/index.html")
if not frontend_exists:
    print("Server cannot start.  Frontend does not exist.  ../frontend/dist does not exist.")
    print("Go to frontend directory and run 'npm run build' to build the frontend.")
    sys.exit()

config_exists = path.isfile("./conf/backend.config")
if not config_exists:
    print("Server cannot start.  Config file does not exist.  ../conf/backend.config does not exist.")
    sys.exit()

config_parser = configparser.ConfigParser()
config_parser.read("./conf/backend.config")
config = config_parser['DEFAULT']
jupyter_config = config_parser['JUPYTERAPI']
meta_db_config = config_parser['CADRE_META_DATABASE_INFO']



application = app = Flask(__name__, 
    template_folder="./frontend",
    static_folder="./frontend/assets"
    )

CORS(application);

@application.route("/api/new-notebook/<username>")
def api_new_notebook_username(username):

    headers = {"Authorization": "token " + jupyter_config["AuthToken"]}
    payload = {}
    r = requests.post(jupyter_config["APIURL"] + "/users/" + username + "/server", data=payload, headers=headers)
    return jsonify({"status_code": r.status_code, "text": r.text})


@application.route("/api/notebook-status/<username>")
def api_notebook_status_username(username):

    headers = {"Authorization": "token "  + jupyter_config["AuthToken"]}
    payload = {}
    r = requests.get(jupyter_config["APIURL"] + "/users/" + username + "", data=payload, headers=headers)
    return jsonify({"json": r.json(), "status_code": r.status_code, "text": r.text})

@application.route("/api/get-new-notebook-token/<username>")
def api_get_new_notebook_token(username):
    conn = psycopg2.connect(dbname = meta_db_config["database-name"], user= meta_db_config["database-username"], password= meta_db_config["database-password"], host= meta_db_config["database-host"], port= meta_db_config["database-port"])
    cur = conn.cursor()
    cur.execute("SELECT j_pwd, j_token FROM jupyter_user WHERE j_username=%s", [username])
    row = cur.fetchone()
    pwd = row[0]

    token_args = {
        "username": username,
        "password": pwd
    }

    headers = {
        "Content-Type": "application/json"
    }
    jupyterhub_token_ep = jupyter_config["APIURL"] + '/authorizations/token'
    response = requests.post(jupyterhub_token_ep, json=token_args, headers=headers)
    # response = requests.get(util.config_reader.get_jupyterhub_api())
    status_code = response.status_code
    
    access_token_json = response.json()
    token = access_token_json['token']

    cur.execute("UPDATE jupyter_user SET j_token = %s WHERE j_username= %s", [token, username])
    conn.commit()

    cur.close()
    conn.close()

    return token

    
# @application.route("/api/stop-notebook/<username>")
# def api_stop_notebook_username(username):

#     headers = {"Authorization": "token "  + jupyter_config["AuthToken"]}
#     payload = {}
#     r = requests.delete(jupyter_config["APIURL"] + "/users/" + username + "", data=payload, headers=headers)
#     return jsonify({"json": r.json(), "status_code": r.status_code, "text": r.text})


@application.route("/api")
@application.route("/api/")
@application.route("/api/<path:fallback>")
def api_index(fallback=""):
    return jsonify({"error": "Unknown endpoint."})



@application.route("/")
def index():
    return render_template("/index.html")

@application.route("/<path:fallback>")
def fallback(fallback):
    return render_template("/index.html")

if __name__ == '__main__':
    application.run(host=config['FlaskHost'], port=int(config['FlaskPort']), debug=config['DebugMode']=='True')