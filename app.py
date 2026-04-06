# ============================================
# Alpha J Language - Web IDE
# Language: Alpha J
# Course: CIT4004 - Analysis of Programming Languages
# University of Technology, Jamaica
# ============================================

from flask import Flask, request, jsonify, render_template_string
import sys, os, io, contextlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.parser.parser_1 import parser
from src.lexer import lexer
from src.semantic import SemanticAnalyzer
from src.interpreter import Interpreter

import ply.lex as lex

app = Flask(__name__)

# ============================================
# HTML Template (Inline)
# ============================================
HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Alpha J — Online IDE</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }

    body {
      font-family: 'Segoe UI', sans-serif;
      background: #0d1117;
      color: #c9d1d9;
      height: 100vh;
      display: flex;
      flex-direction: column;
    }

    /* ── Header ── */
    header {
      background: #161b22;
      border-bottom: 1px solid #30363d;
      padding: 12px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .logo {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .logo-icon {
      width: 36px; height: 36px;
      background: linear-gradient(135deg, #58a6ff, #bc8cff);
      border-radius: 8px;
      display: flex; align-items: center; justify-content: center;
      font-weight: bold; font-size: 20px; color: #fff;
    }

    .logo-text h1 { font-size: 20px; color: #f0f6fc; }
    .logo-text p  { font-size: 15px; color: #8b949e; }

    .header-right { font-size: 20px; color: #8b949e; text-align: right; }

    /* ── Main Layout ── */
    .main {
      display: flex;
      flex: 1;
      overflow: hidden;
    }

    /* ── Editor Panel ── */
    .editor-panel {
      display: flex;
      flex-direction: column;
      width: 50%;
      border-right: 1px solid #30363d;
    }

    .panel-header {
      background: #161b22;
      border-bottom: 1px solid #30363d;
      padding: 8px 16px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 20px;
      color: #8b949e;
    }

    .panel-title {
      display: flex; align-items: center; gap: 8px;
      font-weight: 600; color: #f0f6fc; font-size: 15px;
    }

    .dot { width: 8px; height: 8px; border-radius: 50%; }
    .dot-red    { background: #ff5f57; }
    .dot-yellow { background: #febc2e; }
    .dot-green  { background: #28c840; }

    #editor {
      flex: 1;
      background: #0d1117;
      color: #c9d1d9;
      border: none;
      outline: none;
      padding: 16px;
      font-family: 'Courier New', monospace;
      font-size: 20px;
      line-height: 1.6;
      resize: none;
      tab-size: 4;
    }

    #editor::placeholder { color: #484f58; }

    .editor-footer {
      background: #161b22;
      border-top: 1px solid #30363d;
      padding: 10px 16px;
      display: flex;
      gap: 10px;
      align-items: center;
    }

    .btn {
      padding: 8px 20px;
      border: none;
      border-radius: 6px;
      font-size: 15px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
    }

    .btn-run {
      background: linear-gradient(135deg, #238636, #2ea043);
      color: #fff;
    }
    .btn-run:hover { background: linear-gradient(135deg, #2ea043, #3fb950); }

    .btn-clear {
      background: #21262d;
      color: #c9d1d9;
      border: 1px solid #30363d;
    }
    .btn-clear:hover { background: #30363d; }

    .btn-llm {
      background: linear-gradient(135deg, #6e40c9, #bc8cff);
      color: #fff;
    }
    .btn-llm:hover { opacity: 0.85; }

    .btn:disabled { opacity: 0.5; cursor: not-allowed; }

    /* ── Output Panel ── */
    .output-panel {
      display: flex;
      flex-direction: column;
      width: 50%;
    }

    .tabs {
      display: flex;
      background: #161b22;
      border-bottom: 1px solid #30363d;
    }

    .tab {
      padding: 10px 20px;
      font-size: 20px;
      font-weight: 600;
      cursor: pointer;
      color: #8b949e;
      border-bottom: 2px solid transparent;
      transition: all 0.2s;
    }

    .tab.active {
      color: #58a6ff;
      border-bottom-color: #58a6ff;
    }

    .tab-content { display: none; flex: 1; overflow-y: auto; padding: 16px; }
    .tab-content.active { display: block; }

    .output-box {
      background: #161b22;
      border: 1px solid #30363d;
      border-radius: 8px;
      padding: 14px;
      font-family: 'Courier New', monospace;
      font-size: 15px;
      line-height: 1.7;
      min-height: 200px;
      white-space: pre-wrap;
      word-break: break-word;
    }

    .status-bar {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 10px;
      font-size: 20px;
      font-weight: 600;
    }

    .badge {
      padding: 3px 10px;
      border-radius: 20px;
      font-size: 15px;
      font-weight: 700;
    }

    .badge-success { background: #1a4731; color: #3fb950; }
    .badge-error   { background: #4d1a1a; color: #f85149; }
    .badge-info    { background: #1a2d4d; color: #58a6ff; }
    .badge-purple  { background: #2d1a4d; color: #bc8cff; }

    .step-block {
      margin-bottom: 14px;
      border-left: 3px solid #30363d;
      padding-left: 12px;
    }

    .step-block.pass { border-left-color: #3fb950; }
    .step-block.fail { border-left-color: #f85149; }

    .step-title {
      font-size: 15px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 4px;
      color: #8b949e;
    }

    .step-block.pass .step-title { color: #3fb950; }
    .step-block.fail .step-title { color: #f85149; }

    .output-text { color: #e6edf3; }
    .error-text  { color: #f85149; }

    .placeholder-text {
      color: #484f58;
      font-style: italic;
      text-align: center;
      margin-top: 40px;
      font-size: 15px;
    }

    .spinner {
      display: none;
      width: 16px; height: 16px;
      border: 2px solid #30363d;
      border-top-color: #58a6ff;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }

    @keyframes spin { to { transform: rotate(360deg); } }

    /* ── Footer ── */
    footer {
      background: #161b22;
      border-top: 1px solid #30363d;
      padding: 6px 24px;
      font-size: 15px;
      color: #484f58;
      display: flex;
      justify-content: space-between;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #0d1117; }
    ::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }

    /* ── Keywords highlight hint ── */
    .keywords {
      display: flex; flex-wrap: wrap; gap: 6px;
      margin-bottom: 12px;
    }
    .kw {
      background: #1f2937;
      border: 1px solid #374151;
      border-radius: 4px;
      padding: 2px 8px;
      font-size: 15px;
      font-family: monospace;
      color: #93c5fd;
    }
  </style>
</head>
<body>

<!-- Header -->
<header>
  <div class="logo">
    <div class="logo-icon">αJ</div>
    <div class="logo-text">
      <h1>Alpha J — Online IDE</h1>
      <p>CIT4004 · University of Technology, Jamaica</p>
    </div>
  </div>
  <div class="header-right">
    Imperative · General Purpose · High Level<br/>
    Powered by Python + PLY
  </div>
</header>

<!-- Main -->
<div class="main">

  <!-- Editor -->
  <div class="editor-panel">
    <div class="panel-header">
      <div class="panel-title">
        <span class="dot dot-red"></span>
        <span class="dot dot-yellow"></span>
        <span class="dot dot-green"></span>
        &nbsp; program.alphaj
      </div>
      <span>Alpha J Editor</span>
    </div>

    <textarea id="editor" spellcheck="false" placeholder="@@ Write your Alpha J code here...

youare x = 10
youare y = 5

if x > y
    broadcast &quot;x is greater!&quot;
fallback
    broadcast &quot;y is greater!&quot;
end"></textarea>

    <div class="editor-footer">
      <button class="btn btn-run" onclick="runCode()">▶ Run</button>
      <button class="btn btn-clear" onclick="clearAll()">✕ Clear</button>
      <button class="btn btn-llm" onclick="runLLM()">✦ LLM Analysis</button>
      <div class="spinner" id="spinner"></div>
    </div>
  </div>

  <!-- Output -->
  <div class="output-panel">
    <div class="tabs">
      <div class="tab active" onclick="switchTab('output')">Output</div>
      <!-- JS TOKEN N TREE -->
      <div class="tab" onclick="switchTab('tokens')">Tokens</div>
      <div class="tab" onclick="switchTab('tree')">Parse Tree</div>
      <div class="tab" onclick="switchTab('llm')">LLM Analysis</div>
      <div class="tab" onclick="switchTab('help')">Help</div>
    </div>

    <!-- Output Tab -->
    <div class="tab-content active" id="tab-output">
      <div id="output-area">
        <p class="placeholder-text">▶ Run your Alpha J program to see output here.</p>
      </div>
    </div>

    <!-- Tokens Tab -->
    <div class="tab-content" id="tab-tokens">
      <div class="output-box" id="tokens-area">
        <p class="placeholder-text">Tokens will appear here.</p>
      </div>
    </div>

    <!-- Parse Tree Tab -->
    <div class="tab-content" id="tab-tree">
      <div class="output-box" id="tree-area">
        <p class="placeholder-text">Parse tree will appear here.</p>
      </div>
    </div>

    <!-- LLM Tab -->
    <div class="tab-content" id="tab-llm">
      <div id="llm-area">
        <p class="placeholder-text">✦ Click "LLM Analysis" to analyze your program with GPT.</p>
      </div>
    </div>

    <!-- Help Tab -->
    <div class="tab-content" id="tab-help">
      <div class="keywords">
        <span class="kw">youare</span>
        <span class="kw">broadcast</span>
        <span class="kw">if</span>
        <span class="kw">fallback</span>
        <span class="kw">end</span>
        <span class="kw">cycle</span>
        <span class="kw">try</span>
        <span class="kw">catch</span>
        <span class="kw">@@</span>
      </div>
      <div class="output-box" style="font-size:13px; line-height:1.9;">

<span style="color:#8b949e; font-weight:bold;">@@ ── RESERVED WORDS ──────────────────────────</span>

<span style="color:#58a6ff;">@@</span>  <span style="color:#484f58;">— comment, ignored by the compiler</span>
<span style="color:#58a6ff;">@@ anything written after @@ is not executed</span>

<span style="color:#bc8cff;">youare</span> x = 10          <span style="color:#484f58;">@@ youare — declares a new variable and assigns a value</span>
x = x + 1               <span style="color:#484f58;">@@ = (assignto) — reassigns a value to an existing variable</span>

<span style="color:#bc8cff;">broadcast</span> "Hello" x    <span style="color:#484f58;">@@ broadcast — prints one or more values to the console</span>

<span style="color:#bc8cff;">if</span> x &gt; 5               <span style="color:#484f58;">@@ if — starts a conditional block, runs if condition is true</span>
    broadcast "big"
<span style="color:#bc8cff;">fallback</span>               <span style="color:#484f58;">@@ fallback — runs if the if condition was false (like else)</span>
    broadcast "small"
<span style="color:#bc8cff;">end</span>                    <span style="color:#484f58;">@@ end — closes an if, cycle, or try/catch block</span>

<span style="color:#bc8cff;">cycle</span> x &lt; 10           <span style="color:#484f58;">@@ cycle — repeats a block while condition is true (like while)</span>
    broadcast x
    x = x + 1
<span style="color:#bc8cff;">end</span>

<span style="color:#bc8cff;">try</span>                    <span style="color:#484f58;">@@ try — attempts code that might cause a runtime error</span>
    youare y = x / 0
<span style="color:#bc8cff;">catch</span>                  <span style="color:#484f58;">@@ catch — runs if an error occurred inside the try block</span>
    broadcast "Error caught!"
<span style="color:#bc8cff;">end</span>

<span style="color:#8b949e; font-weight:bold;">@@ ── OPERATORS ───────────────────────────────</span>

youare a = 10
youare b = 3

youare add = a + b      <span style="color:#484f58;">@@ +  addition</span>
youare sub = a - b      <span style="color:#484f58;">@@ -  subtraction</span>
youare mul = a * b      <span style="color:#484f58;">@@ *  multiplication</span>
youare div = a / b      <span style="color:#484f58;">@@ /  division</span>
youare pow = b ^ 2      <span style="color:#484f58;">@@ ^  power / exponentiation</span>

<span style="color:#8b949e; font-weight:bold;">@@ ── COMPARISON OPERATORS ────────────────────</span>

<span style="color:#bc8cff;">if</span> a == 10             <span style="color:#484f58;">@@ == checks if two values are equal</span>
    broadcast "equal"
<span style="color:#bc8cff;">end</span>
<span style="color:#bc8cff;">if</span> a != b              <span style="color:#484f58;">@@ != checks if two values are NOT equal</span>
    broadcast "not equal"
<span style="color:#bc8cff;">end</span>
<span style="color:#bc8cff;">if</span> b &lt; a               <span style="color:#484f58;">@@ &lt;  less than</span>
    broadcast "b is less"
<span style="color:#bc8cff;">end</span>
<span style="color:#bc8cff;">if</span> a &gt; b               <span style="color:#484f58;">@@ &gt;  greater than</span>
    broadcast "a is greater"
<span style="color:#bc8cff;">end</span>
<span style="color:#bc8cff;">if</span> b &lt;= 3              <span style="color:#484f58;">@@ &lt;= less than or equal to</span>
    broadcast "at most 3"
<span style="color:#bc8cff;">end</span>
<span style="color:#bc8cff;">if</span> a &gt;= 10             <span style="color:#484f58;">@@ &gt;= greater than or equal to</span>
    broadcast "at least 10"
<span style="color:#bc8cff;">end</span>
      </div>
    </div>
  </div>
</div>

<!-- Footer -->
<footer>
  <span>Alpha J Language Compiler · CIT4004 Sem 2 2025/2026</span>
  <span>Python + PLY · OpenAI GPT</span>
</footer>

<script>
  function switchTab(name) {
    document.querySelectorAll('.tab').forEach((t, i) => { 
      t.classList.toggle('active', ['output','tokens','tree','llm','help'][i] === name);
    });
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    document.getElementById('tab-' + name).classList.add('active');
  }

  function setLoading(on) {
    document.getElementById('spinner').style.display = on ? 'block' : 'none';
    document.querySelectorAll('.btn').forEach(b => b.disabled = on);
  }

  function clearAll() {
    document.getElementById('editor').value = '';
    document.getElementById('output-area').innerHTML = '<p class="placeholder-text">▶ Run your Alpha J program to see output here.</p>';
    document.getElementById('llm-area').innerHTML = '<p class="placeholder-text">✦ Click "LLM Analysis" to analyze your program with GPT.</p>';
  }

  async function runCode() {
    const code = document.getElementById('editor').value.trim();
    if (!code) { alert('Please write some Alpha J code first!'); return; }

    setLoading(true);
    switchTab('output');

    try {
      const res  = await fetch('/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code })
      });
      const data = await res.json();
      renderOutput(data);
    } catch(e) {
      document.getElementById('output-area').innerHTML = `<div class="error-text">Network error: ${e.message}</div>`;
    }

    setLoading(false);
  }

  async function runLLM() {
    const code = document.getElementById('editor').value.trim();
    if (!code) { alert('Please write some Alpha J code first!'); return; }

    setLoading(true);
    switchTab('llm');
    document.getElementById('llm-area').innerHTML = '<p class="placeholder-text">✦ Contacting GPT... please wait.</p>';

    try {
      const res  = await fetch('/llm', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code })
      });
      const data = await res.json();
      renderLLM(data);
    } catch(e) {
      document.getElementById('llm-area').innerHTML = `<div class="error-text">Network error: ${e.message}</div>`;
    }

    setLoading(false);
  }

  function renderOutput(data) {
    let html = '';

    // Step 1
    html += `<div class="step-block ${data.parse_ok ? 'pass' : 'fail'}">
      <div class="step-title">Step 1 — Lexing & Parsing</div>
      <div>${data.parse_ok ? '✅ Passed' : '❌ ' + escHtml(data.parse_error)}</div>
    </div>`;

    // Step 2
    if (data.parse_ok) {
      html += `<div class="step-block ${data.semantic_ok ? 'pass' : 'fail'}">
        <div class="step-title">Step 2 — Semantic Analysis</div>
        <div>${data.semantic_ok ? '✅ Passed' : '❌ ' + escHtml(data.semantic_error)}</div>
      </div>`;
    }

    // Step 3
    if (data.semantic_ok) {
      html += `<div class="step-block pass">
        <div class="step-title">Step 3 — Interpreter Output</div>
        <div class="output-box output-text">${escHtml(data.output) || '<span style="color:#484f58">No output produced.</span>'}</div>
      </div>`;
    }

    document.getElementById('output-area').innerHTML = html;
    
   
    document.getElementById('tokens-area').innerHTML = `<pre>${escHtml(data.tokens)}</pre>`;

    document.getElementById('tree-area').innerHTML = `<pre>${escHtml(data.tree)}</pre>`;
  }

  function renderLLM(data) {
    if (data.error) {
      document.getElementById('llm-area').innerHTML = `<div class="error-text">❌ ${escHtml(data.error)}</div>`;
      return;
    }

    const match = data.match;
    const badge = match
      ? '<span class="badge badge-success">✅ MATCHED</span>'
      : '<span class="badge badge-error">❌ DIFFERED</span>';

    let html = `
      <div class="step-block pass">
        <div class="step-title">Program Explanation</div>
        <div class="output-box output-text">${escHtml(data.explanation)}</div>
      </div>
      <div class="step-block ${match ? 'pass' : 'fail'}">
        <div class="step-title">Predicted Output</div>
        <div class="output-box output-text">${escHtml(data.predicted_output)}</div>
      </div>
      <div class="step-block pass">
        <div class="step-title">Interpreter Actual Output</div>
        <div class="output-box output-text">${escHtml(data.actual_output)}</div>
      </div>
      <div class="step-block ${match ? 'pass' : 'fail'}">
        <div class="step-title">Comparison Result &nbsp; ${badge}</div>
        <div>${match ? 'LLM prediction matched interpreter output!' : escHtml(data.diff)}</div>
      </div>`;

    document.getElementById('llm-area').innerHTML = html;
  }

  function escHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g,'&amp;')
      .replace(/</g,'&lt;')
      .replace(/>/g,'&gt;')
      .replace(/\n/g,'<br/>');
  }
</script>
</body>
</html>
"""

#Helper Functions JS
def get_tokens(source):
   # Reset lexer
    lexer.lineno = 1
    lexer.input(source)

    tokens_list = []

    while True:
        tok = lexer.token()
        if not tok:
            break

        tokens_list.append(
            f"{tok.type:<12} → {tok.value}"
        )

    return "\n".join(tokens_list)


def tree_to_string(node, indent=0):
    space = "  " * indent
    result = ""

    if isinstance(node, tuple):
        result += f"{space}{node[0]}\n"
        for child in node[1:]:
            result += tree_to_string(child, indent + 1)

    elif isinstance(node, list):
        for item in node:
            result += tree_to_string(item, indent)

    else:
        result += f"{space}{node}\n"

    return result


# ============================================
# Routes
# ============================================
@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/run", methods=["POST"])
def run_code():
    data = request.get_json()
    source = data.get("code", "")

    result = {
      "parse_ok"     : False,
      "parse_error"  : "",
      "semantic_ok"  : False,
      "semantic_error": "",
      "output"       : "",
      "tokens": "",
      "tree": ""
    }

    # Step 1 — Parse
    try:
        ast = parser.parse(source, lexer=lexer)
        if ast is None:
            result["parse_error"] = "Parsing failed. Check your syntax."
            return jsonify(result)
        result["parse_ok"] = True
        
        result["tokens"] = get_tokens(source)
        result["tree"] = tree_to_string(ast)
    except Exception as e:
        result["parse_error"] = str(e)
        return jsonify(result)

    # Step 2 — Semantic
    try:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            analyzer = SemanticAnalyzer()
            passed   = analyzer.analyze(ast)

        if not passed:
            result["semantic_error"] = buf.getvalue().strip()
            return jsonify(result)
        result["semantic_ok"] = True
    except Exception as e:
        result["semantic_error"] = str(e)
        return jsonify(result)

    # Step 3 — Interpret
    try:
        interp = Interpreter()
        interp.interpret(ast)
        result["output"] = "\n".join(interp.output_log)
    except Exception as e:
        result["output"] = f"Runtime Error: {str(e)}"

    return jsonify(result)


@app.route("/llm", methods=["POST"])
def run_llm():
    data   = request.get_json()
    source = data.get("code", "")

    # First run interpreter to get actual output
    try:
        ast    = parser.parse(source, lexer=lexer)
        interp = Interpreter()
        interp.interpret(ast)
        actual = "\n".join(interp.output_log)
    except Exception as e:
        return jsonify({"error": f"Could not run interpreter: {str(e)}"})

    # Run LLM
    try:
        from src.llm import LLMAnalyzer
        llm     = LLMAnalyzer()
        results = llm.analyze(source, actual)

        # Build diff string
        diff = ""
        if not results["match"]:
            pred = results["predicted_lines"]
            act  = results["actual_lines"]
            lines = []
            for i in range(max(len(pred), len(act))):
                p = pred[i] if i < len(pred) else "<missing>"
                a = act[i]  if i < len(act)  else "<missing>"
                if p != a:
                    lines.append(f"Line {i+1}: Predicted: {p!r} | Actual: {a!r}")
            diff = "\n".join(lines)

        return jsonify({
            "explanation"     : results["explanation"],
            "predicted_output": results["predicted_output"],
            "actual_output"   : actual,
            "match"           : results["match"],
            "diff"            : diff
        })
    except Exception as e:
        return jsonify({"error": str(e)})


# ============================================
# Entry Point
# ============================================
if __name__ == "__main__":
    app.run(debug=True, port=5000)
