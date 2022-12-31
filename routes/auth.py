import hashlib
import secrets
import string
from flask import request
import configurations
import pymongo
from app import app

from models.user import UserLoginRequest, User, UserLoginResponse


# !!!!!!!!!!!Need to do the hashing for the password in the frontend side!!!!!!!!!
# Login for any user (admin, patient, therapist)
# if returned_type = 0->admin, 1->therapist, 2->patient
@app.route("/login", methods=['POST'])
def login_user():
    try:
        print("We are in the login")
        # pass
        raw_user = request.get_json()
        print("---->",raw_user['_id'])
        user = UserLoginRequest(**raw_user)
        user_collection = pymongo.collection.Collection(configurations.db, 'User')
        db_user = user_collection.find_one({'_id': user.id})
        # db_user = User(**db_user)
        if db_user['password'] == hashlib.md5(user.password.encode()).hexdigest():
            print("Generating a new token:\n")
            new_token = generate_new_token()
            user_collection.update_one({"_id": db_user['_id']}, {"$set": {"token": new_token}})
            raw_response = {"_id": db_user['_id'], "token": new_token, "user_type":db_user['user_type']}
            response = UserLoginResponse(**raw_response)
            return response.to_json()
        else:
            return "unauthorized"
    except Exception as e:
        print(e)
        return "Already used username, try another one!"


def generate_new_token():
    N = 16
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits)
                   for i in range(N))
