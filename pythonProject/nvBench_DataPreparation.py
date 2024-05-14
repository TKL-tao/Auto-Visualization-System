import json
import pandas as pd
from sklearn.model_selection import train_test_split

validation_data = pd.read_csv('/hpc2hdd/home/tzou317/git_workspace/Auto-Visualization/pythonProject/data/nl2vis_validation.csv', header=0)
validation_data_list = validation_data['grounth_truth_outputs'].to_list()
print(validation_data_list)
with open('/hpc2hdd/home/tzou317/git_workspace/Auto-Visualization/pythonProject/data/nl2vis_validation_ground_truth_outputs.json', 'w') as f:
    json.dump(validation_data_list, f)

NVBench_json_path = "../nvBench/NVBench.json"
spider_train_merged_path = "../../spider/train_merged.json"

with open(NVBench_json_path) as json_file:
    NVBench_data = json.load(json_file)

with open(spider_train_merged_path) as json_file:
    spider_train_data = json.load(json_file)

print(spider_train_data[0])

print(type(NVBench_data))
print(type(NVBench_data["3"]), NVBench_data["3"], sep='\n')
print(NVBench_data["3"]["db_id"])

prompt_list = []
ground_truth_outputs_list = []
for key, value in NVBench_data.items():
    sql = value['vis_query']['data_part']['sql_part']
    nl_vis_list = value['nl_queries']

    chart = value['chart']
    vis_obj_chart = value['vis_obj']['chart']
    x_name = value['vis_obj']['x_name']
    y_name = value['vis_obj']['y_name']
    classify_name = value['vis_obj']['classify']
    if not classify_name:  # Only consider bar, pie, line, scatter, excluding these have grouping value.
        for nl_vis in nl_vis_list:
            prompt = f'''Given the SQL and visualization demands, your job is to determine the chart type of bar, pie, line, scatter, and you need to determine the x-axis name, y-axis name and grouping value name if it exists from SELECT clause.
Please format the answer in {{"chart":chart_type, "x_name": x_name, "y_name": y_name, "grouping": grouping_name}}
SQL: {sql}
Visualization demands: {nl_vis}'''
            grouth_truth_outputs = f'''{{"chart": {vis_obj_chart}, "x_name": {x_name}, "y_name": {y_name}, "grouping_name": None}}'''
            # print(prompt, grouth_truth_outputs, sep='\n')
            prompt_list.append(prompt)
            ground_truth_outputs_list.append(grouth_truth_outputs)

pd.DataFrame({'prompts': prompt_list, 'grounth_truth_outputs': ground_truth_outputs_list}).to_csv('data/nl2vis.csv', index=False)
print(prompt_list[10000])
    # if classify_name and chart == 'Grouping Line':
    #     print(value)
        # print(value['vis_obj']['describe'])
        # print(sql)
        # print(nl_vis)
        # print(chart_type, x_name, y_name, sep='\n')
        # print(classify_name)
        # break

mydataset = pd.read_csv('data/nl2vis.csv', header=0)
train_dataset, validation_dataset = train_test_split(mydataset, test_size=0.2, random_state=42)
train_dataset.to_csv('data/nl2vis_train.csv', index=False)
validation_dataset.to_csv('data/nl2vis_validation.csv', index=False)

validation_data = pd.read_csv('/hpc2hdd/home/tzou317/git_workspace/Auto-Visualization/pythonProject/data/nl2vis_validation.csv', header=0)
validation_data_list = validation_data['prompts'].to_list()
with open('/hpc2hdd/home/tzou317/git_workspace/Auto-Visualization/pythonProject/data/nl2vis_validation_input.json', 'w') as f:
    json.dump(validation_data_list, f)

validation_data = pd.read_csv('/hpc2hdd/home/tzou317/git_workspace/Auto-Visualization/pythonProject/data/nl2vis_validation.csv', header=0)
validation_data_list = validation_data['grounth_truth_outputs'].to_list()
with open('/hpc2hdd/home/tzou317/git_workspace/Auto-Visualization/pythonProject/data/nl2vis_validation_ground_truth_outputs.json', 'w') as f:
    json.dump(validation_data_list, f)








