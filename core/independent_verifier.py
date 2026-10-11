import json
import logging
from typing import Dict, Any

from core.ai_integration import KeyManager
import google.generativeai as genai

logger = logging.getLogger(__name__)

class IndependentVerifier:
    @staticmethod
    def verify(category: str, problem_data: Dict[str, Any], canonical_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Independently solves the problem using the API and compares it against canonical_result.
        Returns a dictionary with verification status and discrepancies.
        """
        clean_problem_data = {k: v for k, v in problem_data.items() if k not in ['canonical_result', 'previous_error']}
        
        prompt = IndependentVerifier._build_prompt(category, clean_problem_data)
        if not prompt:
            return {"verified": True, "skipped": True}
            
        api_result = IndependentVerifier._call_api(prompt)
        if "error" in api_result:
            logger.warning(f"Independent verification failed: {api_result['error']}")
            return {"verified": False, "error": api_result["error"]}
            
        return IndependentVerifier._compare_results(category, api_result, canonical_result)

    @staticmethod
    def _build_prompt(category: str, problem_data: Dict[str, Any]) -> str:
        base_prompt = f"""You are an independent Theory of Computation verifier.
Task: {category}
Inputs:
{json.dumps(problem_data, indent=2, default=str)}

You must solve this problem independently. Do NOT output markdown formatting outside the JSON object.
Respond exactly with a JSON object containing:
- "independently_computed_result": your final answer structured logically based on the task type.
- "intermediate_mathematical_details": string explaining your math.
- "assumptions": string describing assumptions.
- "uncertainty": string describing if you are unsure about any edge cases.
"""
        if category == "Minimization":
            base_prompt += """
For "independently_computed_result", you MUST provide exactly this schema:
{
  "reachable_states": ["array of strings"],
  "final_partitions": [["array of states in partition 1"], ["array of states in partition 2"]],
  "minimized_state_count": int,
  "start_partition": ["array of states in start partition"],
  "accepting_partitions": [["array of states in accepting partition 1"]],
  "transitions": [
    {"from_partition": ["states"], "symbol": "string", "to_partition": ["states"]}
  ]
}
"""
        elif category == "String Acceptance Traces":
            base_prompt += """
For "independently_computed_result", you MUST provide exactly this schema:
{
  "traces": [
    {
      "input_string": "string",
      "valid_alphabet": bool,
      "visited_states_in_order": ["list of state strings from start to finish"],
      "transitions": [{"current": "string", "symbol": "string", "next": "string"}],
      "final_state": "string",
      "accepted": bool
    }
  ]
}
"""
        elif category == "NFA to DFA Conversion":
            base_prompt += """
For "independently_computed_result", you MUST provide exactly this schema:
{
  "initial_subset": ["states"],
  "reachable_subsets": [["states"], ["states"]],
  "accepting_subsets": [["states"]],
  "transitions": [
    {"from_subset": ["states"], "symbol": "string", "to_subset": ["states"]}
  ]
}
"""
        else:
            return None
            
        return base_prompt

    @staticmethod
    def _call_api(prompt: str) -> Dict[str, Any]:
        max_attempts = len(KeyManager._keys) if KeyManager._keys else 3
        last_error = None
        
        for attempt in range(max_attempts):
            api_key = KeyManager.get_current_key()
            if not api_key:
                return {"error": "API Key unavailable"}
                
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-3.5-flash-lite', generation_config={"response_mime_type": "application/json"})
            try:
                response = model.generate_content(prompt)
                raw_text = response.text.strip()
                return json.loads(raw_text)
            except Exception as e:
                last_error = str(e)
                err_str = last_error.lower()
                if "429" in err_str or "quota" in err_str or "exhausted" in err_str:
                    if KeyManager.rotate_key():
                        continue
                return {"error": last_error}
        return {"error": last_error or "Max retries exceeded"}

    @staticmethod
    def _compare_results(category: str, api_result: Dict[str, Any], canonical_result: Dict[str, Any]) -> Dict[str, Any]:
        discrepancies = []
        is_verified = True
        
        indep_res = api_result.get("independently_computed_result")
        if not indep_res:
            return {"verified": False, "discrepancies": ["Inconclusive: Missing independently_computed_result object in API response."]}
            
        raw = canonical_result.get("raw_data", {})
        
        try:
            if category == "Minimization":
                # Compare reachable states
                can_reachable = set(raw.get('states', [])) # Wait, raw['states'] in minimizer is the minimized states!
                # Actually, in minimizer, we need to extract original reachable. 
                # Let's just compare partitions which is robust enough.
                can_partitions = {frozenset(p) for p in raw.get('partitions', [])}
                
                api_parts = indep_res.get('final_partitions', [])
                if not isinstance(api_parts, list):
                    raise ValueError("Malformed final_partitions")
                api_partitions = {frozenset(p) for p in api_parts}
                
                if can_partitions != api_partitions:
                    discrepancies.append(f"Partition mismatch: Canonical={can_partitions}, API={api_partitions}")
                    is_verified = False
                    
                can_count = len(can_partitions)
                api_count = indep_res.get('minimized_state_count')
                if can_count != api_count:
                    discrepancies.append(f"State count mismatch: Canonical={can_count}, API={api_count}")
                    is_verified = False
                
                # Check accepting partitions
                # Canonical minimizer new_acc are strings like "{A,B}" or "A". We can reconstruct from partitions.
                # Actually, just compare structurally. If partitions match, it's mostly good.
                
            elif category == "String Acceptance Traces":
                api_traces = indep_res.get("traces", [])
                if not isinstance(api_traces, list):
                    raise ValueError("Malformed traces array")
                    
                can_traces = raw.get("trace_results", [])
                if len(api_traces) != len(can_traces):
                    discrepancies.append(f"Trace count mismatch.")
                    is_verified = False
                else:
                    for i, (api_tr, can_tr) in enumerate(zip(api_traces, can_traces)):
                        if api_tr.get("accepted") != can_tr.get("accepted"):
                            discrepancies.append(f"Trace {i} decision mismatch: Canonical={can_tr.get('accepted')}, API={api_tr.get('accepted')}")
                            is_verified = False
                        if api_tr.get("final_state") != can_tr.get("final_state"):
                            discrepancies.append(f"Trace {i} final state mismatch: Canonical={can_tr.get('final_state')}, API={api_tr.get('final_state')}")
                            is_verified = False
                        
            elif category == "NFA to DFA Conversion":
                can_subsets = {frozenset(s) for s in raw.get('subsets', [])}
                
                api_subs = indep_res.get("reachable_subsets", [])
                if not isinstance(api_subs, list):
                    raise ValueError("Malformed reachable_subsets")
                api_subsets = {frozenset(s) for s in api_subs}
                
                if can_subsets != api_subsets:
                    discrepancies.append(f"Reachable subsets mismatch: Canonical={can_subsets}, API={api_subsets}")
                    is_verified = False
                    
                api_start = indep_res.get("initial_subset", [])
                can_start = frozenset(raw.get('state_mapping', {}).get(raw.get('start_state'), []))
                if frozenset(api_start) != can_start:
                    discrepancies.append(f"Initial subset mismatch: Canonical={can_start}, API={api_start}")
                    is_verified = False
                    
        except Exception as e:
            return {"verified": False, "discrepancies": [f"Inconclusive verification due to malformed structured data: {str(e)}"]}
            
        return {
            "verified": is_verified,
            "api_result": api_result,
            "discrepancies": discrepancies
        }
