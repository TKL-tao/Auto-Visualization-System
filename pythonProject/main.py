import requests

url = "http://127.0.0.1:5000/predict"
query = {"question": "List the average lat and long of different cities in table `station`",
        "target_db_path": "/hpc2hdd/home/tzou317/git_workspace/spider/test_database/bike_1/bike_1.sqlite"}

response = requests.post(url, json=query)

if response.status_code == 200:
    result = response.json()
    print("BOT1:", result["predicted_sql"])
    print("BOT2:", result["predicted_chart_pattern"])
else:
    print("Error:", response.status_code, response.text)

import sqlite3
conn = sqlite3.connect("D:/NL2SQL/Data/spider/test_database/chinook_1/chinook_1.sqlite")
cursor = conn.cursor()
cursor.execute('SELECT InvoiceDate ,  count(*) FROM CUSTOMER AS T1 JOIN INVOICE AS T2 ON T1.CustomerId  = T2.CustomerId WHERE T1.FirstName  =  "Astrid" AND T1.LastName  =  "Gruber" GROUP BY InvoiceDate;')
rows = cursor.fetchall()
column_names = [description[0] for description in cursor.description]
column_types = []
for item in rows[0]:
    if type(item).__name__ == 'int' or type(item).__name__ == 'float':
        column_types.append('numeric')
    else:
        column_types.append('categorical')


print(rows)
print(column_names)
print(column_types)