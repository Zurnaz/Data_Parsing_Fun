# Foreign Office consular data clean up and parsing
Data-Set can be found here https://www.gov.uk/government/collections/consular-data
### Summary
Aggregates the data from multiple columns into more generic columns and replaces the <=5 with a number and a flag to allow easier queries on the data.

NOTE: Data structure from Feb 2016 and onwards changed. It still works fine but the columns were changed and makes querying mixed datasets difficult. For me Feb 2016 - Feb 2017 was fine for data analysis. I recommend separating pre Feb 2016 data for older data analysis. 

## usage

#### Prerequisites
```
Python 3
```
#### Instructions
Create folders for each year and place the CSVs inside them. Like so:

```
Foreign_Office_Consular_Data
├─┬ 2016
│ └─┬─ Consular_cases_April_2016.csv
│ 	└─ OTHERFILES.csv etc
└─┬ 2017
  └─┬─ Transparency_Data_Jan_17.csv
  	└─ OTHERFILES.csv etc
```
The year as the folder is important as the file naming for the CSVs is inconsistent and the date inside them only includes month and day.

Update the folder list in the python script on line 5 for your folders:
```
FOLDER_LIST = ["2016","2017"]
```

NOTE: For march 2016 there is an extra row at the top of the CSV that needs to be deleted pre script

Run the script from the folder:
```
py -3 consular_data_parser.py
```

You may see a few (in various forms):
```
Adding to CityCases value ignored: '#N/A' for (Wuhan : Fee bearing services) IN Transparency_data_Sep_16.csv
```
The script ignores values that are not integars or <=5. It carries on fine and does not cause issues. Just take a glance at the data to make sure no valid data is ignored. If there is then it is time to submit a pull request. Otherwise SQLite file is generated. Job complete.

## Extra info:

Note: I use DBeaver to run queries and export the data 


### Table structure

NOTE: I used the upto flag as true instead of the <=5 and having the amount as 5 for easier querying

##### Case Types

id |casetype                            |subtype                             |
---|------------------------------------|------------------------------------|
1  |Arrest/Detention                    | Assault                            |
2  |Arrest/Detention                    | Assault with Weapon                |

##### City

id  |name                |
----|--------------------|
1   |CITYNAME1           |
2   |CITYNAME2           |

##### CityCases

cityid |casetypeid |created             |amount |upto |
-------|-----------|--------------------|-------|-----|
2      |5          |2016-04-16 00:00:00 |5      |1    |
2      |7          |2016-04-16 00:00:00 |6      |0    |

NOTE: Created is date the document was created. upto is flagged when <=5 was entered and the number 5 is the amount entered. The flag indicates the number is between 1 and the amount (in this case 5).

### Querying the data

###### Quick and interesting query i made:

Due to the way they present the data in some cases as <=5 (It could be one instance or up to 5). I assume for anonymization reasons. It can be confusing to see approximate real data. This query gives you an estimate range of the cases the consulates had to deal with to prevent misunderstanding. 

```
SELECT "Between:"
		, SUM(cs.amount) - ((SUM(cs.upto) * 5) - SUM(cs.upto)) AS lower
		, "to" 
		, SUM(cs.amount) AS upper
		, c.name
		, ct.casetype
		, ct.subtype
FROM CityCases cs
JOIN City c ON c.id = cs.cityid
JOIN CaseTypes ct ON  ct.id = cs.casetypeid
WHERE ct.casetype LIKE '%Accident%'
GROUP BY c.name
ORDER BY upper DESC
```

##### Result:

"Between:" |lower |"to" |upper |name             |casetype            |subtype                |
-----------|------|-----|------|-----------------|--------------------|-----------------------|
Between:   |6     |to   |30    |Bangkok          |Accident/Emergency  | Road Traffic Accident |
Between:   |3     |to   |15    |Paris            |Accident/Emergency  | Road Traffic Accident |


NOTE: "Between" and "to" are just there for clarity feel free to remove them from the query.

## Licence
This project is licensed under the terms of the MIT license.