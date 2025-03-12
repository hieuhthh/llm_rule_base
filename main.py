import os
import shutil
import json

from llm_rule_base import generate_json_rule_base
from solve import solve_rule_base

out_route = 'generate_files'
# shutil.rmtree(out_route, ignore_errors=True)
os.makedirs(out_route, exist_ok=True)

questions = [
    'Proof that Vietnam is in Southeast Asia.',
    'Is Hồ Chí Minh city the capital of Vietnam?',
    'Is the Earth flat?',
    'Can humans breathe underwater?',
    'Check if the following statement is true: "Number 16 is an odd number."',
    'Is 15 a prime number?',
]

skip_list = [0]

for i, question in enumerate(questions):
    if i in skip_list:
        continue
    
    print(f"Generating for question {i+1}: {question}")
    
    json_rule_base = generate_json_rule_base(question)
    solve_result = solve_rule_base(json_rule_base)
    
    output_dict = {}
    output_dict['question'] = question
    output_dict['llm_generate'] = json_rule_base
    output_dict['solve_steps'] = solve_result['steps']
    output_dict['result'] = solve_result['result']
    
    answer_statement = json_rule_base["parsed_logical_statements"][json_rule_base["answer_logical_statement"]]
    answer_statement = answer_statement.split('. ')[1]

    if solve_result['is_answer_true']:
        final_conclusion = f"The statement '{answer_statement}' is True."
    else:
        final_conclusion = f"The statement '{answer_statement}' is False."
        
    output_dict['final_conclusion'] = final_conclusion
    
    # Clean up the output
    del output_dict['llm_generate']['parsed_logical_statements']
    
    with open(f'{out_route}/output_{i}.json', 'w') as f:
        f.write(json.dumps(output_dict, indent=4, ensure_ascii=False))
        
    print('-'*20)
