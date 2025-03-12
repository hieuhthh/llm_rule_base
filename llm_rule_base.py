import json

from gemini_api import ask_gemini

def generate_json_rule_base(problem_input):
    problem_prompt_template = f"""\
Based on the original problem: "{problem_input}", please perform the following tasks:

1. **Logical Statements Generation**:
- Generate a series of diverse and logically related statements in the following format:
    - A. [First logical statement]
    - B. [Second logical statement]
    - C. [Third logical statement]
    - ...
- Ensure that at least one of the statements directly supports solving the original problem.

2. **Rule Representation**:
- Express the logical relationships between the statements using formal logic notation:
    - **Implication (→)**: A → B (If A is true, then B is true)
    - **Conjunction (∧)**: A ∧ B (Both A and B are true)
    - **Disjunction (∨)**: A ∨ B (At least one of A or B is true)
    - **Negation (¬)**: ¬A (A is false)
    - **Truth Assertion**: A (A is true)
- Provide only symbolic logical rules—no natural language explanations.
- Include rules that allow for deriving the logical statements.
- Do not provide too complex rules like "¬(A ∧ B)" or "B ∧ (A → ¬D) → ¬D" or "D ↔ (A → ¬F)".
- Generate rules that are not contradictory.
- It should take steps to derive the answer logical statement from the logical statements.

3. **Output Format**:
- Structure the output as a JSON dictionary:
```json
{{
    "logical_statements": [
        "A. [First logical statement]",
        "B. [Second logical statement]",
        "C. [Third logical statement]",
        ...
    ],
    "rule_representation": [
        "[Rule 1]",
        "[Rule 2]",
        ...
    ],
    "answer_logical_statement": "[One alphabetical choice from logical statements]"
}}
```
"""
    response = ask_gemini(problem_prompt_template)
    json_rule_base = response.split("```json\n")[1].split("```")[0]
    json_rule_base = json_rule_base.strip()
    json_rule_base = json.loads(json_rule_base)
    
    logical_statement_dict = {}
    for i, statement in enumerate(json_rule_base['logical_statements']):
        logical_statement_dict[chr(65 + i)] = statement
    json_rule_base['parsed_logical_statements'] = logical_statement_dict
    
    return json_rule_base

if __name__ == '__main__':
    problem_input = "Proof that Vietnam is in Southeast Asia."
    json_rule_base = generate_json_rule_base(problem_input)
    print(json_rule_base)
    # {'logical_statements': ['A. Southeast Asia is a region defined by geographical and political criteria.', 'B. Countries within Southeast Asia share common characteristics such as climate, culture, and history.', 'C. Vietnam is located on the Indochinese Peninsula.', 'D. The Indochinese Peninsula is geographically considered part of Southeast Asia.', 'E. Vietnam shares cultural and historical similarities with other Southeast Asian nations.', 'F. If a country is located on the Indochinese Peninsula, then it is located in Southeast Asia.', 'G. Vietnam is located in Southeast Asia.'], 'rule_representation': ['A', 'B', 'C', 'D', 'E', 'D → F', 'C ∧ F → G'], 'answer_logical_statement': 'G'}
