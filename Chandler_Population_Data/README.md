# Chandler Population Data clean up and parsing
Data-Set can be found here https://figshare.com/articles/Chandler_Population_Data/2059494
## Summary
Creates an SQL text based data dump to build a database
Two files of insert statements, one for each table
### Usage
Place the python script in the same folder as the data.
Run the script using "python generate_sql_inserts.py" in shell.
It generates two output text files.
Note: FILENAME is hardcoded to "chandlerV2.csv" since this was a one off.
### Create Database
Create two tables in your database.
I use these, be warned there were duplicate year|city combos, if you do not care you can remove the uq_CityPopulation constraint line.
Note: The python script handles duplicate cities fine but you loose the other names values from the duplicate cities.
```
CREATE TABLE  Cities(
	CityId INT NOT NULL,
	CityName VARCHAR(100) NOT NULL,
	OtherName VARCHAR(1000),
	Country VARCHAR(100),
	Latitude DECIMAL,
	Longitude DECIMAL,
	CONSTRAINT cities_pk PRIMARY KEY (CityId),
	CONSTRAINT city_u UNIQUE (CityName,Country)
);

CREATE TABLE CityPopulation (
	CityId INT NOT NULL,
	Year SMALLINT NOT NULL,
	Population INT NOT NULL,
	Certainty TINYINT,
	CONSTRAINT uq_CityPopulation UNIQUE (CityId, year),
	CONSTRAINT fk_cities  FOREIGN KEY (CityId)  REFERENCES Cities(CityId)
);
```
### Build and run the queries
I added:
	XACT_ABORT to terminate on error aka duplicates.
	NOCOUNT to stop those annoying row added messages.
	BEGIN / COMMIT to prevent partial data entry.
Note: I added drop tables later at the start so I could rebuild the tables later.
Final query looked something like this:
```
SET XACT_ABORT ON
SET NOCOUNT ON
BEGIN TRAN

CREATE TABLE Cities...
CREATE TABLE CityPopulation...
INSERT INTO  Cities...
INSERT INTO  CityPopulation...

COMMIT TRAN
SET XACT_ABORT OFF
SET NOCOUNT OFF
```
Now just run the cities query first then the population query.
Note: You will get duplicate errors if you used the CityPopulation table as is. I manually removed them.
## Extra info:
The script handles escaping apostrophes but not SQL injection.
It can be modified to interface directly to a database just make sure you consider SQL Injection.
## Licence
This project is licensed under the terms of the MIT license.