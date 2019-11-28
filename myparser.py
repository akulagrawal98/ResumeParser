import os
import spacy
from spacy.matcher import Matcher
import utils
import re
import pandas as pd

class ResumeParse():
	def clean_project(self,project_text):
		temp=project_text
		content2=re.sub(r'\w{3,9}?\s\d{1,2},?\s\d{4}?',"",temp)
		content2=re.sub(r'\w{3}.?\s\d{1,2},?\s\d{4}?',"",content2)
		content2=re.sub(r'Key Skills:|\sMentor:|Team Size:|\s-\s|\d{1}|\s\|\s',"",content2)
		return content2

	def get_skills(self,skill_text):
		data = pd.read_csv(os.path.join(os.path.dirname(__file__), 'skills.csv')) 
		skills = list(data.columns.values)
		final_skill=[]
		skill_list=skill_text.split()
		skill_len=len(skill_list)

		flag=0
		prev=0
		for i in range(skill_len-1):	
			if(prev==1):
				prev=0
				continue
			else:
				skill=skill_list[i].lower()+" "+skill_list[i+1].lower()
				if skill in skills:
					s=skill_list[i]+" "+skill_list[i+1]
					final_skill.append(s)
					prev=1
				else:
					if(i==skill_len-2):
						flag=1
					final_skill.append(skill_list[i])
		if(flag==1):
			final_skill.append(skill_list[skill_len-1])
		return final_skill


	def get_details(self,resume_name):
		resume_path="Resumes/"+resume_name
		ext="pdf"
		nlp=spacy.load('en_core_web_sm')
		matcher = Matcher(nlp.vocab)
		text_raw=utils.extract_text(resume_path, '.' + ext)
		text= ' '.join(text_raw.split())
		array=text.split()

		topics=[]
		field_list=['OVERVIEW / CAREER OBJECTIVE / SUMMARY','KEY EXPERTISE / SKILLS','EDUCATION','AWARDS AND SCHOLARSHIPS','INTERNSHIPS','PROJECTS','ACHIEVEMENTS','SEMINARS / TRAININGS / WORKSHOPS','CO-CURRICULAR ACTIVITIES','EXTRA CURRICULAR ACTIVITIES','PERSONAL INTERESTS / HOBBIES','WEB LINKS','PERSONAL DETAILS']
		for word in field_list:
			if(text.find(word)>=0):
				topics.append(word)

		content={}
		total_topics=len(topics)
		for i in range(total_topics-1):
			string_to_find=topics[i]+'(.*)'+topics[i+1]
			result = re.search(string_to_find, text)
			content[topics[i]]=result.group(1)
		temp=topics[total_topics-1]+'(.*)'
		temp_res=re.search(temp, text)
		content[topics[total_topics-1]]=temp_res.group(1)
		
		__full_text=nlp(text)

		actual_marks = "CGPA: "+'(.*)'+"/ 10.00"
		cgpa = re.search(actual_marks, content['EDUCATION'])
		
		# DOMAIN RANKING
		rank_text=content['KEY EXPERTISE / SKILLS']+content['PROJECTS']
		project_text=ResumeParse().clean_project(rank_text)

		file_name="rank/"+resume_name.split('.')[0]+".txt"
		f=open(file_name,"w+")
		f.write(project_text)
		f.close()

		#FOR SKILLS
		skills=ResumeParse().get_skills(content['KEY EXPERTISE / SKILLS'])

		# name=utils.extract_name(__full_text,matcher)
		email= utils.extract_email(text)
		mobile= utils.extract_mobile_number(text)
		details={}
		# details['name']=name
		details['email']=email
		details['mobile']=mobile
		details['skills']=skills
		details['cgpa'] = cgpa.group(1)
		return details,content
