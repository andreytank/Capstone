import argparse
from flask import Flask, jsonify, request, send_from_directory
from flask import render_template
import joblib
import socket
import json
import numpy as np
import pandas as pd
import os,re

## import model specific functions and variables
from solution_guidance.model import model_train, model_load, model_predict
from solution_guidance.model import MODEL_VERSION, MODEL_VERSION_NOTE

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
LOGS_DIR = os.path.join(THIS_DIR, "static", "logs")
HOST = "127.0.0.1"
PORT = 8080
app = Flask(__name__)

@app.route('/log/<path:path>')
def response_log(path):
    return send_from_directory(LOGS_DIR, path)

@app.before_first_request
def startup():
    global cur_data, current_models
    print("-loading models-")
    cur_data,current_models = model_load(training=False)
    print("-all models loaded-")

@app.route("/")
def landing():
    return render_template('index.html')

@app.route("/logs")
def logs():
    return render_template('logs.html')

@app.route("/logslist")
def logslist():
    files = [f for f in os.listdir(LOGS_DIR)]
    return jsonify(files)

@app.route('/predict')
def predict():
    """
    function for requesting prediction
    """
    country = request.args.get('country')
    target_date = request.args.get('target_date')

    ## input checking
    if target_date is None:
        print("API-predict exception: received request, but no 'target_date' was found")
        return jsonify([]), 400

    if country is None:
        print("API-predict exception: received request, but no country specified")
        return jsonify([]), 400

    m = re.match(r'(\d{4})-(\d{2})-(\d{2})', target_date)
    try:
        year, month, day = m.group(1, 2, 3)
    except:
        print("API-predict exception: 'target_date' format is invalid")
        return jsonify([]), 400
        
    result = {}
    try:
        _result = model_predict(country,year,month,day,all_models=current_models,all_data=cur_data)
        ## convert numpy objects so ensure they are serializable
        for key,item in _result.items():
            if isinstance(item,np.ndarray):
                result[key] = item.tolist()
            else:
                result[key] = item
        return(jsonify(result))
    except Exception as e:
        print("API-predict exception: model_predict returned: {}".format(str(e)))
        return jsonify([]), 400

@app.route('/train')
def train():
    """
    function for creating new models
    """

    regressor = request.args.get('regressor')
    if regressor is None:
        print("API train exception: no regressor specified")
        return jsonify([]), 400
        
    print("-training model-")
    data_dir = os.path.join(THIS_DIR,"cs-train")
    try:
        model_train(data_dir,regressor=regressor)
        print("-training complete-")
        # reload models and data after re-train
        print("-updating models in browser-")
        cur_data,current_models = model_load(training=False)
        return(jsonify(True))
    except Exception as e:
        print("API train exception: model_train returned: {}".format(str(e)))
        return jsonify([]), 400
        
    
if __name__ == '__main__':


    ## parse arguments for debug mode
    ap = argparse.ArgumentParser()
    args = vars(ap.parse_args())

    if args["debug"]:
        app.run(debug=True, port=PORT)
    else:
        app.run(host=HOST, threaded=True ,port=PORT)

