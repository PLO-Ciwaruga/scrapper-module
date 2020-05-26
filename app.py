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


# Verify the inputted password and username
# Will return the username of the user if the auth succed
# Else it will return None 
@httpAuth.verify_password
def verify_password(username, password):
    if auth.auth(username, password):
        return username
    else:
        return None


# Function to get the role of the user
# Outputs "user", "admin", or None if there's
# no such user in the auth file
@httpAuth.get_user_roles
def get_user_roles(user):
    return auth.getRole(user)


# Main app route
# Shows the main page of the app
# 
# Auth :
#   None, public page
# 
# TBA : Main page of the app
@app.route('/')
def home():
    return "Not Yet, bruh.", 404


# Updates label studio with scrapping data
# Once requested and authenticated, there will
#   be 3 procceses scrapping and sending the resulting news
#   to labelstudio API of the url specified in the settings
# 
# Auth :
#   Works for both admin and user, will need auth
# 
# Usage :
#   Simple request using POST or GET,
#   Override the number of news of each site with
#   adding the name in the GET request and number of news
#   Example,
#   http://localhost:5000/update?kompas=10&detik=15&republika=0
#   
#   The url will update labelstudio with 10 news from kompas, 15
#   from detik and 0 from republika
@app.route('/update')
@httpAuth.login_required(role=['user', 'admin'])
def updateQuery():
    try:
        # Getting arguments for each site
        nKompas = request.args.get('kompas')
        nDetik = request.args.get('detik')
        nRepublika = request.args.get('republika')

        # Sanitizing inputs
        # Looking for None value in the args
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
        # Creating a new instance of Scrapper and adding the
        #   wrapper of the scrapper for it to works using threading
        kompasScrap = ScrapperKompas(
            chromeExecPath=params.chrome_driver_path,
            chromeBinPath=params.chrome_bin_path)
        kompasWrapper = ScrapperWrapper(
            kompasScrap, 'kompas', nKompas, params.label_studio_url)

        detikScrap = ScrapperDetik(
            chromeExecPath=params.chrome_driver_path,
            chromeBinPath=params.chrome_bin_path)
        detikWrapper = ScrapperWrapper(
            detikScrap, 'detik', nDetik, params.label_studio_url)

        republikaScrap = ScrapperRepublika(
            chromeExecPath=params.chrome_driver_path,
            chromeBinPath=params.chrome_bin_path)
        republikaWrapper = ScrapperWrapper(
            republikaScrap, 'republika', nRepublika, params.label_studio_url)

        # Starting the proccess using thread
        # Will also kill the webdriver instance
        kompasWrapper.start()
        detikWrapper.start()
        republikaWrapper.start()

        return "Success", 200

    except TypeError as TE:
        # In case of the args having non integer type
        print("[ERROR] : Type error on update query")
        print("[ERROR INFO] : ", TE)

        return "Error", 400


# Sets the parameters for the app
# Will updates the app parameters using the API,
#   instant change on the app
# 
# Auth :
#   Admin only
# 
# Types :
#   - Label Studio url, using /set/labelurl
#       To update the labelstudio url to be used by the
#           connector instance to updates and gets the label
#       Usage :
#           Send the url of the main page of the labelstudio via
#               POST request using variable name `url`
# 
#           Example on curl, 
#               'curl -X -d "url=http://labelstud.io" http://localhost:5000'
# 
@app.route('/set/<paramType>', methods=['POST'])
@httpAuth.login_required(role='admin')
def setParams(paramType):
    if paramType == 'labelurl':
        # Updating the labelstudio url
        url = request.form.get('url')
        print('[INFO] Got request label change to %s' % (url))

        # Checks on illegal urls
        if url != None or len(url) == 0:
            # Updating the params, and the params file
            params.label_studio_url = url
            params.update()

            return "Success", 200

        else:
            return "Error", 400

    else:
        return "Error", 400


# Addition into the auth
# Requesting into this will add new things into auth
#  instance and updates its file
# 
# Auth :
#   Admin only
# 
# Types :
#   - User addition, via /add/user
#       Will adds new user and its roles into the auth files
# 
#       Usage :
#           Request into it using POST method, with the following
#           parameters
#           - username, username of the user
#           - password, password of the user
#           - role, either "user", or "admin"
# 
#           Curl example,
#               'curl -X POST -d "username=admin&password=admin&role=admin"
#                   http://localhost:5000/add/user'
# 
@app.route('/add/<paramType>', methods=['POST'])
@httpAuth.login_required(role='admin')
def addParams(paramType):
    if paramType == 'user':
        # Getting the user variables
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')

        # Checking for non valid request into the system
        valid = len(username) != 0 and \
            len(password) != 0 and \
            (role != 'user' or \
                role != 'admin')

        if valid:
            tempStatus = auth.newUser(username, password, role)

            # If the newUser method returns False, it meant the addition
            #   doesn't succeeded 
            if tempStatus:
                return "Success", 200
            else:
                return "Duplicate", 400

        else:
            return "Error", 400

    else:
        return "Error", 400


# Getting the content after labelling
# Returning the result after labelling by the user in the
#   labelstudio
# 
# Auth :
#   Admin and user
# 
# Types :
#   - List the content, via /get/list
#       Retruns the list of the results directory as
#           the parameters specify
#       
#       Usage :
#           Simple request into the url via POST request
# 
#   - Update, via /get/update
#       By requesting into this the app will request the newest
#           labelling result from the labelstudio, and save it
#           on the result folder using the following nomenclature
#           of filename,
#               'results-DayMonthYear-HourMinuteSecond.json'
# 
#       The resulting filename will be sent back as the request in a json
#           type response into the request.
#       
#       Usage :
#           Simple request into the url via POST request
# 
#   - Content, via /get/content
#       Returns the content of files in result folder in json
# 
#       Usage :
#           Request using POST type into the url with specifying any file
#               that are listed in the /get/list, specify the filename in
#               the variable 'filename'
# 
@app.route('/get/<paramType>', methods=['POST'])
@httpAuth.login_required(role=['user', 'admin'])
def getParams(paramType):
    if paramType == 'list':
        # List the directory
        resultList = os.listdir(params.result_dir)

        # Returns the resulting list in json
        return jsonify(resultList)

    elif paramType == 'content':
        filename = request.form.get('filename')
        fullDir = params.result_dir + '/' + filename

        # Try to open up the file, if not found throw 404
        try:
            with open(fullDir, 'r') as source_file:
                rawDict = json.load(source_file)

            return jsonify(rawDict)

        except FileNotFoundError as FNFE:
            print('[ERROR] No such file ', FNFE)

            return 'Not Found', 404

    elif paramType == 'update':
        # Download the file using the Receiver class
        receiver = Receiver(params.label_studio_url, params.temp_dir)
        # Save the file it self
        savedFileDir = receiver.saveFile(params.result_dir)

        # Return the file name by getting it from the full directory
        return jsonify(filename=savedFileDir.split('/')[-1])

    return "Error", 400

if __name__ == "__main__":
    # Debugging purpose only
    # If the app is using gunicorn this line will not be executed
    #   as the file is not the main insertion point
    # 
    # To use the debugging function in heroku, either
    #   - Starts it via cmd line using 'python app.py'
    #   - Change the procfile into 'python app.py' instead of gunicorn
    #   - Or add line to add DEBUG = True and add it into the app config
    # 
    app.run(debug=True)
