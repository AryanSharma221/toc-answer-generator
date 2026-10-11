import os
import json
import logging
import google.generativeai as genai
from dotenv import load_dotenv

from solvers.dfa_minimizer import DFAMinimizer
from solvers.dfa_verification import moore_minimize, table_filling_minimize

load_dotenv()
logger = logging.getLogger(__name__)


class KeyManager:
    _keys = []
    _current_index = 0
    _loaded = False

    @classmethod
    def load_keys(cls):
        if cls._loaded:
            return
        cls._loaded = True
        
        # Check GEMINI_API_KEYS (comma separated)
        keys_str = os.environ.get("GEMINI_API_KEYS", "")
        if keys_str:
            cls._keys = [k.strip() for k in keys_str.split(",") if k.strip()]
        
        # Check individual keys GEMINI_API_KEY_1, GEMINI_API_KEY_2, etc.
        if not cls._keys:
            i = 1
            while True:
                k = os.environ.get(f"GEMINI_API_KEY_{i}")
                if k:
                    cls._keys.append(k.strip())
                    i += 1
                else:
                    break
                    
        # Check standard GEMINI_API_KEY as fallback
        if not cls._keys:
            k = os.environ.get("GEMINI_API_KEY")
            if k:
                cls._keys.append(k.strip())
                
    @classmethod
    def get_current_key(cls):
        cls.load_keys()
        if not cls._keys:
            return None
        return cls._keys[cls._current_index]

    @classmethod
    def rotate_key(cls):
        cls.load_keys()
        if len(cls._keys) <= 1:
            return False
        cls._current_index = (cls._current_index + 1) % len(cls._keys)
        logger.info(f"Rotated to API key index {cls._current_index}")
        return True

class AIIntegrationPolicy:
    @staticmethod
    def get_api_key():
        # Policy: Keep API keys on backend and manage rotation
        return KeyManager.get_current_key()
        
    @staticmethod
    def query_gemini_minimization(problem_data):
        """
        Query Gemini for a minimized DFA proposition and explanation.
        Policy: Gemini may explain or suggest, but MUST NOT supply the authoritative partition.
        """
        api_key = AIIntegrationPolicy.get_api_key()
        if not api_key:
            return {"error": "API unavailable", "explanation": "Deterministic fallback used."}
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-3.5-flash-lite', generation_config={"response_mime_type": "application/json"})
        prompt = f"""
Minimize this DFA and return the result as JSON.
States: {problem_data['states']}
Alphabet: {problem_data['alphabet']}
Transitions: {problem_data['transitions']}
Start State: {problem_data['start_state']}
Accepting States: {problem_data['accepting_states']}

Return ONLY valid JSON mapping strictly to the DFA JSON schema. No markdown blocks.
"""
        max_attempts = len(KeyManager._keys) if KeyManager._keys else 3
        last_error = None
        
        for attempt in range(max_attempts):
            api_key = KeyManager.get_current_key()
            if not api_key:
                return {"error": "API Key unavailable", "explanation": "Deterministic fallback used."}
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-3.5-flash-lite', generation_config={"response_mime_type": "application/json"})
            try:
                response = model.generate_content(prompt)
                raw_text = response.text.strip()
                
                if raw_text.startswith('```json'):
                    raw_text = raw_text.split('```json')[1]
                if raw_text.endswith('```'):
                    raw_text = raw_text.rsplit('```', 1)[0]
                raw_text = raw_text.strip()
                
                try:
                    return {"proposed_dfa": json.loads(raw_text)}
                except json.JSONDecodeError:
                    import re
                    cleaned_text = re.sub(r',\s*([}\]])', r'\1', raw_text)
                    return {"proposed_dfa": json.loads(cleaned_text)}
            except Exception as e:
                last_error = str(e)
                err_str = last_error.lower()
                if "429" in err_str or "quota" in err_str or "exhausted" in err_str:
                    if KeyManager.rotate_key():
                        logger.warning(f"API limit hit in minimization. Rotated key. (Attempt {attempt+1}/{max_attempts})")
                        continue
                return {"error": last_error, "explanation": "API timeout, rate limit, or malformed JSON."}
        
        return {"error": last_error, "explanation": "Failed after trying all available API keys."}

    @staticmethod
    def solve_universal_with_ai(category, problem_data):
        import json
        api_key = AIIntegrationPolicy.get_api_key()
        if not api_key:
            raise RuntimeError("API Key unavailable.")
            
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-3.5-flash-lite', generation_config={"response_mime_type": "application/json"})
        prompt = f'''
You are an expert Theory of Computation solver. 
Task Category: {category}
Problem Inputs:
{json.dumps(problem_data, indent=2)}

If the Problem Inputs contain a "canonical_result" field, YOU MUST NOT perform your own computation. The result has already been mathematically verified. Your job is ONLY to explain the interpretation, assumptions, and the step-by-step logic matching the canonical_result provided. Do not contradict the canonical_result.

You must output your answer as a raw JSON object with exactly these fields:
{{
  "markdown_content": "The complete Markdown representing the solution.",
  "diagram_type": "dfa or parse_tree or none",
  "diagram_json": {{ ... the valid JSON mapping to the DFA or Parse Tree diagram schema if applicable ... }}
}}

The "markdown_content" field MUST include the following 6 sections in order, using Markdown headers:
### Interpreted Problem
### Assumptions & Missing Information
### Step-by-Step Solution
### Tables, Traces, or State Partitions
### Final Answer
### Structured Description of Diagram

Use strictly Markdown formatting. Do not use raw HTML tags. Do not fabricate an answer if you cannot solve it.
If the category is "Minimization", "String Acceptance Traces", "NFA to DFA Conversion", "Regex to DFA Conversion", or "DFA/NFA Analysis", diagram_type should be "dfa", and diagram_json should contain strictly: {{"states": ["s1"], "alphabet": ["0"], "transitions": {{"s1": {{"0": "s1"}}}}, "start_state": "s1", "accepting_states": ["s1"]}}.
If the category is "CFG Derivation", diagram_type should be "parse_tree", and diagram_json should contain the nested dictionary of the tree, e.g., {{"name": "S", "children": [{{"name": "a"}}]}}.
'''
        max_attempts = len(KeyManager._keys) if KeyManager._keys else 3
        last_error = None
        
        for attempt in range(max_attempts):
            api_key = KeyManager.get_current_key()
            if not api_key:
                raise RuntimeError("API Key unavailable.")
            genai.configure(api_key=api_key)
            # Make sure we declare model here so it gets the new key config
            model = genai.GenerativeModel('gemini-3.5-flash-lite', generation_config={"response_mime_type": "application/json"})
            try:
                response = model.generate_content(prompt)
                raw_text = response.text.strip()
                

                # Fallback cleanups in case model hallucinates markdown inside JSON mode
                if raw_text.startswith('```json'):
                    raw_text = raw_text.split('```json', 1)[1]
                if raw_text.endswith('```'):
                    raw_text = raw_text.rsplit('```', 1)[0]
                raw_text = raw_text.strip()
                
                try:
                    return json.loads(raw_text)
                except json.JSONDecodeError as jde:
                    # sometimes the lite model leaves a trailing comma
                    import re
                    cleaned_text = re.sub(r',\s*([}\]])', r'\1', raw_text)
                    return json.loads(cleaned_text)

            except Exception as e:
                last_error = str(e)
                err_str = last_error.lower()
                # If rate limit or quota exceeded, try to rotate key
                if "429" in err_str or "quota" in err_str or "exhausted" in err_str:
                    rotated = KeyManager.rotate_key()
                    if rotated:
                        logger.warning(f"API rate limit hit. Rotated key and retrying... (Attempt {attempt+1}/{max_attempts})")
                        continue
                    else:
                        raise RuntimeError(f"API quota exceeded and no other keys available. Error: {last_error}")
                else:
                    # Not a rate limit error, break out and let upstream retry loop handle it
                    raise RuntimeError(f"API call failed: {last_error}")
                    
        raise RuntimeError(f"API call failed after cycling keys. Last error: {last_error}")

    @staticmethod
    def solve_and_verify(problem_data):
        # 1. Authoritative Deterministic Execution
        minimizer = DFAMinimizer(
            problem_data['states'], problem_data['alphabet'],
            problem_data['transitions'], problem_data['start_state'],
            problem_data['accepting_states']
        )
        
        validation_error = minimizer.validate()
        if validation_error:
            raise ValueError(f"Computation Error: {validation_error}")
            
        deterministic_result = minimizer.minimize()
        
        # 2. Independent Verification Check
        moore_res = moore_minimize(
            problem_data['states'], problem_data['alphabet'],
            problem_data['transitions'], problem_data['start_state'],
            problem_data['accepting_states']
        )
        
        hopcroft_classes = []
        for s in deterministic_result['states']:
            if s.startswith('{') and s.endswith('}'):
                hopcroft_classes.append(frozenset(s[1:-1].split(',')))
            else:
                hopcroft_classes.append(frozenset([s]))
                
        moore_classes = [frozenset(b) for b in moore_res]
        
        if set(hopcroft_classes) != set(moore_classes):
            raise RuntimeError("Deterministic verification failed: Hopcroft and Moore disagree. Refusing to output unverified DFA.")
            
        # 3. Gemini Advisory Call (Non-blocking, non-authoritative)
        gemini_response = AIIntegrationPolicy.query_gemini_minimization(problem_data)
        
        if "error" not in gemini_response:
            proposed = gemini_response.get("proposed_dfa", {})
            proposed_states = proposed.get("states", [])
            
            if len(proposed_states) != len(deterministic_result["states"]):
                logger.warning("DISCREPANCY: Gemini proposed %d states, but deterministic algorithm verified %d states. Ignoring Gemini proposal.", len(proposed_states), len(deterministic_result["states"]))
                gemini_response["discrepancy"] = True
                
        # 4. Strict Enforcement: Always return the verified deterministic result
        return deterministic_result, gemini_response
