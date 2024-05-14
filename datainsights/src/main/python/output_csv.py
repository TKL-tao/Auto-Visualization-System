import sys
import pandas as pd
import json
from collections import Counter
import sqlite3

def main():
    if len(sys.argv) != 3:
        print("Usage: python simple_script.py <question> <dbPath>")
        sys.exit(1)

    sql = sys.argv[1]
    target_db = sys.argv[2]

    def sql2data(sql, target_db):
        conn = sqlite3.connect(target_db)
        cursor = conn.cursor()
        try:
            cursor.execute(sql)
            rows = cursor.fetchall()
            column_names = [description[0] for description in cursor.description]
            # print('SQL query succeeded.')
        except sqlite3.OperationalError:
            # print('SQL query failed.')
            return None, None, None

        column_types = []
        for item in rows[0]:
            if type(item).__name__ == 'int' or type(item).__name__ == 'float':
                column_types.append('numeric')
            else:
                column_types.append('categorical')
        # print(rows, column_names, column_types, sep='\n')
        return rows, column_names, column_types

    rows, column_names, column_types = sql2data(sql, target_db)
    outputcsv_filepath = "src/main/python/output_files/queried_results.csv"
    pd.DataFrame(rows, columns=column_names).to_csv(outputcsv_filepath, index=False)

if __name__ == "__main__":
    main()