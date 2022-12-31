from flask import request
import configurations
import json
import pymongo
from app import app



# Models
from models.patient import Patient
from models.therapist import Therapist
from models.exercise import Exercise
from models.appointment import Appointment
from models.perform import Perform
from models.session import Session


# --------------------Therapist------------------------#
# This API will get Therapist information based on therapistId
@app.route("/therapist/information/<therapist_id>", methods=['GET'])
def therapist_information(therapist_id):
    therapist_collection = pymongo.collection.Collection(configurations.db, 'Therapist')
    therapists = therapist_collection.find({'_id': therapist_id})
    return [Therapist(**therapist).to_json() for therapist in therapists]


# This API will return the list of patients assigned for a specific therapistId
@app.route("/therapist/getPatientsByTherapistId/<therapist_id>", methods=['GET'])
def get_patients_by_therapist_id(therapist_id):
    patient_collection = pymongo.collection.Collection(configurations.db, 'Patient')
    patients = patient_collection.find({'therapistId': therapist_id})
    return [Patient(**patient).to_json() for patient in patients]


# /therapist/getPerformsForPatientByTherapist?therapist_id=x&patient_id=y
# This API will return the list of performs assigned for a specific patientId by therapistId
@app.route("/therapist/getPerformsForPatientByTherapist", methods=['GET'])
def get_performs_by_therapist_id_patient_id(therapist_id, patient_id):
    args = request.args
    therapist_id = args.get('therapist_id')
    patient_id = args.get('patient_id')
    print(therapist_id)
    print(patient_id)
    performs_collection = pymongo.collection.Collection(configurations.db, 'Performs')
    performs = performs_collection.find({'therapistId': therapist_id, 'patientId': patient_id})
    return [Perform(**perform).to_json() for perform in performs]


# This API will return the list of sessions of a specific exercise assigned by therapistId to a patientId
@app.route("/therapist/getSessionsByTherapistIdPatientIdExerciseName/<therapist_id>/<patient_id>/<exercise_name>",
           methods=['GET'])
def get_sessions_by_therapist_id_patient_id_exerciseName(therapist_id, patient_id, exercise_name):
    session_collection = pymongo.collection.Collection(configurations.db, 'Session')
    sessions = session_collection.find(
        {'therapistId': therapist_id, 'patientId': patient_id, 'exerciseName': exercise_name})
    return [Session(**session).to_json() for session in sessions]


# This API will update session and add comment based on session_id
@app.route("/therapist/addCommentToSession/<session_id>", methods=['PATCH'])
def add_session_comment(session_id):
    session_collection = pymongo.collection.Collection(configurations.db, 'Session')
    updated_doc = session_collection.update_one({"_id": session_id}, {"$set": request.get_json()})
    if updated_doc:
        return "updated"
    else:
        return "error"


# This API will add a new perform to patientId by therapistId
@app.route("/therapist/addNewPerform", methods=['POST'])
def add_new_perform():
    try:
        performs_collection = pymongo.collection.Collection(configurations.db, 'Performs')
        info = json.loads(request.data)
        therapist_id = info.get('therapistId', '')
        patient_id = info.get('patientId', '')
        exercise_id = info.get('exerciseName', '')
        perform_id = therapist_id + "_" + patient_id + "_" + exercise_id
        raw_performs = request.get_json()
        perform = Perform(**raw_performs)
        perform.id = perform_id
        performs_collection.insert_one(perform.to_bson())
        return "true"
    except Exception as e:
        print(e)
        return "Error"


@app.route("/therapist/appointments", methods=['GET'])
def therapist_appointment():
    appointment_collection = pymongo.collection.Collection(configurations.db, 'Appointment')
    info = json.loads(request.data)
    therapist_id = info.get('therapistId', '')
    appointment = appointment_collection.find({'therapistId': therapist_id, 'status': "accepted"})
    print(appointment)
    return [Appointment(**appointment).to_json() for appointment in appointment]


# This API will return the pending appointments for a specific therapistId
@app.route("/therapist/appointments/pending", methods=['GET'])
def therapist_pending_appointment():
    appointment_collection = pymongo.collection.Collection(configurations.db, 'Appointment')
    info = json.loads(request.data)
    therapist_id = info.get('therapistId', '')
    appointment = appointment_collection.find({'therapistId': therapist_id, 'status': "pending"})
    print(appointment)
    return [Appointment(**appointment).to_json() for appointment in appointment]


# This API will update appointment status for a specific therapistId
@app.route("/therapist/appointments/updateStatus/<appointment_id>", methods=['PATCH'])
def therapist_update_appointment(appointment_id):
    appointment_collection = pymongo.collection.Collection(configurations.db, 'Appointment')
    appointment = appointment_collection.update_one({'_id': appointment_id}, {"$set": request.get_json()})
    if appointment:
        return "updated"
    else:
        return "error"


# This API will return the exercises that can be added to a patient by the therapist without
# any duplication between these available exercises and the ones found in the performs
@app.route("/therapist/exercises/viewNewToAdd/<therapist_id>/<patient_id>", methods=['GET'])
def view_new_exercises_to_add(therapist_id, patient_id):
    # Three Steps:
    # 1- get the therapyType of the therapist,
    # 2- get exerciseId from performs by patientId and therapistId
    # 3- get exercises by therapyType, subtract those found in step 2
    # --------------------------- #
    therapist_collection = pymongo.collection.Collection(configurations.db, 'Therapist')
    therapist = therapist_collection.find_one({'_id': therapist_id})
    exerciseType = therapist['speciality']
    # --------------------------- #
    performs_collection = pymongo.collection.Collection(configurations.db, 'Performs')
    performs = performs_collection.find({'therapistId': therapist_id, 'patientId': patient_id})
    chosen_exercises = []
    for perform in performs:
        chosen_exercises.append(perform['exerciseName'])
    # --------------------------- #
    exercise_collection = pymongo.collection.Collection(configurations.db, 'Exercise')
    exercises = exercise_collection.find({'exerciseType': exerciseType})
    output_exercises = []
    print(chosen_exercises)
    print('---------------------------------------')
    for exercise in exercises:
        if exercise['exerciseName'] not in chosen_exercises:
            print(exercise['exerciseName'])
            output_exercises.append(exercise)

    return [Exercise(**exercise).to_json() for exercise in output_exercises]

    return ""
