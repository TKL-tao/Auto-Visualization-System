import mii
import time

pipe = mii.pipeline('/hpc2hdd/home/tzou317/git_workspace/models/nl2vis_model_llama3_fp16')

print("Begin to inference----------------------------------")
start_time = time.time()
predicted_sql = "SELECT sum(height) , sex FROM people GROUP BY sex ORDER BY sum(height);"
question = "Give me the comparison about the sum of Height over the Sex , and group by attribute Sex by a pie chart, and rank x axis in ascending order."
prompt = f'''Given the SQL and visualization demands, your job is to determine the chart type of bar, pie, line, scatter, and you need to determine the x-axis name, y-axis name and grouping value name if it exists from SELECT clause.
Please format the answer in {{"chart":chart_type, "x_name": x_name, "y_name": y_name, "grouping": grouping_name}}
SQL: {predicted_sql}
Visualization demands: {question}'''
response = pipe([prompt], max_new_tokens=128)
end_time = time.time()

print(response)
print(end_time-start_time)