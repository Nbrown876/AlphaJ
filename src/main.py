# ============================================
# Alpha J Language - Main Entry Point
# Language: Alpha J
# Course: CIT4004 - Analysis of Programming Languages
# University of Technology, Jamaica
# ============================================

import sys
import os

# Establish dynamic project rooting
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.parser.parser_1 import parser
from src.lexer import lexer
from src.semantic import SemanticAnalyzer
from src.interpreter import Interpreter
from src.llm import LLMAnalyzer, print_llm_results

# ============================================
# UI Helpers
# ============================================

BANNER = r"""
  ___  _     _____  _   _    _              _
 / _ \| |   |  __ \| | | |  / \            | |
/ /_\ \ |   | |__) | |_| | / _ \           | |
|  _  | |   |  ___/|  _  |/ /_\ \          | |
| | | | |___| |    | | | / /   \ \   ______| |
\_| |_/_____|_|    \_| |_\/     \_/  \_|_____|

        Alpha J Language Compiler
   CIT4004 — University of Technology, Jamaica
"""

DIVIDER     = "=" * 56
THIN_DIV    = "-" * 56

def print_banner():
    print(DIVIDER)
    print(BANNER)
    print(DIVIDER)

def print_section(title: str):
    print(f"\n{THIN_DIV}")
    print(f"  {title}")
    print(THIN_DIV)

def print_success(msg: str):
    print(f"  ✅  {msg}")

def print_error(msg: str):
    print(f"  ❌  {msg}")

def print_info(msg: str):
    print(f"  ➤  {msg}")

# ============================================
# Core Pipeline Runner
# ============================================
def run_pipeline(source_code: str, use_llm: bool = True):
    """
    Runs the full Alpha J compiler pipeline:
    1. Parse  → AST
    2. Semantic Analysis
    3. Interpret → Actual Output
    4. LLM Analysis (optional)
    """

    # ── Step 1: Parse ──────────────────────────────
    print_section("STEP 1 — Lexing & Parsing")
    ast = parser.parse(source_code, lexer=lexer)

    if ast is None:
        print_error("Parsing failed. Please check your Alpha J syntax.")
        return
    print_success("Lexing & Parsing completed successfully.")

    # ── Step 2: Semantic Analysis ───────────────────
    print_section("STEP 2 — Semantic Analysis")
    analyzer = SemanticAnalyzer()
    passed = analyzer.analyze(ast)

    if not passed:
        print_error("Semantic errors found. Execution halted.")
        return
    print_success("Semantic Analysis passed.")

    # ── Step 3: Interpret ───────────────────────────
    print_section("STEP 3 — Interpreter Output")
    interpreter = Interpreter()
    interpreter.interpret(ast)
    actual_output = "\n".join(interpreter.output_log)

    # ── Step 4: LLM Analysis ────────────────────────
    if use_llm:
        print_section("STEP 4 — LLM Analysis")
        ask = input("  Run LLM analysis on this program? (y/n): ").strip().lower()
        if ask == 'y':
            llm = LLMAnalyzer()
            results = llm.analyze(source_code, actual_output)
            print_llm_results(results)
        else:
            print_info("LLM analysis skipped.")

    print(f"\n{DIVIDER}")
    print("  Alpha J execution complete.")
    print(DIVIDER)


# ============================================
# File Mode
# ============================================
def run_file(filepath: str):
    print_banner()
    print_info(f"File Mode — Loading: {filepath}")

    if not os.path.exists(filepath):
        print_error(f"File not found: {filepath}")
        sys.exit(1)

    if not filepath.endswith(".alphaj"):
        print_error("File must have a .alphaj extension.")
        sys.exit(1)

    with open(filepath, "r") as f:
        source_code = f.read()

    print_success(f"File loaded successfully. ({len(source_code.splitlines())} lines)")
    run_pipeline(source_code)


# ============================================
# Interactive Mode
# ============================================
def run_interactive():
    print_banner()
    print_info("Interactive Mode — Type your Alpha J code below.")
    print_info("Type 'run' on a new line to execute.")
    print_info("Type 'clear' to reset the editor.")
    print_info("Type 'exit' to quit.")
    print(f"\n{THIN_DIV}")

    lines = []

    while True:
        try:
            line = input("  > ")
        except (EOFError, KeyboardInterrupt):
            print("\n\n  Goodbye! 👋")
            break

        if line.strip().lower() == "exit":
            print("\n  Goodbye! 👋")
            break

        elif line.strip().lower() == "clear":
            lines = []
            print_info("Editor cleared. Start typing your program again.")

        elif line.strip().lower() == "run":
            if not lines:
                print_error("No code to run. Type some Alpha J code first.")
                continue

            source_code = "\n".join(lines)
            print(f"\n{DIVIDER}")
            print("  Running your Alpha J program...")
            print(DIVIDER)
            run_pipeline(source_code)

            # Ask if they want to continue or exit
            print()
            again = input("  Run another program? (y/n): ").strip().lower()
            if again == 'y':
                lines = []
                print_info("Editor cleared. Type your next program.")
                print(THIN_DIV)
            else:
                print("\n  Goodbye! 👋")
                break

        else:
            lines.append(line)


# ============================================
# Entry Point
# ============================================
if __name__ == "__main__":
    if len(sys.argv) == 2:
        # File mode — python main.py program.alphaj
        run_file(sys.argv[1])
    else:
        # Interactive mode — python main.py
        run_interactive()
