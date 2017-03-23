import csv
#import sqlite as lite
'''
Generates two text file lists of INSERT SQL statements for a data-set from 
https://figshare.com/articles/Chandler_Population_Data/2059494
Single use code, but might useful as a reference
Notes:
city_id|year combination for population data can generate duplicates 
(I just manually remove them while while inserting into the database)
**Not to be used for user input**
'''
def get_duplicates(the_list):
	'''
	Found http://stackoverflow.com/a/1541820
	Modified for a scenario, at this point bares almost no resemblance to the orginal...
	Returns a dictionary with the duplicate as the key 
	and all the duplicate index locations in a list as the value
	'''
	seen = {}
	duplicates = {}
	for counter, item in enumerate(the_list):
		if item in seen:
			if item in duplicates:
				duplicates[item].append(counter)
			else:
				duplicates[item] = [seen[item],counter]
		else:
			seen[item] = counter
	return duplicates

def get_csv_duplicates(file_name,*args):
	'''
	INPUT: file, *INT (as many columns as you want)
	combines any number of columns to create a unique hash to compares against itself
	and then uses get_duplicates to return a dictionary with the unique hash and indexes
	of duplicates.
	Dictionary returned format: {"|foo|bar":[1,4,6]}
	'''

	cvfile = open(file_name, "rb")
	reader = csv.reader(cvfile, delimiter=',')
	unique_hash_list = []
	for row in reader:
		unique_hash = ""
		for arg in args:
			if arg <= len(row) and arg >= 0:
				unique_hash += "|" + str(row[arg]) #added | for readability
			else:
				raise ValueError('Invalid CSV Column: ' + str(arg) +" Min|Max Column length: "+ "0|"+str(len(row)))
		unique_hash_list.append(unique_hash)

	return get_duplicates(unique_hash_list)

def generate_inserts():	

	'''rb is for reading a file, and w is for writing'''
	FILENAME = "chandlerV2.csv"
	cvfile = open(FILENAME, "rb")
	reader = csv.reader(cvfile, delimiter=',')
	cities_text_file = open("OutputCities.txt", "w")
	population_text_file = open("OutputPopulation.txt", "w")

	cities_sql = '''INSERT INTO Cities(CityId, CityName, OtherName, Country, Latitude, Longitude) VALUES ( {}, {}, {}, {}, {}, {})'''
	population_sql = '''INSERT INTO CityPopulation(CityId, Year, Population, Certainty) VALUES ( {}, {}, {}, {})'''

	dup_columns = [0,2]
	duplicates = get_csv_duplicates(FILENAME, *dup_columns)
	title_row = []

	for counter, row in enumerate(reader):
		#check for title row and skip iteration
		if counter == 0:
			title_row = row
			continue

		city_id = counter #just to make it more readable

		#Parsing first few columns for the first table
		# checks for a duplicate city/country combo and set the id to the first instance
		unique_hash = "|" + row[dup_columns[0]] + "|" + row[dup_columns[1]] 
		if unique_hash in duplicates and city_id != duplicates[unique_hash][0]:
			city_id = duplicates[unique_hash][0]
		else:
			cities_par = [city_id] #cities_parameters
			no_of_par = 5 #first 6 columns 
			for i in range(0,no_of_par):			
				cities_par.append(row[i] or "NULL")

			#NOT SQL injection safe and it looks nasty
			cites_par_temp = ["'{0}'".format(str(p).replace("'", "''")) for p in cities_par]
			cites_par_temp_2 = [p.replace("'NULL'","NULL") for p in cites_par_temp]
			cities_text_file.write( cities_sql.format(*cites_par_temp_2) + "\n")
		
		#Parsing the rest of the columns: Convert column title to year and get population
		certainty = row[5]  # certainty is located on the 6th column
		first_date_column = 6  #dates start on the 7th columm
		for i in range(first_date_column,len(row)):
			if row[i].replace(" ", ""):
				population = row[i]
				column_title = title_row[i].lower() 
				year = 0
				if column_title.startswith("bc"):
					year = int(column_title.replace("bc_", "-", 1))
				elif column_title.startswith("ad"):
					year = int(column_title.replace("ad_", "", 1))
				else:
					raise ValueError('CSV Column title did not start with AD or BC instead: ' + str(column_title))

				population_par = [city_id, year, population, certainty]
				#NOT SQL injection safe
				population_text_file.write(population_sql.format(*population_par) + "\n")

	cities_text_file.close()
	population_text_file.close()

if __name__ == "__main__":
    generate_inserts()

