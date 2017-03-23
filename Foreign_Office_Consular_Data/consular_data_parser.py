import csv
import sqlite3 as lite
import os
from datetime import datetime
FOLDER_LIST = ["2016","2017"]
DATABASE_NAME = "Consolar-data"

class Database:
	def __init__(self, folder_name):
		file_location = os.path.dirname(os.path.realpath(__file__)) + "\\"
		file_name = folder_name+".sqlite"
		self.sqlite_file = file_location + file_name
		self.conn = None
		self.cur = None
		self.create_tables()

	def create_tables(self):
		conn = lite.connect(self.sqlite_file)
		cur = conn.cursor()
		try:
			cur.execute (''' CREATE TABLE City (id INTEGER PRIMARY KEY, name VARCHAR(100) UNIQUE) ''')

			cur.execute(''' CREATE TABLE CaseTypes (id INTEGER PRIMARY KEY
																, casetype VARCHAR(255)
																, subtype VARCHAR(255)
																, UNIQUE (casetype,subtype) ON CONFLICT ABORT ) ''')

			cur.execute(''' CREATE TABLE CityCases (cityid INTEGER
												, casetypeid INTEGER
												, created DATE
												, amount INTEGER
												, upto BIT
												, UNIQUE (cityid, casetypeid, created) ON CONFLICT ABORT ) ''')

		except lite.IntegrityError:
			print('ERROR: Unable to create tables {}'.format(id))
			cur.close()

		conn.commit()
		cur.close()

	def add_city(self, _name):
		city_id = None

		try:
			sql = ''' INSERT INTO City (name) VALUES (?) '''
			task = (_name,)
			self.cur.execute(sql, task)
			city_id = self.cur.lastrowid

		except lite.IntegrityError:
			print('ERROR: ID already exists in the campaign tables id column {}'.format(_name))

		return city_id

	def add_casetype(self, _type, _subtype = None):
		case_type_id = None

		try:
			sql = ''' INSERT INTO CaseTypes (casetype,subtype) VALUES (?,?) '''
			task = (_type,_subtype)
			self.cur.execute(sql, task)
			case_type_id = self.cur.lastrowid

		except lite.IntegrityError:
			print('ERROR: type:subtype combo already exists in the casetype tables. {} : {}'.format(_type, _subtype))

		return case_type_id

	def add_citycase(self, _cityid, _casetypeid, _created, _amount, _upto = False):
		try:
			sql = ''' INSERT INTO CityCases (cityid, casetypeid, created, amount, upto) VALUES (?,?,?,?,?) '''
			task = (_cityid, _casetypeid, _created, _amount, _upto)
			self.cur.execute(sql, task)
			case_type_id = self.cur.lastrowid

		except lite.IntegrityError:
			print('ERROR: _cityid:_casetypeid combo already exists in the citycase tables. {} : {}'.format(_cityid, _casetypeid))

		return True

	def open_connection(self):		
		self.conn = lite.connect(self.sqlite_file)
		self.cur = self.conn.cursor()

	def close_connection(self):		
		self.conn.commit()
		self.cur.close()

def generate_database():
	try:
		consular_database = Database(DATABASE_NAME)
	except:
		raise Exception('Database already exist, change the DATABASE_NAME, or delete/rename the existing one. "' + DATABASE_NAME+'.sqlite"')
	column_lookup = {} # check against previously created columns for inconsistency between docs
	city_lookup = {} # same for cities
	for FOLDER_NAME in FOLDER_LIST:
		#FOLDER_NAME = "2016"
		filelist = []
		try:
			for file in os.listdir(FOLDER_NAME):
				if file.endswith(".csv"):
					filelist.append(file)
		except:
			print("Folder failed to open. Skipping. Does it exist? '" + FOLDER_NAME +"'")

		for file in filelist:
			consular_database.open_connection()
			cvfile = open(FOLDER_NAME + "/" +file, "rt")
			reader = csv.reader(cvfile, delimiter=',')
			first_row = next(reader)
			#date is in top left corner of csv
			try:
				created = datetime.strptime(first_row[0] + "-" + FOLDER_NAME, '%b-%d-%Y')
			except:
				raise ValueError('Bad date in document: ' + file)

			for item in first_row[1:]:
				if item in column_lookup.keys():
					continue

				types = item.split(">")
				if len(types) == 1:
					column_lookup[item] = consular_database.add_casetype(types[0])
				elif len(types) == 2:
					column_lookup[item] = consular_database.add_casetype(types[0],types[1])
				else:
					raise ValueError('Invalid amount of parameters for adding a case type. Should be 1 or 2.')

			for row in reader:
				if row[0] in city_lookup.keys():
					city_id = city_lookup[row[0]]
				else:
					city_id = consular_database.add_city(row[0])
					city_lookup[row[0]] = city_id

				for index, item in enumerate(row[1:]):
					# indexes ater offset by 1 because we start one later
					case_id = column_lookup[first_row[index+1]]
					amount = 0
					upto_flag = False
					if item == "<=5":
						amount = 5
						upto_flag = True
					else:
						try:
							amount = int(item)
						except:
							print("Adding to CityCases value ignored: '" + item
								+"' for (" +row[0] +" : " + first_row[index+1]
								+") in "+ file )
					if(amount > 0):
						consular_database.add_citycase(city_id, case_id, created, amount, upto_flag)

			consular_database.close_connection()

if __name__ == "__main__":
	generate_database()
