from flask import Flask, request, jsonify, render_template, session, send_file
from python_resumable import UploaderFlask
from flask_redis import FlaskRedis

import json
import urllib.request
import os
import shutil
import csv
import time
import datetime

app = Flask(__name__)

app.config['SECRET_KEY'] = '1@$5323as24d'
app.config['REDIS_URL'] = "redis://localhost:6379/0"

redis_client = FlaskRedis(app)


UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static/uploads')
TEMP_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static/temp')


@app.route("/",methods=['GET'])
def home():
	if request.method == 'GET':
		return render_template('index.html')


@app.route("/api/upload",methods=['POST'])
def baseline_upload_start():
    resumable_dict = {
        'resumableIdentifier': request.form.get('resumableIdentifier'),
        'resumableFilename': request.form.get('resumableFilename'),
        'resumableTotalSize': request.form.get('resumableTotalSize'),
        'resumableTotalChunks': request.form.get('resumableTotalChunks'),
        'resumableChunkNumber': request.form.get('resumableChunkNumber')
        }
    session['lastFileIdentifier'] = request.form.get('resumableIdentifier')

    #Create Resumable object and start uploading
    resumable = UploaderFlask(resumable_dict,UPLOAD_FOLDER,TEMP_FOLDER,request.files['file'])
    resumable.upload_chunk()

    #Assemble downloaded chunks when complete
    if resumable.check_status() is True:
        resumable.assemble_chunks()
        return jsonify({"fileUploadStatus": True,"resumableIdentifier": resumable.repo.file_id})

    return jsonify({"chunkUploadStatus": True,"resumableIdentifier": resumable.repo.file_id})

@app.route('/api/upload/cancel',methods=['POST'])
def baseline_upload_cancel():
	try:
		#Delete the folder containing the downloaded chunks from temp
		shutil.rmtree(os.path.join(TEMP_FOLDER,session['lastFileIdentifier']))
		print("Successfully deleted temp chunks of cancelled upload")
	except Exception as e:
		print(str(e))
		return jsonify({"status":"error","message":"exception "+str(e)+" occurred"})

	return jsonify({"status":"success","message":"cancelled upload and deleted uploaded chunks"})


@app.route("/api/export/new",methods=['GET'])
def export_data_start():

	redis_client.set("export_operation_status","True".encode('utf-8'))
	
	mylist = []
	ctr = 0
	i = 0

	#from_date = request.form.get('from_date')
	#The above statement would be getting user input date, but here I have assumed and taken a random input date
	from_date = '2020-01-01 21:00'
	user_datetime_obj = datetime.datetime.strptime(from_date, '%Y-%m-%d %H:%M')

	current_datetime = str(datetime.datetime.utcnow())[0:16]
	current_datetime_obj = datetime.datetime.strptime(current_datetime, '%Y-%m-%d %H:%M')

	duration = current_datetime_obj - user_datetime_obj
	days  = duration.days

	#To fill dummy data I am just filling it with numbers from 0 till number of days
	while i < days:
		#If the export operation is cancelled midway
		if redis_client.get('export_operation_status').decode('utf-8') == 'False':
			break
		#If the export operation is paused 
		if redis_client.get('export_operation_status').decode('utf-8') == 'Pause':
			while redis_client.get('export_operation_status').decode('utf-8') == 'Pause':
				ctr = ctr+1
				#If the export operation is paused for a long time i.e. 10000 ctr value (assumed) then cancel operation
				if ctr == 10000:
					redis_client.set("export_operation_status","False".encode('utf-8'))
					break
			i = i-1
		#To simulate real situation where it would take a lot of time I am manually making the process slow
		time.sleep(2)
		mylist.append(i)
		i = i+1

	if redis_client.get('export_operation_status').decode('utf-8') == 'True':
		with open('Ex_data.csv', 'w', newline='') as myfile:
			wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
			wr.writerow(mylist)
		return send_file('Ex_data.csv',mimetype='text/csv',attachment_filename='Ex_data.csv',as_attachment=True,cache_timeout=0)
	return jsonify({"status":"success","message":"operation stopped"})

@app.route("/api/export/status/toggle",methods=['PUT'])
def export_data_status_toggle():
	cur_status = redis_client.get('export_operation_status').decode('utf-8')
	#Toggle operation status based on current status
	if cur_status == 'Pause':
		redis_client.set("export_operation_status","True".encode('utf-8'))
	elif cur_status == 'True':
		redis_client.set("export_operation_status","Pause".encode('utf-8'))
	return jsonify({"status":"success","message":"toggled current export status"})

@app.route("/api/export/cancel",methods=['PUT'])
def export_data_cancel():
	redis_client.set("export_operation_status","False".encode('utf-8'))
	return jsonify({"status":"success","message":"cancelled export operation"})


@app.route("/api/bulk_teams/create",methods=['GET'])
def create_bulk_teams():
	redis_client.set("team_operation_status","True".encode('utf-8'))
	#Store the value of the last created team in Redis so that it can be used while deleting if reqd.
	redis_client.set("last_team_created","0".encode('utf-8'))
	no_of_teams = int(request.args.get('no_of_teams'))

	ctr = 0
	i = 0

	while i < no_of_teams:
		if redis_client.get('team_operation_status').decode('utf-8') == 'True':
			create_team(i)
			redis_client.set("last_team_created",str(i).encode('utf-8'))
			#To simulate real situation where it would take a lot of time I am manually making the process slow
			time.sleep(2)

		elif redis_client.get('team_operation_status').decode('utf-8') == 'Pause':
			while redis_client.get('team_operation_status').decode('utf-8') == 'Pause':
				ctr = ctr+1
				#To simulate real situation where it would take a lot of time I am manually making the process slow
				time.sleep(2)
				if ctr == 10000:
					redis_client.set("team_operation_status","False".encode('utf-8'))
					break
			i = i-1
			
		else:
			break
		i = i+1
	if redis_client.get('team_operation_status').decode('utf-8') == 'True':
		return jsonify({"status":"success","message":"created all the teams"})
	return jsonify({"status":"success","message":"operation cancelled"})

@app.route("/api/bulk_teams/status/toggle",methods=['PUT'])
def bulk_teams_status_toggle():
	cur_status = redis_client.get('team_operation_status').decode('utf-8')
	#Toggle operation status based on current status
	if cur_status == 'Pause':
		redis_client.set("team_operation_status","True".encode('utf-8'))
	elif cur_status == 'True':
		redis_client.set("team_operation_status","Pause".encode('utf-8'))
	return jsonify({"status":"success","message":"toggle team status"})


@app.route("/api/bulk_teams/cancel",methods=['PUT'])
def bulk_teams_cancel():
	redis_client.set("team_operation_status","False".encode('utf-8'))
	last_team_created = int(redis_client.get('last_team_created').decode('utf-8'))
	for i in range(last_team_created+1):
		remove_team(i)
	return jsonify({"status":"success","message":"cancelled team creation and deleted created teams"})

def create_team(i):
	print("Creating team number : "+str(i))

def remove_team(i):
	print("Removing created team : "+str(i))

if __name__ == "__main__":
    app.run()
