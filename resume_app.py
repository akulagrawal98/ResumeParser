from flask import Flask,render_template,request,redirect,url_for,g,make_response
import sqlite3
from myparser import ResumeParse
import json
from ranker_script import cal_rank
app=Flask(__name__)


DATABASE='database.db'
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/',methods=['POST','GET'])
def home():
	if(request.method=='POST'):
		resume_name=request.form['pdf']
		fullname = request.form['fullname']
		basic_detail,resume_content=ResumeParse().get_details(resume_name)
		skills=json.dumps(basic_detail['skills']).encode('utf8')
		basic_detail['name'] = fullname

		# STORE IN DATABASE
		cur=get_db().cursor()	
		try:
			cur.execute('insert into resume(email,filename,name,mobile,cgpa,skills) values(?,?,?,?,?,?)',(basic_detail['email'],resume_name,fullname,basic_detail['mobile'],basic_detail['cgpa'],skills))

			get_db().commit()
		except:
			print("NOT SAVED")
			return render_template('home.html',file_error=True,resume_upload=True,err=True)		
	
		return render_template('home.html',file_error=True,resume_upload=False,details=basic_detail,resume_name=resume_name)
	return render_template('home.html',file_error=True,resume_upload=True,err=False)

@app.route('/search',methods=['GET','POST'])
def ranking():
	if(request.method=='POST'):
		userquery=request.form['userquery']
		skillquery=request.form['skillquery']
		cgpaquery=request.form['cgpaquery']
		cgpaweight=request.form['cgpaweight']
		queryweight=request.form['queryweight']
		skillweight=request.form['skillweight']

		try:
			cur=get_db().cursor()
			results = cur.execute('select filename,cgpa,skills from resume').fetchall()
			cgpa_list = []
			skills_list = []
			filename = []

			for tuples in results:
				cgpa_list.append(tuples[1])

				skill_set = json.loads(tuples[2])
				skill_string = ""
				for skill in skill_set:
					skill_string += skill
					skill_string += " "

				skills_list.append(skill_string)
				filename.append(tuples[0])
			# print("DATA EXTRACTED")
			# print(cgpa_list)
			# print(skills_list)
			# print(filename)
		except:
			pass
		resume_list=cal_rank(userquery, cgpaquery, skillquery, cgpa_list, skills_list, filename, float(queryweight), float(skillweight), float(cgpaweight))
		return render_template('rank_list.html',resume_list=resume_list)	
	return render_template('rank_list.html')

@app.route('/all',methods=['GET'])
def view_all():
	cur=get_db().cursor()
	results = cur.execute('select * from resume').fetchall()

	email=[]
	name=[]
	resume_name=[]
	mobile=[]
	skills=[]
	cgpa = []
	for tuples in results:
		email.append(tuples[0])
		resume_name.append(tuples[1])
		name.append(tuples[2])
		mobile.append(tuples[3])
		cgpa.append(tuples[4])
		skills.append(json.loads(tuples[5]))
	# print("THESE ARE NAMES",name)
	# return render_template('all_resumes.html',results=results)
	return render_template('all_resumes.html',email=email,resume_name=resume_name,name=name,mobile=mobile,skills=skills,cgpa=cgpa)
if __name__ == "__main__":
	app.run(debug=True)
