#!/usr/bin/env python
"""API to list, start, and stop labs in CML"""
import os
import sys
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from cml import Cml


TODAY = datetime.today().strftime('%m-%d-%Y')

logging.basicConfig(filename = f"API-LOG-{TODAY}.log",
                    level=logging.DEBUG,
                    format = "%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s")


app = Flask(__name__)


@app.route("/", methods=["GET"])
def home() -> str:
    """Home page"""
    welcome = "WELCOME TO THE CML START/STOP SCRIPT"
    return jsonify(welcome), 200

@app.route("/lab-list", methods=["GET"])
def get_labs():
    """GET a list of labs"""
    cml = cml_connect(ip, username, password)
    labs = get_lab_list(cml)
    return jsonify(labs), 200

@app.route("/lab/<lab_id>", methods=["GET"])
def get_update_lab_status(lab_id: str,):
    """GET lab status
    args:
        lab_id (int): key number of lab_dict
    """
    # Check for optional arg ?status=<state>
    cml = cml_connect(ip, username, password)
    labs = get_lab_list(cml)
    # Create a list of ints 1 through the number of labs
    lab_check = [i for i in range(1, len(labs) + 1)]
    # Check if lab_id is in the list of ints
    if int(lab_id) in lab_check:
        return jsonify(
            {
                "name": labs[int(lab_id) - 1]["name"],
                "status": labs[int(lab_id) - 1]["state"],
                }
                ), 200
    else:
        return jsonify("Record not found"), 400

@app.route("/lab/<lab_id>/<status>", methods=["POST"])
def start_stop_lab(lab_id: str, status: str):
    """Start or Stop lab
    args:
        status (str): pass `start` or stop to update CML lab status
    """
    cml = cml_connect(ip, username, password)
    labs = get_lab_list(cml)
    # Create a list of ints 1 through the number of labs
    lab_check = [i for i in range(1, len(labs) + 1)]
    # Check if lab_id is in the list of ints
    if int(lab_id) in lab_check:
        if request.method == "POST":
            # Check api key
            check_auth = check_authorization(request)
            # Check optional <status> arg
            if status and status.lower() == "start":
                # If authorized, start lab and return status
                if check_auth[0]:
                    cml.start_lab(labs[int(lab_id) - 1][lab_id])
                    return jsonify(
                        {
                            "name": labs[int(lab_id) - 1]["name"],
                            "status": labs[int(lab_id) - 1]["state"],
                            }
                            ), 200
                else:
                    return jsonify(check_auth[1]), 400
            elif status and status.lower() == "stop":
                if check_auth[0]:
                    cml.stop_lab(labs[int(lab_id) - 1][lab_id])
                    return jsonify(
                        {
                            "name": labs[int(lab_id) - 1]["name"],
                            "status": "STOPPED",
                            }
                            ), 200
                else:
                    return jsonify(check_auth[1]), 400
            else:
                return jsonify("Invalid status"), 400
        else:
            return jsonify(
                {
                    "name": labs[int(lab_id) - 1]["name"],
                    "status": labs[int(lab_id) - 1]["state"],
                    }
                    ), 200
    else:
        return jsonify("Record not found"), 400

def cml_connect(ip, username, password):
    """Connect to CML"""
    cml = Cml(ip, username, password)
    return cml

def get_lab_list(cml):
    """Get a list of labs"""
    lab_list = cml.get_lab_list()
    labs = []
    i = 1
    for lab in lab_list:
        labs.append({str(i): lab.id, "name": lab.title, "state": lab.state()})
        i += 1
    return labs

def check_authorization(request):
    """Check authorization"""
    try:
        # Check if api key is in the request header and is correct
        if request.headers["api-key"] == api_key:
            return (True, "Success")
        else:
            return (False, {"Error": "Invalid API Key."})
    except KeyError:
        return (False, {"Error": "Method requires API key."})


if __name__ == "__main__":
    from argparse import ArgumentParser
    from dotenv import load_dotenv

    load_dotenv()

    parser = ArgumentParser("CML API")
    parser.add_argument(
        "-ip", "--ipaddress", help="IP or URL of CML instance", required=False
    )
    parser.add_argument(
        "-p", "--password", help="CML login user password", required=False,
    )
    parser.add_argument(
        "-u", "--username", help="CML login username", required=False
    )
    parser.add_argument(
        "-s", "--apikey", help="App Server Key Expected in API Calls", required=False
    )

    args = parser.parse_args()

    ip = args.ipaddress
    if ip is None:
        ip = os.getenv("CML_IP")
        if ip is None:
            sys.exit("No IP or URL provided.")

    username = args.username
    if username is None:
        username = os.getenv("CML_USERNAME")
        if username is None:
            sys.exit("No CML login username provided.")

    password = args.password
    if password is None:
        password = os.getenv("CML_PASSWORD")
        if password is None:
            sys.exit("No CML login password provided.")

    api_key = args.apikey
    if api_key is None:
        api_key = os.getenv("CML_API_KEY")

    app.run("0.0.0.0", debug=True)
