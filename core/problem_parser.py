import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

def parse_nl_to_dfa_json(natural_language_text):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in the environment variables.")
        
    genai.configure(api_key=api_key)
    # Using Gemini 1.5 Flash for quick parsing
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
You are a formal language specification parser.
I will give you a natural language description of a Deterministic Finite Automaton (DFA) or a transition table.
You must extract the formal DFA specification and return ONLY a valid JSON object matching this schema perfectly:
{{
    "states": ["A", "B", "C"],
    "alphabet": ["0", "1"],
    "transitions": {{
        "A": {{"0": "B", "1": "C"}},
        "B": {{"0": "B", "1": "C"}},
        "C": {{"0": "B", "1": "C"}}
    }},
    "start_state": "A",
    "accepting_states": ["C"]
}}

Do not include markdown blocks like ```json. Return raw JSON text only.
If the input cannot be interpreted as a DFA, return an empty JSON object: {{}}

Input:
{natural_language_text}
"""
    
    response = model.generate_content(prompt)
    raw_text = response.text.strip()
    
    if raw_text.startswith('```json'):
        raw_text = raw_text.split('```json')[1]
    if raw_text.endswith('```'):
        raw_text = raw_text.rsplit('```', 1)[0]
    raw_text = raw_text.strip()
    
    try:
        data = json.loads(raw_text)
        if not data:
            raise ValueError("Could not determine a valid DFA from the input. Please provide more detail.")
        return data
    except json.JSONDecodeError:
        raise ValueError(f"AI failed to produce valid JSON. Output was: {raw_text}")
