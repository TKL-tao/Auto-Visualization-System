import sqlite3
import sys
import json
import re

def main():
    if len(sys.argv) != 4:
        print("Usage: python simple_script.py <sql> <db_path> <nl2vis_output_dic>")
        sys.exit(1)
    sql = sys.argv[1]
    target_db = sys.argv[2]

    nl2vis_output_dict = sys.argv[3]
    nl2vis_output_dict = nl2vis_output_dict.strip("{}")
    pairs = re.findall(r'(\w+)\s*=\s*([^,]+)', nl2vis_output_dict)
    result = {}
    for key, value in pairs:
        # if value == 'None':
        #     value = None
        result[key] = value
    nl2vis_output_dict = result

    # nl2vis_output_dict = {"chart": "bar", "x_name": "city", "y_name": "avg(lat)", "grouping_name": "None"}
    # sql = "SELECT Rank , count(*) FROM Faculty AS T1 JOIN Student AS T2 ON T1.FacID = T2.advisor GROUP BY T1.rank"
    # target_db = "../../spider/test_database/activity_1/activity_1.sqlite"
    # nl2vis_output_dict = {"chart": "scatter", "x_name": "SALARY", "y_name": "COMMISSION_PCT", "grouping_name": "None"}
    chart_info = nl2vis_output_dict.copy()
    chart_info["x_data"], chart_info["y_data"], chart_info["grouping_data"] = [], [], []

    conn = sqlite3.connect(target_db)
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        # print("SQL query succeeded.")
        # print(rows)
        # print(column_names)
    except sqlite3.OperationalError:
        # print("SQL query failed.")

        return

    column_names_lower = [column_name.lower() for column_name in column_names]

    if nl2vis_output_dict["x_name"].lower() in column_names_lower:
        column_index = column_names_lower.index(nl2vis_output_dict["x_name"].lower())
        chart_info["x_data"] = [item[column_index] for item in rows]
    if nl2vis_output_dict["y_name"].lower() in column_names_lower:
        column_index = column_names_lower.index(nl2vis_output_dict["y_name"].lower())
        chart_info["y_data"] = [item[column_index] for item in rows]
    if nl2vis_output_dict["grouping_name"].lower() in column_names_lower:
        column_index = column_names_lower.index(nl2vis_output_dict["grouping_name"].lower())
        chart_info["grouping_data"] = [item[column_index] for item in rows]

    print(json.dumps(chart_info))

if __name__ == "__main__":
    main()