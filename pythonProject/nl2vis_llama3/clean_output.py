import re
import json

with open('../data/nl2vis_validation_output.json', 'r') as f:
    outputs = json.load(f)

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
    
cleaned_outputs = clean_outputs(outputs)
print('The length of cleaned outputs is {}'.format(len(outputs)))


def get_precision(cleaned_outputs, ground_truth_outputs):
    print('Length of cleaned outputs: {}'.format(len(cleaned_outputs)))
    correct_count = 0
    for i, cleaned_output in enumerate(cleaned_outputs):
        if cleaned_output == ground_truth_outputs[i]:
            correct_count += 1
        else:
            print('Unmatched sample when i = {}'.format(i))
            print(cleaned_output, ground_truth_outputs[i], sep='\n')
    return correct_count / len(cleaned_outputs)

with open('/hpc2hdd/home/tzou317/git_workspace/Auto-Visualization/pythonProject/data/nl2vis_validation_ground_truth_outputs.json', 'r') as f:
    ground_truth_outputs = json.load(f)
ground_truth_outputs = clean_outputs(ground_truth_outputs, False)

get_precision(cleaned_outputs, ground_truth_outputs)