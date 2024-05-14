from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import StoppingCriteria
import sqlite3
import re
import mii
from flask import Flask, request, jsonify

app = Flask(__name__)

class EosListStoppingCriteria(StoppingCriteria):
    def __init__(self, eos_sequence = [6203]):
        self.eos_sequence = eos_sequence

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        last_ids = input_ids[:,-len(self.eos_sequence):].tolist()
        return self.eos_sequence in last_ids

model1_name = 'deepseek-ai/deepseek-coder-6.7b-instruct'
model1_path = '/hpc2hdd/home/tzou317/nl2sql/model_inference/model1'
model2_name = 'deepseek-ai/deepseek-coder-6.7b-instruct'
model2_path = '/hpc2hdd/home/tzou317/nl2sql/model_inference/model2'
nl2vis_model_name = 'meta-llama/Meta-Llama-3-8B'
nl2vis_model_path = '/hpc2hdd/home/tzou317/git_workspace/models/nl2vis_model_llama3'


################################################  Stage1
def get_prompt1(question, target_db_path):

    conn = sqlite3.connect(target_db_path)
    cur = conn.cursor()
    try:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table_name[0] for table_name in cur.fetchall()]
    except Exception as e:
        print('Can not execute tables-finding-sql in the given target_db_path')
        return e
    
    database_schema = ""
    for table in tables:
        print(table)
        database_schema += f"CREATE TABLE `{table}` (\n"

        cur.execute(f"PRAGMA table_info(`{table}`);")
        cur_fetchall = cur.fetchall()
        for column in cur_fetchall:
            database_schema += column[1] + ',\n'
        database_schema = database_schema[:-2] + ');\n\n'

    prompt1 = f'''Given the following SQL tables, your job is to determine the tables that the question is referring to. Please format the answer in {{"tables": [entities]}}
{database_schema}### 
Question: 
{question}'''
    return prompt1

# Model1 preparation
tokenizer = AutoTokenizer.from_pretrained(model1_name)
tokenizer.pad_token = tokenizer.bos_token
tokenizer.pad_token_id = tokenizer.bos_token_id
tokenizer.padding_side = 'left'
tokenizer.encode(' ;')

model1 = AutoModelForCausalLM.from_pretrained(model1_path, device_map='auto')  # important
model1.eval()
################################################  Stage2

def get_prompt2(question, target_db_path, table_list):
    conn = sqlite3.connect(target_db_path)
    cur = conn.cursor()
    database_schema = ''
    for table in table_list:
        try:
            cur.execute(f"PRAGMA table_info({table});")
        except Exception as e:
            print(table, 'is not found in target_db')
            continue
        database_schema += f"CREATE TABLE `{table}` (\n"
        cur_fetchall = cur.fetchall()
        for column in cur_fetchall:
            database_schema += column[1] + ' ' + column[2] + ',\n'
        database_schema = database_schema[:-2] + ');\n\n' + f"Sample rows from the `{table}`:\n"
        cur.execute(f"SELECT * FROM `{table}` LIMIT 3;")
        database_schema += '\n'.join([', '.join(str(ele) for ele in element) for element in cur.fetchall()])
    prompt2 = f'''Given the following SQL tables, your job is to generate only one Sqlite SQL query given the user's question.
Put your answer inside the ```sql and ``` tags.
{database_schema}
### 
Question: 
{question}'''
    return prompt2

# Model2 preparation
tokenizer = AutoTokenizer.from_pretrained(model2_name)
tokenizer.pad_token = tokenizer.bos_token
tokenizer.pad_token_id = tokenizer.bos_token_id
tokenizer.padding_side = 'left'
tokenizer.encode(' ;')

model2 = AutoModelForCausalLM.from_pretrained(model2_path, device_map='auto')  # important
model2.eval()


################################################ nl2vis
def get_prompt3(question, predicted_sql):
    prompt = f'''Given the SQL and visualization demands, your job is to determine the chart type of bar, pie, line, scatter, and you need to determine the x-axis name, y-axis name and grouping value name if it exists from SELECT clause.
Please format the answer in {{"chart":chart_type, "x_name": x_name, "y_name": y_name, "grouping": grouping_name}}
SQL: {predicted_sql}
Visualization demands: {question}'''
    return prompt

# NL2VIS model preparation
tokenizer3 = AutoTokenizer.from_pretrained(nl2vis_model_name)
tokenizer3.pad_token = tokenizer.bos_token
tokenizer3.pad_token_id = tokenizer.bos_token_id
tokenizer3.padding_side = 'left'

# model3 = AutoModelForCausalLM.from_pretrained(nl2vis_model_path, device_map='auto')
# model3.eval()

pipe = mii.pipeline('/hpc2hdd/home/tzou317/git_workspace/models/nl2vis_model_llama3_fp16')

########################################################## inference
# question = "List the average lat and long of different cities in table `station`"
# target_db_path = 'nl2sql/data/bike_1.sqlite'

@app.route('/predict', methods=['POST'])
def predict():
    inputdata_json = request.json
    # input1, input2 = data['input1'], data['input2']
    question, target_db_path = inputdata_json['question'], 'temp/' + inputdata_json['target_db_path']

    # input and output
    prompt1 = get_prompt1(question, target_db_path)
    print(prompt1)

    message = [{'role': 'user', 'content': prompt1.strip()}]
    input1 = tokenizer.apply_chat_template(message, tokenize=True, return_tensors='pt', add_generation_prompt=True).to(model1.device)
    print("Model1 is inferencing...")
    responses = model1.generate(
        input1,
        max_new_tokens=50, 
        do_sample=False, 
        pad_token_id=tokenizer.eos_token_id,
        eos_token_id=tokenizer.eos_token_id,
        stopping_criteria = [EosListStoppingCriteria()]
        )
    output1 = tokenizer.decode(responses[0], skip_special_tokens=True).strip()

    match = re.findall(r'\[[^\]]*\]', output1)
    if match[-1] != '{"tables": [entities]}':
        print('Output1: ', match[-1])
        output1 = eval(match[-1])
        # eval(match[-1]): [table1, table2, ...]
    else:
        print('Output1 goes wrong.')
        print('Output1: ', output1, sep='\n')

    # input and output
    prompt2 = get_prompt2(question, target_db_path, output1)
    print(prompt2)
    message = [{'role': 'user', 'content': prompt2.strip()}]
    input1 = tokenizer.apply_chat_template(message, tokenize=True, return_tensors='pt', add_generation_prompt=True).to(model2.device)
    print("Model2 is inferencing...")
    responses = model2.generate(
        input1,
        max_new_tokens=250, 
        do_sample=False, 
        pad_token_id=tokenizer.eos_token_id,
        eos_token_id=tokenizer.eos_token_id,
        stopping_criteria = [EosListStoppingCriteria()]
        )
    output2 = tokenizer.decode(responses[0], skip_special_tokens=True).strip()

    match = re.findall(r"```sql(.*?)```", output2, re.DOTALL)
    if match is None or match == [' and ']:
        print('output2 went wrong.')
        print('output2: ', output2)
    else:
        output2 = match[1].strip()
        print('output2: ', output2)
    

    # # input and output 3
    prompt3 = get_prompt3(question, output2)
    print(prompt3)
    
    # message = [{'role': 'user', 'content': prompt3.strip()}]
    # inputs = tokenizer3.apply_chat_template(message, tokenize=True, return_tensors='pt', add_generation_prompt=True).to(model3.device)
    # print("Model3 is inferencing...")
    # responses = model3.generate(
    #     inputs,
    #     max_new_tokens=80, 
    #     do_sample=False, 
    #     pad_token_id=tokenizer3.eos_token_id,
    #     eos_token_id=tokenizer3.eos_token_id,
    #     # stopping_criteria=stopping_criteria
    #     # stopping_criteria = [EosListStoppingCriteria()]
    # )
    # output = tokenizer3.decode(responses[0], skip_special_tokens=True).strip()
    # print(output)
    output = pipe([prompt3], max_new_tokens=100)
    output = str(output[0])
    print(output)

    def clean_outputs(outputs, if_truncate=True):
        outputs_list = []
        pattern = r'{"chart":\s*([^,]+)\s*,\s*"x_name":\s*([^,]+)\s*,\s*"y_name":\s*([^,]+)\s*,\s*"grouping_name":\s*([^,]+)\s*}'
        for i, output in enumerate(outputs):
            if if_truncate:
                text = output[350:]
            else:
                text = output
            match = re.findall(pattern, text)
            if match:
                match = match[0]
                chart_type = match[0]
                x_name = match[1]
                y_name = match[2]
                grouping_name = match[3]
                outputs_list.append({'chart': chart_type, 'x_name': x_name, 'y_name': y_name, 'grouping_name': grouping_name})
            else:
                print("The nl2vis model doesn't output in standard form: {}----------------------".format(i))
                print(text)
                outputs_list.append({})
        return outputs_list
    cleaned_output = clean_outputs([output], if_truncate=False)
    cleaned_output = cleaned_output[0]


    return jsonify({'predicted_sql': output2, 'predicted_chart_pattern': cleaned_output})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)