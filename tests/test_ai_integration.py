import os
import json
import unittest
from unittest.mock import patch, MagicMock

from core.ai_integration import AIIntegrationPolicy

class TestGeminiIntegrationPolicy(unittest.TestCase):
    def setUp(self):
        self.dfa = {
            "states": ["A", "B", "C"],
            "alphabet": ["0", "1"],
            "start_state": "A",
            "accepting_states": ["B"],
            "transitions": {
                "A": {"0": "B", "1": "A"},
                "B": {"0": "C", "1": "A"},
                "C": {"0": "B", "1": "A"}
            }
        }
        
    @patch('os.environ.get')
    def test_gemini_unavailable(self, mock_env):
        mock_env.return_value = None # No API key
        
        result, ai_response = AIIntegrationPolicy.solve_and_verify(self.dfa)
        
        # Deterministic result MUST remain correct
        self.assertEqual(len(result['states']), 2)
        # API missing must not prevent local minimization
        self.assertIn("error", ai_response)
        self.assertEqual(ai_response["error"], "API unavailable")

    @patch('core.ai_integration.genai.GenerativeModel')
    def test_gemini_malformed(self, mock_model_class):
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "This is not JSON at all."
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        # Set a dummy key to trigger the call
        with patch('os.environ.get', return_value="dummy_key"):
            result, ai_response = AIIntegrationPolicy.solve_and_verify(self.dfa)
            
            self.assertEqual(len(result['states']), 2)
            self.assertIn("error", ai_response)
            self.assertIn("Expecting value", ai_response["error"]) # JSONDecodeError substring

    @patch('core.ai_integration.genai.GenerativeModel')
    def test_gemini_contradictory(self, mock_model_class):
        mock_model = MagicMock()
        mock_response = MagicMock()
        # Gemini hallucinates a 3-state output (incorrect)
        wrong_dfa = {
            "states": ["A", "B", "C"],
            "alphabet": ["0", "1"],
            "start_state": "A",
            "accepting_states": ["B"],
            "transitions": {}
        }
        mock_response.text = json.dumps(wrong_dfa)
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        with patch('os.environ.get', return_value="dummy_key"), \
             patch('core.ai_integration.logger.warning') as mock_log:
             
            result, ai_response = AIIntegrationPolicy.solve_and_verify(self.dfa)
            
            # Deterministic overrides Gemini
            self.assertEqual(len(result['states']), 2)
            self.assertTrue(ai_response.get("discrepancy"))
            
            # Log the discrepancy safely
            mock_log.assert_called_once()
            args = mock_log.call_args[0]
            self.assertIn("DISCREPANCY", args[0])

if __name__ == '__main__':
    unittest.main()
