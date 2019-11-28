import nltk
import math
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer,PorterStemmer
from scipy import spatial
import glob
import re
from nltk.tokenize import RegexpTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def cal_gpa_rank(query, gpaScore):
	diff_list = []
	for cgpa in gpaScore:
		diff_list.append((cgpa-(float(query)))/10)
	return diff_list

def cal_skill_rank(query, skills_list):
	tokenizer = RegexpTokenizer(r'\w+')
	vectorizer = TfidfVectorizer()
	X= vectorizer.fit_transform(skills_list)
	# print(vectorizer.get_feature_names())

	#USER INPUT
	query_string=query

	query_list=[]
	query_list.append(query_string)
	query_vec= vectorizer.transform(query_list)

	cosine=cosine_similarity(X, query_vec, dense_output=True)
	return cosine

def cal_project_rank(query, filenameList):
	tokenizer = RegexpTokenizer(r'\w+')
	filename_list=[]
	doc_collection=[]
	original_docs=[]

	for files in filenameList:
		file_path = "rank/"+files.split(".")[0]+".txt"
		f=open(file_path,"r")
		content=f.read()
		original_docs.append(content)

	vectorizer = TfidfVectorizer()
	X= vectorizer.fit_transform(original_docs)

	#USER INPUT
	query_string=query

	query_list=[]
	query_list.append(query_string)
	query_vec= vectorizer.transform(query_list)

	cosine=cosine_similarity(X, query_vec, dense_output=True)
	return cosine

def cal_rank(query, cgpaQuery, skillQuery, gpaScore, skillList, filenameList, projectWeight, skillWeight, gpaWeight):

	# GET THE INDIVIDUAL COSINE
	project_vec = cal_project_rank(query, filenameList)
	skill_vec = cal_skill_rank(skillQuery, skillList)
	gpa_vec = cal_gpa_rank(cgpaQuery, gpaScore)

	#  GET AGGREGATE
	total_weight = skillWeight + projectWeight + gpaWeight
	final_rank_vec = []
	for i in range(len(gpa_vec)):
		final_skill = skill_vec[i,0]*skillWeight
		final_project = project_vec[i,0]*projectWeight
		final_cgpa = gpa_vec[i]*gpaWeight
		final_rank_vec.append((final_skill+final_cgpa+final_project)/total_weight)
	resume_rank = []
	for i in range(5):
		max_value = max(final_rank_vec)
		index = final_rank_vec.index(max_value)
		resume_rank.append(filenameList[index])
		final_rank_vec[index] = -2
	return resume_rank