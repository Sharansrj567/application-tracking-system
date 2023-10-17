"""
The flask application for our program
"""
# importing required python libraries
from flask import Flask, jsonify, request, send_file
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

existing_endpoints = ["/applications", "/resume","/boards","/getBoards"]


def create_app():
    """
    Creates a server hosted on localhost

    :return: Flask object
    """
    app = Flask(__name__)
    # make flask support CORS
    CORS(app)
    app.config["CORS_HEADERS"] = "Content-Type"

    @app.errorhandler(404)
    def page_not_found(e):
        """
        Returns a json object to indicate error 404

        :return: JSON object
        """
        return jsonify({"error": "Not Found"}), 404

    @app.errorhandler(405)
    # pylint: disable=C0103
    def page_not_allowed(e):
        """
        Returns a json object to indicate error 405

        :return: JSON object
        """
        return jsonify({"error": "Method not Allowed"}), 405

    @app.before_request
    def middleware():
        """
        Checks for user authorization tokens and returns message

        :return: JSON object
        """
        try:
            if request.method == "OPTIONS":
                return jsonify({"success": "OPTIONS"}), 200
            if request.path in existing_endpoints:
                headers = request.headers
                try:
                    token = headers["Authorization"].split(" ")[1]
                except:
                    return jsonify({"error": "Unauthorized"}), 401
                userid = token.split(".")[0]
                user = Users.objects(id=userid).first()

                if user is None:
                    return jsonify({"error": "Unauthorized"}), 401

                expiry_flag = False
                for tokens in user["authTokens"]:
                    if tokens["token"] == token:
                        expiry = tokens["expiry"]
                        expiry_time_object = datetime.strptime(
                            expiry, "%m/%d/%Y, %H:%M:%S"
                        )
                        if datetime.now() <= expiry_time_object:
                            expiry_flag = True
                        else:
                            delete_auth_token(tokens, userid)
                        break

                if not expiry_flag:
                    return jsonify({"error": "Unauthorized"}), 401

        except:
            return jsonify({"error": "Internal server error"}), 500

    def get_token_from_header():
        """
        Evaluates token from the request header

        :return: string
        """
        headers = request.headers
        token = headers["Authorization"].split(" ")[1]
        return token

    def get_userid_from_header():
        """
        Evaluates user id from the request header

        :return: string
        """
        headers = request.headers
        token = headers["Authorization"].split(" ")[1]
        userid = token.split(".")[0]
        return userid

    def delete_auth_token(token_to_delete, user_id):
        """
        Deletes authorization token of the given user from the database

        :param token_to_delete: token to be deleted
        :param user_id: user id of the current active user
        :return: string
        """
        user = Users.objects(id=user_id).first()
        auth_tokens = []
        for token in user["authTokens"]:
            if token != token_to_delete:
                auth_tokens.append(token)
        user.update(authTokens=auth_tokens)

    @app.route("/")
    @cross_origin()
    def health_check():
        return jsonify({"message": "Server up and running"}), 200

    @app.route("/users/signup", methods=["POST"])
    def sign_up():
        """
        Creates a new user profile and adds the user to the database and returns the message

        :return: JSON object
        """
        try:
            # print(request.data)
            data = json.loads(request.data)
            print(data)
            try:
                _ = data["username"]
                _ = data["password"]
                _ = data["fullName"]
            except:
                return jsonify({"error": "Missing fields in input"}), 400

            username_exists = Users.objects(username=data["username"])
            if len(username_exists) != 0:
                return jsonify({"error": "Username already exists"}), 400
            password = data["password"]
            password_hash = hashlib.md5(password.encode())
            user = Users(
                id=get_new_user_id(),
                fullName=data["fullName"],
                username=data["username"],
                password=password_hash.hexdigest(),
                authTokens=[],
                applications=[],
            )
            user.save()
            return jsonify(user.to_json()), 200
        except:
            return jsonify({"error": "Internal server error"}), 500

    @app.route("/users/login", methods=["POST"])
    def login():
        """
        Logs in the user and creates a new authorization token and stores in the database

        :return: JSON object with status and message
        """
        try:
            try:
                data = json.loads(request.data)
                _ = data["username"]
                _ = data["password"]
            except:
                return jsonify({"error": "Username or password missing"}), 400
            password_hash = hashlib.md5(data["password"].encode()).hexdigest()
            user = Users.objects(
                username=data["username"], password=password_hash
            ).first()
            if user is None:
                return jsonify({"error": "Wrong username or password"})
            token = str(user["id"]) + "." + str(uuid.uuid4())
            expiry = datetime.now() + timedelta(days=1)
            expiry_str = expiry.strftime("%m/%d/%Y, %H:%M:%S")
            auth_tokens_new = user["authTokens"] + [
                {"token": token, "expiry": expiry_str}
            ]
            user.update(authTokens=auth_tokens_new)
            return jsonify({"token": token, "expiry": expiry_str})
        except:
            return jsonify({"error": "Internal server error"}), 500

    @app.route("/users/logout", methods=["POST"])
    def logout():
        """
        Logs out the user and deletes the existing token from the database

        :return: JSON object with status and message
        """
        try:
            userid = get_userid_from_header()
            user = Users.objects(id=userid).first()
            auth_tokens = []
            incoming_token = get_token_from_header()
            for token in user["authTokens"]:
                if token["token"] != incoming_token:
                    auth_tokens.append(token)
            user.update(authTokens=auth_tokens)

            return jsonify({"success": ""}), 200

        except:
            return jsonify({"error": "Internal server error"}), 500

    # get data from the CSV file for rendering root page
    @app.route("/applications", methods=["GET"])
    def get_data():
        """
        Gets user's applications data from the database

        :return: JSON object with application data
        """
        try:
            userid = get_userid_from_header()
            user = Users.objects(id=userid).first()
            applications = user["applications"]
            return jsonify(applications)
        except:
            return jsonify({"error": "Internal server error"}), 500

    @app.route("/applications", methods=["POST"])
    def add_application():
        """
        Add a new job application for the user

        :return: JSON object with status and message
        """
        try:
            userid = get_userid_from_header()
            try:
                request_data = json.loads(request.data)["application"]
                _ = request_data["jobTitle"]
                _ = request_data["companyName"]
            except:
                return jsonify({"error": "Missing fields in input"}), 400

            user = Users.objects(id=userid).first()
            current_application = {
                "id": get_new_application_id(userid),
                "jobTitle": request_data["jobTitle"],
                "companyName": request_data["companyName"],
                "boards.columns":request_data['exobj'],
                "date": request_data.get("date"),
                "jobLink": request_data.get("jobLink"),
                "location": request_data.get("location"),
                "status": request_data.get("status", "1"),
            }
            applications = user["applications"] + [current_application]

            user.update(applications=applications)
            return jsonify(current_application), 200
        except:
            return jsonify({"error": "Internal server error"}), 500
        
    @app.route("/getBoards", methods=["POST"])
    def get_boards():
        try:
            userid = get_userid_from_header()
            user = Users.objects(id=userid).first()

            if user:
                board = user.board  # Access the 'board' field from the user object
                if board:
                    return jsonify(board), 200
            else:
                return jsonify({"error": "User not found"}), 404

        except Exception as e:
            return jsonify({"error": "Internal server error"}), 500


    @app.route("/boards", methods=["POST"], )
    def add_boards():
        """
        Add/Update board for the user

        :return: JSON object with status and message
        """
        try:
            userid = get_userid_from_header()
            data = request.form
            data_dict = data.to_dict()
            json_string = next(iter(data_dict.keys()))
            board_data_dict = json.loads(json_string)
            print("Srj1",json_string)
            print("Srj2",type(board_data_dict["board"]))
            print("Srj3",userid)
            try:
                print("Srj4",board_data_dict["board"])
                request_data = board_data_dict["board"]
                
                # _ = request_data["boardName"]
            except:
                return jsonify({"error": "Missing fields in input"}), 400

            user = Users.objects(id=userid).first()
            if user:
                print("Srj5",user.fullName)
            user.update(board=board_data_dict["board"])
            user.save()
            print("Errrrr")
            return jsonify(board_data_dict), 200
        except:
            return jsonify({"error": "Internal server error"}), 500
        # return '1',200

    @app.route("/applications/<int:application_id>", methods=["PUT"])
    def update_application(application_id):
        """
        Updates the existing job application for the user

        :param application_id: Application id to be modified
        :return: JSON object with status and message
        """
        try:
            userid = get_userid_from_header()
            try:
                request_data = json.loads(request.data)["application"]
            except:
                return jsonify({"error": "No fields found in input"}), 400

            user = Users.objects(id=userid).first()
            current_applications = user["applications"]

            if len(current_applications) == 0:
                return jsonify({"error": "No applications found"}), 400
            else:
                updated_applications = []
                app_to_update = None
                application_updated_flag = False
                for application in current_applications:
                    if application["id"] == application_id:
                        app_to_update = application
                        application_updated_flag = True
                        for key, value in request_data.items():
                            application[key] = value
                    updated_applications += [application]
                if not application_updated_flag:
                    return jsonify({"error": "Application not found"}), 400
                user.update(applications=updated_applications)

            return jsonify(app_to_update), 200
        except:
            return jsonify({"error": "Internal server error"}), 500    

    @app.route("/applications/<int:application_id>", methods=["DELETE"])
    def delete_application(application_id):
        """
        Deletes the given job application for the user

        :param application_id: Application id to be modified
        :return: JSON object with status and message
        """
        try:
            userid = get_userid_from_header()
            user = Users.objects(id=userid).first()

            current_applications = user["applications"]

            application_deleted_flag = False
            updated_applications = []
            app_to_delete = None
            for application in current_applications:
                if application["id"] != application_id:
                    updated_applications += [application]
                else:
                    app_to_delete = application
                    application_deleted_flag = True

            if not application_deleted_flag:
                return jsonify({"error": "Application not found"}), 400
            user.update(applications=updated_applications)
            return jsonify(app_to_delete), 200
        except:
            return jsonify({"error": "Internal server error"}), 500

    @app.route("/resume", methods=["POST"])
    def upload_resume():
        """
        Uploads resume file or updates an existing resume for the user

        :return: JSON object with status and message
        """
        try:
            userid = get_userid_from_header()
            try:
                file = request.files["file"].read()
            except:
                return jsonify({"error": "No resume file found in the input"}), 400

            user = Users.objects(id=userid).first()
            if not user.resume.read():
                # There is no file
                user.resume.put(file)
                user.save()
                return jsonify({"message": "resume successfully uploaded"}), 200
            else:
                # There is a file, we are replacing it
                user.resume.replace(file)
                user.save()
                return jsonify({"message": "resume successfully replaced"}), 200
        except Exception as e:
            print(e)
            return jsonify({"error": "Internal server error"}), 500

    @app.route("/resume", methods=["GET"])
    def get_resume():
        """
        Retrieves the resume file for the user

        :return: response with file
        """
        try:
            userid = get_userid_from_header()
            try:
                user = Users.objects(id=userid).first()
                if len(user.resume.read()) == 0:
                    raise FileNotFoundError
                else:
                    user.resume.seek(0)
            except:
                return jsonify({"error": "resume could not be found"}), 400

            response = send_file(
                user.resume,
                mimetype="application/pdf",
                attachment_filename="resume.pdf",
                as_attachment=True,
            )
            response.headers["x-filename"] = "resume.pdf"
            response.headers["Access-Control-Expose-Headers"] = "x-filename"
            return response, 200
        except:
            return jsonify({"error": "Internal server error"}), 500

    return app


app = create_app()
with open("application.yml") as f:
    info = yaml.load(f, Loader=yaml.FullLoader)
    username = info["username"]
    password = info["password"]
    app.config["MONGODB_SETTINGS"] = {
        "db": "appTracker",
        "host": f"mongodb+srv://{username}:{password}@cluster0.en3fo.mongodb.net/todolistDB?retryWrites=true&w=majority",
    }
db = MongoEngine()
db.init_app(app)

#TODO change the mappings
class Users(db.Document):
    """
    Users class. Holds full name, username, password, as well as applications and resumes
    """

    id = db.IntField(primary_key=True)
    fullName = db.StringField()
    username = db.StringField()
    password = db.StringField()
    authTokens = db.ListField()
    applications = db.ListField()
    resume = db.FileField()
    board=db.ListField()

    def to_json(self):
        """
        Returns the user details in JSON object

        :return: JSON object
        """
        return {"id": self.id, "fullName": self.fullName, "username": self.username}


def get_new_user_id():
    """
    Returns the next value to be used for new user

    :return: key with new user_id
    """
    user_objects = Users.objects()
    if len(user_objects) == 0:
        return 1

    new_id = 0
    for a in user_objects:
        new_id = max(new_id, a["id"])

    return new_id + 1


def get_new_application_id(user_id):
    """
    Returns the next value to be used for new application

    :param: user_id: User id of the active user
    :return: key with new application_id
    """
    user = Users.objects(id=user_id).first()

    if len(user["applications"]) == 0:
        return 1

    new_id = 0
    for a in user["applications"]:
        new_id = max(new_id, a["id"])

    return new_id + 1


if __name__ == "__main__":
    app.run()
