# from transformers import AutoModelForCausalLM, AutoTokenizer
# from peft import PeftModel
# import torch
# from torch.utils.data import Dataset, DataLoader
# import json
# import re

# # peft_layer_path = '/hpc2hdd/home/tzou317/git_workspace/peft_models/nl2vis_llama3'
# # model_path = "/hpc2hdd/home/tzou317/git_workspace/models/nl2vis_model_llama3"

# # model = AutoModelForCausalLM.from_pretrained(model_path, device_map='auto')
# # model = PeftModel.from_pretrained(model, peft_layer_path, torch_type=torch.bfloat16)
# # model = model.merge_and_unload()
# # print('model merge succeeded')
# # model.half()
# # model.save_pretrained("/hpc2hdd/home/tzou317/git_workspace/models/nl2vis_model_llama3_fp16")

# tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B")
# tokenizer.save_pretrained("/hpc2hdd/home/tzou317/git_workspace/models/nl2vis_model_llama3_fp16")

import torch
import time

# 指定使用GPU
device = torch.device("cuda")

# 创建一个张量并将其移动到GPU
x = torch.rand(1000, 1000).to(device)

# 循环以保持GPU占用率在30%左右
while True:
    time.sleep(5)
    x = torch.mm(x, x)