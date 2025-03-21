INFORMATION:
24C15033 - NGUYỄN MẬU TRỌNG HIẾU
24C15054 - PHÙ THỊ KIM TRANG

1. Create a conda environment:
conda create -n llm_rb python=3.10.0 -y
conda activate llm_rb

pip install -r requirements.txt

2. Prepare .env file:
- Create a .env file in the root folder
- Add the following content:
```
GEMINI_API_KEY="xxx"
```

To use the Gemini API, you need to create an account and get the API key from the Gemini website.

3. Run:
python main.py

In main.py, you just need to change:
- questions: list of questions
- out_route: Output route for the result

4. Other files:
- llm_rule_base.py: Contains the logic to interact with the rule-based system
- gemini_api.py: Contains the logic to interact with the Gemini API
- solve.py: Contains the main logic of the rule-based system