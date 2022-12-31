import flask
import configurations
import json
import pymongo
from flask import *
from app import app


# Models
from models.patient import Patient
from models.therapist import Therapist

import hashlib


# --------------------Admin------------------------#
# The admin can sign up a new therapist after passing the data through the request body
@app.route("/admin/therapist/signup", methods=['POST'])
def signup_therapist():
    try:
        therapist_collection = pymongo.collection.Collection(configurations.db, 'Therapist')
        raw_therapist = request.get_json()
        therapist = Therapist(**raw_therapist)
        add_user(therapist.id, hashlib.md5(therapist.password.encode()).hexdigest(), "1")
        therapist_collection.insert_one(therapist.to_bson())
        return therapist.to_json()
    except Exception as e:
        print(e)
        return "Already used username, try another one!"

# sigun up --> username --> password (12344) --> md5 --> azhstte563 -->
# The admin can sign up a new patient after passing the data through the request body
@app.route("/admin/patient/signup", methods=['POST'])
def signup_patient():
    try:
        patient_collection = pymongo.collection.Collection(configurations.db, 'Patient')
        raw_patient = request.get_json()
        patient = Patient(**raw_patient)
        add_user(patient.id, hashlib.md5(patient.password.encode()).hexdigest(), "2")
        patient_collection.insert_one(patient.to_bson())
        return patient.to_json()
    except Exception as e:
        print(e)
        return "Already used username, try another one!"


def add_user(username, password, user_type):
    user_collection = pymongo.collection.Collection(configurations.db, 'User')
    passed_info = {'_id': username, 'password': password, 'user_type': user_type}
    user_collection.insert_one(passed_info)


# This API would get all the therapists based on the passed clinic id and the therapy type
# It will be used mainly in the signup of the patient, as we need a drop list with all possible therapist
@app.route("/admin/therapistsByClinicIdAndTherapyType", methods=['GET'])
def therapists_clinic_id_therapy_type():
    token = request.headers.get('Authorization')
    print(token)
    if authorization("333", token):
        info = json.loads(request.data)
        clinicId = info.get('clinicId', '')
        speciality = info.get('speciality', '')

        therapist_collection = pymongo.collection.Collection(configurations.db, 'Therapist')

        therapists = therapist_collection.find({'clinicId': clinicId, 'speciality': speciality})
        return [Therapist(**therapist).to_json() for therapist in therapists]
    return "Not Authorized"


# This API will get all patients based on the clinic ID
@app.route("/admin/patientsByClinicId/<passed_id>", methods=['GET'])
def patients_clinic_id(passed_id):
    patient_collection = pymongo.collection.Collection(configurations.db, 'Patient')
    clinicId = passed_id
    patients = patient_collection.find({'clinicId': clinicId})
    return [Patient(**patient).to_json() for patient in patients]


# This API will update patient's data based on patient id
@app.route("/admin/updatePatient/<passed_id>", methods=['PATCH'])
def update_patient(passed_id):
    patient_collection = pymongo.collection.Collection(configurations.db, 'Patient')
    patientId = passed_id
    updated_doc = patient_collection.update_one({"_id": patientId}, {"$set": request.get_json()})
    if updated_doc:
        return "updated"
    else:
        flask.abort(404, "Patient Not Found")


# This API will update therapist's data based on therapist id
@app.route("/admin/updateTherapist/<passed_id>", methods=['PATCH'])
def update_therapist(passed_id):
    therapist_collection = pymongo.collection.Collection(configurations.db, 'Therapist')
    therapistId = passed_id
    updated_doc = therapist_collection.update_one({"_id": therapistId}, {"$set": request.get_json()})
    if updated_doc:
        return "updated"
    else:
        flask.abort(404, "Patient Not Found")


# This API will delete a patient based on its id
@app.route("/admin/deletePatient/<passed_id>", methods=['DELETE'])
def delete_patient(passed_id):
    # delete from user collection
    user_collection = pymongo.collection.Collection(configurations.db, 'User')
    user_collection.delete_one({'_id': passed_id})
    # delete from therapist collection
    therapist_collection = pymongo.collection.Collection(configurations.db, 'Therapist')
    therapist_collection.update_many(
        {},
        {'$pull': {'patientId': passed_id}}
    )
    # delete from patient collection
    patient_collection = pymongo.collection.Collection(configurations.db, 'Patient')
    patient_collection.delete_one({'_id': passed_id})
    return "deleted"


# This API will delete a therapist based on its id
@app.route("/admin/deleteTherapist/<passed_id>", methods=['DELETE'])
def delete_therapist(passed_id):
    # delete from user collection
    user_collection = pymongo.collection.Collection(configurations.db, 'User')
    user_collection.delete_one({'_id': passed_id})
    # delete from patient collection
    patient_collection = pymongo.collection.Collection(configurations.db, 'Patient')
    patient_collection.update_many(
        {},
        {'$pull': {'therapistId': passed_id}}
    )
    # delete from therapist collection
    therapist_collection = pymongo.collection.Collection(configurations.db, 'Therapist')
    therapist_collection.delete_one({'_id': passed_id})
    return "deleted"


# This API will get all patients for a specific therapist id
@app.route("/admin/getPatientByTherapistId/<passed_id>", methods=['GET'])
def get_patient_by_therapist_id(passed_id):
    patient_collection = pymongo.collection.Collection(configurations.db, 'Patient')
    patients = patient_collection.find({'therapistId': passed_id})
    return [Patient(**patient).to_json() for patient in patients]


# This API will remove a specific patient from a specific therapist
@app.route("/admin/deletePatientFromTherapist/<therapist_id>/<patient_id>", methods=['DELETE'])
def delete_patient_from_therapist(therapist_id, patient_id):
    # Remove from the patient id, the therapist id
    patient_collection = pymongo.collection.Collection(configurations.db, 'Patient')
    patient_collection.update_many(
        {'_id': patient_id},
        {'$pull': {'therapistId': therapist_id}}
    )
    # Remove from the therapist id, the patient id
    therapist_collection = pymongo.collection.Collection(configurations.db, 'Therapist')
    therapist_collection.update_many(
        {'_id': therapist_id},
        {'$pull': {'patientId': patient_id}}
    )
    return "deleted"


# This API will add a patient to a specific therapist
@app.route("/admin/addPatientToTherapist/<therapist_id>/<patient_id>", methods=['PATCH'])
def add_patient_to_therapist(therapist_id, patient_id):
    # add the therapist to this patient
    patient_collection = pymongo.collection.Collection(configurations.db, 'Patient')
    patient_collection.update_many(
        {'_id': patient_id},
        {'$push': {'therapistId': therapist_id}}
    )
    # add the patient to the therapist's list
    therapist_collection = pymongo.collection.Collection(configurations.db, 'Therapist')
    therapist_collection.update_many(
        {'_id': therapist_id},
        {'$push': {'patientId': patient_id}}
    )
    return "Added"
