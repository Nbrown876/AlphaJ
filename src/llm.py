# Alpha J Language - LLM Integration
# Language: Alpha J
# Course: CIT4004 - Analysis of Programming Languages
# University of Technology, Jamaica
# Jonique Hosang Shaw, Neechelo Brown, Leigh-Ann Cammock, Damani Poyser

import os
from dotenv import load_dotenv
from typing import List

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

#OpenAI client
try:
    from openai import OpenAI, RateLimitError as OpenAIRateLimitError
    openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
except Exception:
    openai_client = None
    OpenAIRateLimitError = Exception

#Gemini client
try:
    import google.generativeai as genai
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=(
                "You are an expert programming language analyst. "
                "You are analyzing programs written in Alpha J, a custom high-level imperative language. "
                "Alpha J keywords: youare (declare variable), broadcast (print output), "
                "if/fallback/end (conditionals), cycle/end (while loop), "
                "try/catch/end (exception handling), @@ (comments). "
                "Operators: +, -, *, /, ^ (power), ==, !=, <, >, <=, >=. "
                "Please do not include bold text in your response because we are running in console."
            )
        )
    else:
        gemini_model = None
except Exception:
    gemini_model = None


SYSTEM_PROMPT = (
    "You are an expert programming language analyst. "
    "You are analyzing programs written in Alpha J, a custom high-level imperative language. "
    "Alpha J keywords: youare (declare variable), broadcast (print output), "
    "if/fallback/end (conditionals), cycle/end (while loop), "
    "try/catch/end (exception handling), @@ (comments). "
    "Operators: +, -, *, /, ^ (power), ==, !=, <, >, <=, >=. "
    "Please do not include bold text in your response because we are running in console."
)

class LLMAnalyzer:
    def __init__(self, model="gpt-4.1"):
        self.model = model

    def _send_prompt(self, prompt: str) -> str:
        """Send a prompt — tries OpenAI first, falls back to Gemini on quota error."""

        #Try OpenAI
        if openai_client:
            try:
                response = openai_client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user",   "content": prompt}
                    ],
                    temperature=0.2
                )
                return response.choices[0].message.content.strip()
            except OpenAIRateLimitError as e:
                print("[LLM] OpenAI unavailable (RateLimitError). Switching to Gemini fallback...")
                openai_err = e
            except Exception as e:
                print(f"[LLM] OpenAI error: {e}. Switching to Gemini fallback...")
                openai_err = e
        else:
            openai_err = Exception("OpenAI not configured.")

        #Gemini fallback
        if gemini_model:
            try:
                result = gemini_model.generate_content(prompt)
                return result.text.strip()
            except Exception as ge:
                return f"[LLM Error] Both OpenAI and Gemini failed. OpenAI: {openai_err} | Gemini: {ge}"

        return f"[LLM Error] OpenAI quota exhausted and Gemini is not configured. Original error: {openai_err}"

    def explain(self, source_code: str) -> str:
        prompt = f"""
The following is a program written in Alpha J, a custom programming language.
Please explain clearly what this program does, step by step.

Alpha J Program:
{source_code}
"""
        return self._send_prompt(prompt)

    def predict_output(self, source_code: str) -> str:
        prompt = f"""
The following is a program written in Alpha J, a custom programming language.
Based on the logic of the program, predict the exact console output it will produce.
Only return the predicted output lines, nothing else.

Alpha J Program:
{source_code}
"""
        return self._send_prompt(prompt)

    def compare(self, predicted: str, actual: str) -> dict:
        predicted_lines = [line.strip() for line in predicted.strip().splitlines() if line.strip()]
        actual_lines    = [line.strip() for line in actual.strip().splitlines() if line.strip()]
        match = predicted_lines == actual_lines
        return {
            "predicted": predicted_lines,
            "actual"   : actual_lines,
            "match"    : match
        }

    def analyze(self, source_code: str, actual_output: str) -> dict:
        print("\n[LLM] Sending program for explanation\n")
        explanation = self.explain(source_code)

        print("[LLM] Sending program for output prediction\n")
        predicted_output = self.predict_output(source_code)

        print("[LLM] Comparing prediction vs actual output\n")
        comparison = self.compare(predicted_output, actual_output)

        return {
            "explanation"     : explanation,
            "predicted_output": predicted_output,
            "actual_output"   : actual_output,
            "match"           : comparison["match"],
            "predicted_lines" : comparison["predicted"],
            "actual_lines"    : comparison["actual"]
        }


# Pretty Print Results
def print_llm_results(results: dict):
    print("\n" + "=" * 50)
    print("LLM ANALYSIS REPORT")
    print("=" * 50)

    print("\n--- Program Explanation ---")
    print(results["explanation"])

    print("\n--- LLM Predicted Output ---")
    for line in results["predicted_lines"]:
        print(f"  {line}")

    print("\n--- Interpreter Actual Output ---")
    for line in results["actual_lines"]:
        print(f"  {line}")

    print("\n--- Comparison Result ---")
    if results["match"]:
        print(" LLM prediction MATCHED interpreter output!")
    else:
        print(" LLM prediction DIFFERED from interpreter output.")
        predicted = results["predicted_lines"]
        actual    = results["actual_lines"]
        for i in range(max(len(predicted), len(actual))):
            p = predicted[i] if i < len(predicted) else "<​missing>"
            a = actual[i]    if i < len(actual)    else "<​missing>"
            if p != a:
                print(f"    Line {i+1}: Predicted: {p!r} | Actual: {a!r}")

    print("=" * 50)



# Development Test Runtime
if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from src.parser.parser_1 import parser
    from src.lexer import lexer
    from src.interpreter import Interpreter

    code = '''
youare x = 10
youare y = 5
broadcast "Starting program"
if x > y
    broadcast "x is greater than y"
fallback
    broadcast "y is greater than x"
end
broadcast "Done!"
'''

    ast = parser.parse(code, lexer=lexer)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    actual_output = "\n".join(interpreter.output_log)

    llm = LLMAnalyzer()
    results = llm.analyze(code, actual_output)
    print_llm_results(results)