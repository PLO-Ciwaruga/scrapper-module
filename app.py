"""
    PLO-Ciwaruga

    Main Program
    20/04/2020
"""

import os
import json
from flask import Flask, request
from flask import jsonify
from flask_httpauth import HTTPBasicAuth

from Scrapper import ScrapperDetik, ScrapperKompas, ScrapperRepublika
from Scrapper import ScrapperWrapper
from Auth import Auth
from Params import Params
from Connector.Receiver import Receiver

# Creating Flask instance
app = Flask(__name__)
httpAuth = HTTPBasicAuth()

# Getting params for the app
params = Params()
params.getEnvSettings()

# Creating Auth instance
auth = Auth()


@httpAuth.verify_password
def verify_password(username, password):
    if auth.auth(username, password):
        return username


@httpAuth.get_user_roles
def get_user_roles(user):
    return auth.getRole(user)


@app.route('/')
def home():
    return "Not Yet, bruh.", 404


@app.route('/update')
@httpAuth.login_required(role=['user', 'admin'])
def updateQuery():
    try:
        # Getting arguments for each site
        nKompas = request.args.get('kompas')
        nDetik = request.args.get('detik')
        nRepublika = request.args.get('republika')

        # Sanitizing inputs
        if nKompas:
            nKompas = int(nKompas)
        else:
            nKompas = params.n_kompas

        if nDetik:
            nDetik = int(nDetik)
        else:
            nDetik = params.n_detik

        if nRepublika:
            nRepublika = int(nRepublika)
        else:
            nRepublika = params.n_republika

        # Getting the NEWS!
        kompasScrap = ScrapperKompas(
            chromeExecPath=params.chrome_driver_path,
            chromeBinPath=params.chrome_bin_path)
        # kompasScrap.get(nKompas)
        # kompasScrap.toLabel(params.label_studio_url)
        kompasWrapper = ScrapperWrapper(
            kompasScrap, 'kompas', nKompas, params.label_studio_url)

        detikScrap = ScrapperDetik(
            chromeExecPath=params.chrome_driver_path,
            chromeBinPath=params.chrome_bin_path)
        # detikScrap.get(nDetik)
        # detikScrap.toLabel(params.label_studio_url)
        detikWrapper = ScrapperWrapper(
            detikScrap, 'detik', nDetik, params.label_studio_url)

        republikaScrap = ScrapperRepublika(
            chromeExecPath=params.chrome_driver_path,
            chromeBinPath=params.chrome_bin_path)
        # republikaScrap.get(nRepublika)
        # republikaScrap.toLabel(params.label_studio_url)
        republikaWrapper = ScrapperWrapper(
            republikaScrap, 'republika', nRepublika, params.label_studio_url)

        kompasWrapper.start()
        detikWrapper.start()
        republikaWrapper.start()

        return "Success", 200

    except TypeError as TE:
        print("[ERROR] : Type error on update query")
        print("[ERROR INFO] : ", TE)

        return "Error", 400


@app.route('/set/<paramType>', methods=['POST'])
@httpAuth.login_required(role='admin')
def setParams(paramType):
    if paramType == 'labelurl':
        url = request.form.get('url')
        print('[INFO] Got request label change to %s' % (url))

        if url != None or len(url) == 0:
            params.label_studio_url = url
            params.update()

            return "Success", 200

        else:
            return "Error", 400

    else:
        return "Error", 400


@app.route('/add/<paramType>', methods=['POST'])
@httpAuth.login_required(role='admin')
def addParams(paramType):
    if paramType == 'user':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')

        if username != None and password != None and role != None:
            tempStatus = auth.newUser(username, password, role)

            if tempStatus:
                return "Success", 200
            else:
                return "Error", 400

        else:
            return "Error", 400

    else:
        return "Error", 400


@app.route('/get/<paramType>', methods=['POST'])
@httpAuth.login_required(role=['user', 'admin'])
def getParams(paramType):
    if paramType == 'list':
        resultList = os.listdir(params.result_dir)

        return jsonify(resultList)

    elif paramType == 'content':
        filename = request.form.get('filename')
        fullDir = params.result_dir + '/' + filename

        try:
            with open(fullDir, 'r') as source_file:
                rawDict = json.load(source_file)

            return jsonify(rawDict)

        except FileNotFoundError as FNFE:
            print('[ERROR] No such file ', FNFE)

            return 'Not Found', 404

    elif paramType == 'update':
        receiver = Receiver(params.label_studio_url, params.temp_dir)
        savedFileDir = receiver.saveFile(params.result_dir)

        return jsonify(filename=savedFileDir.split('/')[-1])

    return "Error", 400

if __name__ == "__main__":
    app.run(debug=True)
