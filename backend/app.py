# importing required python libraries
from flask import Flask, jsonify, request
from flask_mongoengine import MongoEngine
from flask_cors import CORS, cross_origin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from itertools import islice
from webdriver_manager.chrome import ChromeDriverManager
from bson.json_util import dumps
import pandas as pd
import json
from datetime import datetime, timedelta
import yaml
import hashlib
import uuid

existing_endpoints = ["/applications"]


def create_app():
    app = Flask(__name__)
    # make flask support CORS
    CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'

    # testing API, you can try to access http://localhost:5000/ on your browser after starting the server
    # params:
    #   -name: string

    @app.errorhandler(404)
    def page_not_found(e):
        return jsonify({'error': 'Not Found'}), 404

    @app.errorhandler(405)
    def page_not_found(e):
        return jsonify({'error': 'Method not Allowed'}), 405

    @app.before_request
    def middleware():
        try:
            if request.path in existing_endpoints:
                headers = request.headers
                try:
                    token = headers['Authorization'].split(" ")[1]
                except:
                    return jsonify({"error": "Unauthorized"}), 401
                userid = token.split(".")[0]
                user = Users.objects(id=userid).first()

                if user is None:
                    return jsonify({"error": "Unauthorized"}), 401

                expiry_flag = False
                for tokens in user['authTokens']:
                    if tokens['token'] == token:
                        expiry = tokens['expiry']
                        expiry_time_object = datetime.strptime(expiry, "%m/%d/%Y, %H:%M:%S")
                        if datetime.now() <= expiry_time_object:
                            expiry_flag = True
                            delete_auth_token(tokens, userid)
                            break

                if not expiry_flag:
                    return jsonify({"error": "Unauthorized"}), 401


        except:
            return jsonify({"error": "Internal server error"}), 500

    def get_token_from_header():
        headers = request.headers
        token = headers['Authorization'].split(" ")[1]
        return token

    def get_userid_from_header():
        headers = request.headers
        token = headers['Authorization'].split(" ")[1]
        userid = token.split(".")[0]
        return userid

    def delete_auth_token(token_to_delete, user_id):
        user = Users.objects(id=user_id).first()
        auth_tokens = []
        for token in user['authTokens']:
            if token != token_to_delete:
                auth_tokens.append(token)
        user.update(authTokens=auth_tokens)

    @app.route("/")
    @cross_origin()
    def health_check():
        return jsonify({"message": "Server up and running"}), 200

    @app.route("/users/signup", methods=['POST'])
    def sign_up():
        try:
            # print(request.data)
            data = json.loads(request.data)
            print(data)
            try:
                _ = data['username']
                _ = data['password']
                _ = data['fullName']
            except:
                return jsonify({'error': 'Missing fields in input'}), 400

            username_exists = Users.objects(username=data['username'])
            if len(username_exists) != 0:
                return jsonify({'error': 'Username already exists'}), 400
            password = data['password']
            password_hash = hashlib.md5(password.encode())
            user = Users(id=get_new_user_id(),
                         fullName=data['fullName'],
                         username=data['username'],
                         password=password_hash.hexdigest(),
                         authTokens=[],
                         applications=[])
            user.save()
            return jsonify(user.to_json()), 200
        except:
            return jsonify({'error': 'Internal server error'}), 500

    @app.route("/users/login", methods=['POST'])
    def login():
        try:
            try:
                data = json.loads(request.data)
                _ = data['username']
                _ = data['password']
            except:
                return jsonify({'error': 'Username or password missing'}), 400
            password_hash = hashlib.md5(data['password'].encode()).hexdigest()
            user = Users.objects(username=data['username'], password=password_hash).first()
            if user is None:
                return jsonify({"error": "Wrong username or password"})
            token = str(user['id']) + "." + str(uuid.uuid4())
            expiry = datetime.now() + timedelta(days=1)
            expiry_str = expiry.strftime("%m/%d/%Y, %H:%M:%S")
            auth_tokens_new = user['authTokens'] + [{'token': token, 'expiry': expiry_str}]
            user.update(authTokens=auth_tokens_new)
            return jsonify({'token': token, 'expiry': expiry_str})
        except:
            return jsonify({'error': 'Internal server error'}), 500

    @app.route("/users/logout", methods=['POST'])
    def logout():
        try:
            userid = get_userid_from_header()
            user = Users.objects(id=userid).first()
            auth_tokens = []
            incoming_token = get_token_from_header()
            for token in user['authTokens']:
                if token['token'] != incoming_token:
                    auth_tokens.append(token)
            user.update(authTokens=auth_tokens)

            return jsonify({"success": ""}), 200

        except:
            return jsonify({'error': 'Internal server error'}), 500

    # search function
    # params:
    #   -keywords: string
    @app.route("/search")
    def search():
        keywords = request.args.get('keywords') if request.args.get('keywords') else 'random_test_keyword'
        salary = request.args.get('salary') if request.args.get('salary') else ''
        keywords = keywords.replace(' ', '+')
        if keywords == 'random_test_keyword':
            return json.dumps({'label': str("successful test search")})
        # create a url for a crawler to fetch job information
        if salary:
            url = "https://www.google.com/search?q=" + keywords + "%20salary%20" + salary + "&ibp=htl;jobs"
        else:
            url = "https://www.google.com/search?q=" + keywords + "&ibp=htl;jobs"

        # webdriver can run the javascript and then render the page first.
        # This prevent websites don't provide Server-side rendering 
        # leading to crawlers cannot fetch the page
        chrome_options = Options()
        # chrome_options.add_argument("--no-sandbox") # linux only
        chrome_options.add_argument("--headless")
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) " \
                     "Chrome/71.0.3578.98 Safari/537.36 "
        chrome_options.add_argument(f"user-agent={user_agent}")
        driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
        driver.get(url)
        content = driver.page_source
        driver.close()
        soup = BeautifulSoup(content)

        # parsing searching results to DataFrame and return
        df = pd.DataFrame(columns=["jobTitle", "companyName", "location"])
        mydivs = soup.find_all("div", {"class": "PwjeAc"})
        for i, div in enumerate(mydivs):
            df.at[i, "jobTitle"] = div.find("div", {"class": "BjJfJf PUpOsf"}).text
            df.at[i, "companyName"] = div.find("div", {"class": "vNEEBe"}).text
            df.at[i, "location"] = div.find("div", {"class": "Qk80Jf"}).text
        return jsonify(df.to_dict('records'))

    # get data from the CSV file for rendering root page
    @app.route("/applications", methods=['GET'])
    def get_data():
        try:
            userid = get_userid_from_header()
            user = Users.objects(id=userid).first()
            applications = user['applications']
            return jsonify(applications)
        except:
            return jsonify({'error': 'Internal server error'}), 500

    @app.route("/applications", methods=['POST'])
    def add_application():
        try:
            userid = get_userid_from_header()
            try:
                request_data = json.loads(request.data)
                _ = request_data['jobTitle']
                _ = request_data['companyName']
                _ = request_data['date']
            except:
                return jsonify({'error': 'Missing fields in input'}), 400

            user = Users.objects(id=userid).first()
            current_application = {
                'id': get_new_application_id(userid),
                'jobTitle': request_data['jobTitle'],
                'companyName': request_data['companyName'],
                'date': request_data['date'],
            }
            applications = user['applications'] + [current_application]

            user.update(applications=applications)
            return jsonify(current_application), 200
        except:
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/applications/<int:application_id>', methods=['PUT'])
    def update_application(application_id):
        try:
            userid = get_userid_from_header()
            try:
                request_data = json.loads(request.data)
            except:
                return jsonify({'error': 'No fields found in input'}), 400

            user = Users.objects(id=userid).first()
            current_applications = user['applications']

            if len(current_applications) == 0:
                return jsonify({'error': 'No applications found'}), 400
            else:
                updated_applications = []
                application_updated_flag = False
                for application in current_applications:
                    if application['id'] == application_id:
                        application_updated_flag = True
                        for key, value in request_data.items():
                            application[key] = value
                    updated_applications += [application]
                if not application_updated_flag:
                    return jsonify({'error': 'Application not found'}), 400
                user.update(applications=updated_applications)

            return jsonify({'message': 'Application successfully edited'}), 200
        except:
            return jsonify({'error': 'Internal server error'}), 500

    @app.route("/applications/<int:application_id>", methods=['DELETE'])
    def delete_application(application_id):
        try:
            userid = get_userid_from_header()
            user = Users.objects(id=userid).first()

            current_applications = user['applications']

            application_deleted_flag = False
            updated_applications = []
            for application in current_applications:
                if application['id'] != application_id:
                    updated_applications += [application]
                else:
                    application_deleted_flag = True

            if not application_deleted_flag:
                return jsonify({'error': 'Application not found'}), 400
            user.update(applications=updated_applications)
            return jsonify({"message": "Application deleted successfully"}), 200
        except:
            return jsonify({"error": "Internal server error"}), 500

    return app


app = create_app()
with open('backend/application.yml') as f:
    info = yaml.load(f, Loader=yaml.FullLoader)
    app.config['MONGODB_SETTINGS'] = {
        'db': 'appTracker',
        'host': 'localhost'
    }
db = MongoEngine()
db.init_app(app)


class Users(db.Document):
    id = db.IntField(primary_key=True)
    fullName = db.StringField()
    username = db.StringField()
    password = db.StringField()
    authTokens = db.ListField()
    applications = db.ListField()

    def to_json(self):
        return {"id": self.id,
                "fullName": self.fullName,
                "username": self.username}


def get_new_user_id():
    user_objects = Users.objects()
    if len(user_objects) == 0:
        return 1

    new_id = 0
    for a in user_objects:
        new_id = max(new_id, a['id'])

    return new_id + 1


def get_new_application_id(user_id):
    user = Users.objects(id=user_id).first()

    if len(user['applications']) == 0:
        return 1

    new_id = 0
    for a in user['applications']:
        new_id = max(new_id, a['id'])

    return new_id + 1


if __name__ == "__main__":
    app.run()
