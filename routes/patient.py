import flask
import configurations
import json
import pymongo
from flask import *
from app import app


# Models
from models.patient import Patient
from models.therapist import Therapist
from models.exercise import Exercise
from models.appointment import Appointment
from models.perform import Perform


# --------------------Patient------------------------#
# We are now in the Patient APIs according to the plan:
# This API gets all patient information based on the patient's id
@app.route("/patient/information/<patient_id>", methods=['GET'])
def patient_information(patient_id):
    print("We are trying to get patient information\n")
    patient_collection = pymongo.collection.Collection(configurations.db, 'Patient')
    patient = patient_collection.find_one({'_id': patient_id})
    return Patient(**patient).to_json()


@app.route("/patient/infoAll", methods=['GET'])
def patient_information_all():
    patient_collection = pymongo.collection.Collection(configurations.db, 'Patient')
    patients = patient_collection.find()
    return [Patient(**patient).to_json() for patient in patients]


# This API will update patient's data based on patient id
@app.route("/patient/updateInfo/<passed_id>", methods=['PATCH'])
def update_patient_info(passed_id):
    patient_collection = pymongo.collection.Collection(configurations.db, 'Patient')
    updated_doc = patient_collection.update_one({"_id": passed_id}, {"$set": request.get_json()})
    if updated_doc:
        return "updated"
    else:
        flask.abort(404, "Patient Not Found")


# This API will get Exercise information based on exerciseName
@app.route("/patient/exerciseInformation/<exercise_name>", methods=['GET'])
def exercise_information(exercise_name):
    exercise_collection = pymongo.collection.Collection(configurations.db, 'Exercise')
    exercises = exercise_collection.find({'exerciseName': exercise_name})
    return [Exercise(**exercise).to_json() for exercise in exercises]


# This API will return the appointments for a specific patientId
@app.route("/patient/appointment", methods=['GET'])
def patient_appointment():
    appointment_collection = pymongo.collection.Collection(configurations.db, 'Appointment')
    info = json.loads(request.data)
    patient_id = info.get('patientId', '')
    appointment = appointment_collection.find({'patientId': patient_id})
    print(appointment)
    return [Appointment(**appointment).to_json() for appointment in appointment]


# This API will return the list of therapists assigned for a specific patientId
@app.route("/patient/getTherapistByPatientId//<patient_id>", methods=['GET'])
def get_therapist_by_patient_id(patient_id):
    therapist_collection = pymongo.collection.Collection(configurations.db, 'Therapist')
    therapists = therapist_collection.find({'patientId': patient_id})
    return [Therapist(**therapist).to_json() for therapist in therapists]


# This API will return the available appointment slots for a specific therapistId
@app.route("/patient/getSlotsByTherapistId/<therapist_id>", methods=['GET'])
def get_slots_by_therapist_id(therapist_id):
    appointment_collection = pymongo.collection.Collection(configurations.db, 'Appointment')
    appointments = appointment_collection.find({'therapistId': therapist_id, 'status': 'available'})
    return [Appointment(**appointment).to_json() for appointment in appointments]


# This API will update appointment's status and add patientId based on appointment id
@app.route("/patient/appointment/updateStatusPending/<appointment_id>/<patient_id>", methods=['PATCH'])
def update_appointment_pending(appointment_id, patient_id):
    appointment_collection = pymongo.collection.Collection(configurations.db, 'Appointment')
    updated_doc = appointment_collection.update_one({"_id": appointment_id},
                                                    {"$set": {"patientId": patient_id, "status": "pending"}})
    if updated_doc:
        return "updated"
    else:
        flask.abort(404, "Patient Not Found")


# This API will add a new appointment by patient to be in the pending state
@app.route("/patient/appointment/addPending", methods=['POST'])
def add_pending_appointment():
    appointment_collection = pymongo.collection.Collection(configurations.db, 'Appointment')
    raw_appointment = request.get_json()
    appointment = Appointment(**raw_appointment)
    appointment_collection.insert_one(appointment.to_bson())
    return appointment.to_json()


# This API will get all the exercises that a patient should perform
@app.route("/patient/getPerformsByPatientId/<patient_id>", methods=['GET'])
def get_performs_patient_id(patient_id):
    perform_collection = pymongo.collection.Collection(configurations.db, 'Performs')
    performs = perform_collection.find({'patientId': patient_id})
    return [Perform(**perform).to_json() for perform in performs]
