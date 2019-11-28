import sqlite3
from sqlite3 import Error
conn=sqlite3.connect('database.db')
print("Opened Successfully")

def create_connection(db_file):
	conn=None
	try:
		conn=sqlite3.connect(db_file)
		return conn
	except Error as e:
		print(e)
	return conn

def create_table(conn,table_detail):
	try:
		c=conn.cursor()
		c.execute(table_detail)
	except Error as e:
		print(e)

def main():
	database='database.db'
	resume_attr="""CREATE TABLE IF NOT EXISTS resume(
		email text primary key,
		filename text not null,
		name text not null,
		mobile integer not null,
		cgpa real not null,
		skills json not null
		);"""
	conn=create_connection(database)
	if conn is not None:
		create_table(conn,resume_attr)
		print("Successfully Created")
	else:
		print("NOT POSSIBLE to create")
	conn.close()

if __name__ == '__main__':
	main()