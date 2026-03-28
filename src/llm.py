# ============================================
# Alpha J Language - LLM Integration
# Language: Alpha J
# Course: CIT4004 - Analysis of Programming Languages
# University of Technology, Jamaica
# ============================================

import os
from openai import OpenAI
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam
from dotenv import load_dotenv
from typing import List

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# LLM Analysis Engine
class LLMAnalyzer:
    def __init__(self, model="gpt-4.1"):
        self.model = model

    def _send_prompt(self, prompt: str) -> str:
        """Send a prompt to OpenAI and return the response text."""
        try:
            messages: List[ChatCompletionSystemMessageParam | ChatCompletionUserMessageParam] = [
                ChatCompletionSystemMessageParam(
                    role="system",
                    content=(
                        "You are an expert programming language analyst. "
                        "You are analyzing programs written in Alpha J, a custom high-level imperative language. "
                        "Alpha J keywords: youare (declare variable), broadcast (print output), "
                        "if/fallback/end (conditionals), cycle/end (while loop), "
                        "try/catch/end (exception handling), @@ (comments). "
                        "Operators: +, -, *, /, ^ (power), ==, !=, <, >, <=, >=."
                        "Please do not include bold text in your response because we are running in console"
                    )
                ),
                ChatCompletionUserMessageParam(
                    role="user",
                    content=prompt
                )
            ]
            
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.2
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[LLM Error] {str(e)}"

    def explain(self, source_code: str) -> str:
        """Ask the LLM to explain what the Alpha J program does."""
        prompt = f"""
The following is a program written in Alpha J, a custom programming language.
Please explain clearly what this program does, step by step.

Alpha J Program:
{source_code}
"""
        return self._send_prompt(prompt)

    def predict_output(self, source_code: str) -> str:
        """Ask the LLM to predict the output of the Alpha J program."""
        prompt = f"""
The following is a program written in Alpha J, a custom programming language.
Based on the logic of the program, predict the exact console output it will produce.
Only return the predicted output lines, nothing else.

Alpha J Program:
{source_code}
"""
        return self._send_prompt(prompt)

    def compare(self, predicted: str, actual: str) -> dict:
        """Compare LLM predicted output vs interpreter actual output."""
        predicted_lines = [line.strip() for line in predicted.strip().splitlines() if line.strip()]
        actual_lines    = [line.strip() for line in actual.strip().splitlines() if line.strip()]

        match = predicted_lines == actual_lines

        return {
            "predicted": predicted_lines,
            "actual"   : actual_lines,
            "match"    : match
        }

    def analyze(self, source_code: str, actual_output: str) -> dict:
        """
        Full pipeline:
        1. Explain the program
        2. Predict the output
        3. Compare prediction vs actual
        """
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


# ============================================
# Pretty Print Results
# ============================================
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
        print("\n  Differences:")
        predicted = results["predicted_lines"]
        actual    = results["actual_lines"]
        max_len   = max(len(predicted), len(actual))
        for i in range(max_len):
            p = predicted[i] if i < len(predicted) else "<missing>"
            a = actual[i]    if i < len(actual)    else "<missing>"
            if p != a:
                print(f"    Line {i+1}: Predicted: {p!r} | Actual: {a!r}")

    print("=" * 50)


# ============================================
# Development Test Runtime
# ============================================
if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from src.parser.parser_1 import parser
    from src.lexer import lexer
    from src.interpreter import Interpreter

    # Sample Alpha J test program
    code = '''
youare x = 10
youare y = 5

broadcast "Starting program"

if x > y
    broadcast "x is greater than y"
fallback
    broadcast "y is greater than x"
end

youare c = 0
cycle c < 3
    broadcast "Counting: " c
    c = c + 1
end

broadcast "Done!"
'''

    # Step 1 — Run through interpreter to get actual output
    ast = parser.parse(code, lexer=lexer)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    actual_output = "\n".join(interpreter.output_log)

    # Step 2 — Run LLM analysis
    llm = LLMAnalyzer()
    results = llm.analyze(code, actual_output)

    # Step 3 — Print full report
    print_llm_results(results)

