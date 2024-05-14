from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch
from torch.utils.data import Dataset, DataLoader
import json
import re
# from transformers import StoppingCriteriaList

# from transformers import StoppingCriteria
# class EosListStoppingCriteria(StoppingCriteria):
#     def __init__(self, eos_sequence = [128256]):
#         self.eos_sequence = eos_sequence

#     def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
#         last_ids = input_ids[:,-len(self.eos_sequence):].tolist()
#         return self.eos_sequence in last_ids
# stopping_criteria = StoppingCriteriaList([EOSTokenStoppingCriteria()])

model_name = "meta-llama/Meta-Llama-3-8B" 
model_path = "/hpc2hdd/home/tzou317/git_workspace/models/nl2vis_model_llama3"  # 原始模型所存放的文件夹， 例如 ‘nl2sql/hf_models/deepseek’
# peft_layer_path = '../../../peft_models/nl2vis_llama3'  # 在finetuning中， PEFT层的输出路径，例如'nl2sql/peft_models/nl2table/peft_model1'

tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.bos_token
tokenizer.pad_token_id = tokenizer.bos_token_id
tokenizer.padding_side = 'left'
# print(tokenizer.eos_token_id)
# tokenizer.add_tokens(['<|im_end|>'])
# # tokenizer.encode('<|im_end|>')
# print('<|im_end|>' in tokenizer.get_vocab())
# print('<|im_end|> id is ', tokenizer.convert_tokens_to_ids('<|im_end|>'))

model = AutoModelForCausalLM.from_pretrained(model_path, device_map='auto')
# model = PeftModel.from_pretrained(model, peft_layer_path, torch_type=torch.bfloat16)
# model = model.merge_and_unload()
# print('model merge succeeded')
# model.save_pretrained("/hpc2hdd/home/tzou317/git_workspace/models/nl2vis_model_llama3")

model.eval()


nl_vis = "I want to see trend the number of season over season by Home_team, show x-axis in ascending order."
sql = "SELECT Season , COUNT(Season) FROM game GROUP BY Home_team ,  Season ORDER BY Season ASC"

prompt = f'''Given the SQL and visualization demands, your job is to determine the chart type of bar, pie, line, scatter, and you need to determine the x-axis name, y-axis name and grouping value name if it exists from SELECT clause.
Please format the answer in {{"chart":chart_type, "x_name": x_name, "y_name": y_name, "grouping": grouping_name}}
SQL: {sql}
Visualization demands: {nl_vis}'''
message = [
    {'role': 'user', 'content': prompt.strip()}
]
inputs = tokenizer.apply_chat_template(message, tokenize=True, return_tensors='pt', add_generation_prompt=True).to(model.device)
responses = model.generate(
    inputs,
    max_new_tokens=100, 
    do_sample=False, 
    pad_token_id=tokenizer.eos_token_id,
    eos_token_id=tokenizer.eos_token_id,
    # stopping_criteria=stopping_criteria
    # stopping_criteria = [EosListStoppingCriteria()]
)
output = tokenizer.decode(responses[0], skip_special_tokens=True).strip()
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
cleaned_output = clean_outputs([output])
print(cleaned_output[0])