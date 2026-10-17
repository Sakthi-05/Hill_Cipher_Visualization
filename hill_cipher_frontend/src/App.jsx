import { useMemo, useState } from "react";
import {
  ArrowLeft, ArrowRight, ArrowUpRight, Check, ChevronDown, ChevronLeft,
  ChevronRight, CircleHelp, Copy, Fingerprint, KeyRound, LockKeyhole,
  RotateCcw, ShieldCheck, Sparkles, UnlockKeyhole, WandSparkles
} from "lucide-react";

const API_URL = "https://hill-cipher-api.onrender.com";
const PRESETS = {
  "2": [[3, 3], [2, 5]],
  "3": [[6, 24, 1], [13, 16, 10], [20, 17, 15]]
};

function Matrix({ values, highlight = false }) {
  if (!Array.isArray(values)) return <span className="muted">—</span>;
  return <div className={`matrix ${values.length === 3 ? "matrix-three" : ""} ${highlight ? "matrix-highlight" : ""}`}>
    <span className="matrix-bracket left-bracket">[</span>
    <div className="matrix-values">
      {values.map((row, i) => <div className="matrix-row" key={i}>
        {row.map((v, j) => <span className="matrix-cell" key={j}>{v}</span>)}
      </div>)}
    </div>
    <span className="matrix-bracket right-bracket">]</span>
  </div>;
}

function Vector({ values, labels }) {
  if (!Array.isArray(values)) return null;
  return <div className="vector-wrap">
    <div className="matrix vector">
      <span className="matrix-bracket left-bracket">[</span>
      <div className="matrix-values">
        {values.map((v, i) => <div className="matrix-row" key={i}>
          <span className="matrix-cell">{v}</span>
        </div>)}
      </div>
      <span className="matrix-bracket right-bracket">]</span>
    </div>
    {labels && <div className="vector-labels">{labels.map((v, i) => <span key={i}>{v}</span>)}</div>}
  </div>;
}

function StepVisual({ step, operation, keyMatrix }) {
  if (!step) return null;
  const isDecrypt = operation === "decrypt";
  const title = step.title || step.name || `Calculation step`;
  const desc = step.description || step.explanation || "";
  const data = step.data || step;
  const block = step.block || step;
  const formula = data.formula || step.formula;
  const expressions = block.multiplication || data.multiplication || [];
  const inputVector = block.input_vector || data.input_vector;
  const rawVector = block.raw_result_vector || data.raw_result_vector;
  const outputVector = block.output_vector || data.output_vector;
  const matrix = block.key_matrix || data.key_matrix || keyMatrix;
  const outputLetters = block.output_letters || data.output_letters;
  const inputLetters = block.input_letters || data.input_letters;

  return <div className="step-visual">
    {desc && <p className="step-description">{desc}</p>}
    {formula && <div className="formula-banner">{formula}</div>}
    {(data.determinant !== undefined || data.determinant_mod_26 !== undefined) && (
      <div className="calculation-grid">
        <div className="calc-chip"><span>Determinant</span><strong>{data.determinant}</strong></div>
        <div className="calc-chip"><span>Modulo 26</span><strong>{data.determinant_mod_26}</strong></div>
        {data.gcd_determinant_26 !== undefined && <div className="calc-chip"><span>gcd(det, 26)</span><strong>{data.gcd_determinant_26}</strong></div>}
        {data.determinant_inverse_mod_26 !== undefined && <div className="calc-chip"><span>Determinant inverse</span><strong>{data.determinant_inverse_mod_26}</strong></div>}
      </div>
    )}
    {data.adjugate_matrix && <div className="matrix-pair">
      <div><span className="eyebrow">Adjugate matrix</span><Matrix values={data.adjugate_matrix}/></div>
      {data.inverse_key_matrix && <div><span className="eyebrow">Inverse key matrix</span><Matrix values={data.inverse_key_matrix} highlight/></div>}
    </div>}
    {matrix && inputVector && <div className="math-flow">
      <div className="math-item"><span className="eyebrow">{isDecrypt ? "Inverse key" : "Key matrix"}</span><Matrix values={isDecrypt ? (data.inverse_key_matrix || matrix) : matrix}/></div>
      <span className="math-operator">×</span>
      <div className="math-item"><span className="eyebrow">{isDecrypt ? "Cipher vector" : "Plaintext vector"}</span><Vector values={inputVector}/><span className="letter-label">{inputLetters || ""}</span></div>
      <span className="math-operator">=</span>
      <div className="math-item"><span className="eyebrow">Raw result</span><Vector values={rawVector || []}/></div>
      <span className="math-operator">mod 26</span>
      <div className="math-item result-math"><span className="eyebrow">Reduced vector</span><Vector values={outputVector || []}/><span className="letter-label">{outputLetters || ""}</span></div>
    </div>}
    {Array.isArray(expressions) && expressions.length > 0 && <div className="expression-list">
      <span className="eyebrow">Row-by-row multiplication</span>
      {expressions.map((item, i) => <div className="expression-row" key={i}>
        <span className="expression-index">R{i + 1}</span>
        <span>{item.expression || (item.terms || []).join(" + ")}</span>
        <strong>= {item.sum}</strong>
      </div>)}
    </div>}
    {Array.isArray(data.modulo_calculation) && <div className="modulo-list">
      {data.modulo_calculation.map((line, i) => <span key={i}><Check size={14}/>{line}</span>)}
    </div>}
    {data.input_letters && !inputVector && <div className="letter-conversion">
      <div><span className="eyebrow">Input letters</span><strong>{data.input_letters}</strong></div>
      {inputVector && <div><span className="eyebrow">Number vector</span><Vector values={inputVector}/></div>}
      {data.output_letters && <div><span className="eyebrow">Output letters</span><strong className="accent-text">{data.output_letters}</strong></div>}
    </div>}
    {data.message && <p className="step-description">{data.message}</p>}
    {!inputVector && !data.adjugate_matrix && data.determinant === undefined && !formula && !data.message && (
      <pre className="fallback-json">{JSON.stringify(data, null, 2)}</pre>
    )}
  </div>;
}

function buildSteps(result, operation) {
  const steps = [];
  if (operation === "encrypt") {
    const padding = result.padding || { count: 0, padded_plaintext: result.normalized_plaintext || result.original_text };
    steps.push({
      title: "Normalize and prepare the message",
      description: `The input is converted to uppercase English letters. Non A–Z characters are ignored. ${padding.count ? `${padding.count} X character(s) are appended to complete the final block.` : "No padding is required."}`,
      data: { formula: "A = 0, B = 1, …, Z = 25", message: `Prepared text: ${padding.padded_plaintext || result.normalized_plaintext || result.original_text}` }
    });
    if (result.numeric_plaintext) {
      steps.push({ title: "Convert letters to numbers", description: "Each letter is mapped to its alphabet index, then grouped into column vectors.", data: { message: `${padding.padded_plaintext || result.normalized_plaintext}: [${result.numeric_plaintext.join(", ")}]` } });
    }
  } else {
    const derivation = result.inverse_matrix_derivation || result.inverse_steps || result;
    steps.push({ title: "Derive the inverse key matrix", description: "A key is decryptable only when gcd(det(K), 26) = 1. The inverse is K⁻¹ = det(K)⁻¹ × adj(K) mod 26.", data: derivation });
  }
  const blocks = result.blocks || result.block_steps || [];
  blocks.forEach((block, i) => steps.push({
    title: `${operation === "encrypt" ? "Encrypt" : "Decrypt"} block ${block.block_index || i + 1}: ${block.input_letters || ""}`,
    description: operation === "encrypt"
      ? "Multiply the key matrix by the plaintext column vector, then reduce each row total modulo 26."
      : "Multiply the inverse key matrix by the ciphertext column vector, then reduce each row total modulo 26.",
    block,
    data: block
  }));
  if (!blocks.length) {
    const keys = Object.keys(result);
    steps.push({ title: "Calculation details", description: "The API returned the following calculation data.", data: result });
  }
  return steps;
}

export default function App() {
  const [operation, setOperation] = useState("encrypt");
  const [text, setText] = useState("HELP");
  const [dimension, setDimension] = useState("2");
  const [keyMatrix, setKeyMatrix] = useState(PRESETS["2"]);
  const [result, setResult] = useState(null);
  const [steps, setSteps] = useState([]);
  const [stepIndex, setStepIndex] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [apiState, setApiState] = useState("unknown");
  const [showKeyHelp, setShowKeyHelp] = useState(false);
  const [copied, setCopied] = useState(false);

  const currentStep = steps[stepIndex];
  const progress = steps.length ? ((stepIndex + 1) / steps.length) * 100 : 0;

  const changeDimension = (value) => {
    setDimension(value);
    setKeyMatrix(PRESETS[value].map(row => [...row]));
    setResult(null); setSteps([]); setStepIndex(0); setError("");
  };

  const updateKey = (row, col, value) => {
    const next = keyMatrix.map(r => [...r]);
    next[row][col] = value === "" ? 0 : Number(value);
    setKeyMatrix(next);
  };

  async function runCipher() {
    setLoading(true); setError(""); setResult(null); setSteps([]); setStepIndex(0);
    try {
      const response = await fetch(`${API_URL}/api/cipher/${operation}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, key_matrix: keyMatrix })
      });
      const body = await response.json();
      if (!response.ok) throw new Error(typeof body.detail === "string" ? body.detail : "The API rejected this request. Check your input and key.");
      setResult(body);
      setSteps(buildSteps(body, operation));
      setApiState("connected");
    } catch (err) {
      setError(err.message || "Could not connect to the backend. Is FastAPI running on port 8000?");
      setApiState("disconnected");
    } finally { setLoading(false); }
  }

  async function validateKey() {
    setError("");
    try {
      const response = await fetch(`${API_URL}/api/cipher/validate-key`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ key_matrix: keyMatrix })
      });
      const body = await response.json();
      if (!response.ok) throw new Error(body.detail || "Key validation failed.");
      if (!body.invertible_mod_26) throw new Error(body.reason || `This key is not invertible modulo 26 (gcd = ${body.gcd_determinant_26}). It cannot be used for decryption.`);
      setError("");
      setResult({ validation: body });
    } catch (err) { setError(err.message); }
  }

  const finalText = result?.ciphertext || result?.plaintext || result?.result;
  const isValidating = result?.validation;
  const resultLabel = operation === "encrypt" ? "Ciphertext" : "Recovered plaintext";

  async function copyResult() {
    if (!finalText) return;
    try { await navigator.clipboard.writeText(finalText); setCopied(true); setTimeout(() => setCopied(false), 1400); }
    catch { setError("Clipboard access was blocked by the browser. Select and copy the result manually."); }
  }

  function swapOperation() {
    setOperation(operation === "encrypt" ? "decrypt" : "encrypt");
    setText(operation === "encrypt" ? (result?.ciphertext || "HIAT") : "HELP");
    setResult(null); setSteps([]); setStepIndex(0); setError("");
  }

  return <div className="app-shell">
    <header className="topbar">
      <div className="brand">
        <div className="brand-mark"><Fingerprint size={22}/></div>
        <div><strong>HILL CIPHER <span>LAB</span></strong><small>CLASSICAL CRYPTOGRAPHY VISUALIZER</small></div>
      </div>
      <div className="topbar-right">
        <span className={`api-status ${apiState}`}><span className="status-dot"/>{apiState === "connected" ? "API connected" : apiState === "disconnected" ? "API unavailable" : "Local workspace"}</span>
        <a className="docs-link" href={`${API_URL}/docs`} target="_blank" rel="noreferrer">API docs <ArrowUpRight size={14}/></a>
      </div>
    </header>

    <main className="main-content">
      <section className="hero">
        <div className="hero-copy">
          <div className="overline"><Sparkles size={14}/> INTERACTIVE MATHEMATICS</div>
          <h1>See the cipher.<br/><span>Understand the math.</span></h1>
          <p>Explore how matrix multiplication transforms a message, one calculation at a time.</p>
        </div>
        <div className="hero-equation" aria-hidden="true">
          <div className="equation-label">THE HILL CIPHER</div>
          <div className="equation">C = K × P <span>mod 26</span></div>
          <div className="equation-caption">COLUMN VECTORS · A = 0 … Z = 25</div>
        </div>
      </section>

      <section className="workspace">
        <aside className="control-panel panel">
          <div className="panel-heading"><div><span className="section-index">01</span><h2>Set up your cipher</h2></div><span className="heading-icon"><KeyRound size={18}/></span></div>
          <div className="field-label">OPERATION</div>
          <div className="segmented">
            <button className={operation === "encrypt" ? "active" : ""} onClick={() => {setOperation("encrypt"); setResult(null); setSteps([]); setError("");}}><LockKeyhole size={15}/> Encrypt</button>
            <button className={operation === "decrypt" ? "active" : ""} onClick={() => {setOperation("decrypt"); setResult(null); setSteps([]); setError("");}}><UnlockKeyhole size={15}/> Decrypt</button>
          </div>

          <label className="field-label" htmlFor="message-input">{operation === "encrypt" ? "PLAINTEXT MESSAGE" : "CIPHERTEXT MESSAGE"}</label>
          <textarea id="message-input" value={text} onChange={e => setText(e.target.value)} placeholder="Type your message…" rows={3} maxLength={10000}/>
          <div className="input-foot"><span>English letters A–Z</span><span>{text.length}/10000</span></div>

          <div className="key-heading">
            <label className="field-label">KEY MATRIX</label>
            <button className="text-button" onClick={() => setShowKeyHelp(!showKeyHelp)}><CircleHelp size={14}/> How keys work</button>
          </div>
          {showKeyHelp && <div className="help-box">A valid key must be square (2×2 or 3×3). For decryption, its determinant must be coprime with 26: gcd(det(K), 26) = 1. Use integers in the matrix.</div>}
          <div className="matrix-config">
            <div className="dimension-select">
              <span>DIMENSION</span>
              <div className="dimension-buttons">
                <button className={dimension === "2" ? "chosen" : ""} onClick={() => changeDimension("2")}>2 × 2</button>
                <button className={dimension === "3" ? "chosen" : ""} onClick={() => changeDimension("3")}>3 × 3</button>
              </div>
            </div>
            <div className="editable-matrix" style={{"--n": dimension}}>
              {keyMatrix.map((row, i) => row.map((v, j) => <input key={`${i}-${j}`} aria-label={`Key matrix row ${i + 1} column ${j + 1}`} type="number" value={v} onChange={e => updateKey(i, j, e.target.value)} />))}
            </div>
          </div>
          <div className="key-actions">
            <button className="button-secondary" onClick={() => {setKeyMatrix(PRESETS[dimension].map(row => [...row])); setResult(null); setSteps([]); setError("");}}><RotateCcw size={14}/> Reset key</button>
            <button className="button-secondary" onClick={validateKey}><ShieldCheck size={14}/> Validate key</button>
          </div>

          {error && <div className="error-box"><span>!</span><p>{error}</p></div>}
          {isValidating && <div className="success-box"><Check size={16}/><div><strong>Key is invertible</strong><small>det(K) = {isValidating.determinant}; gcd(det(K), 26) = 1</small></div></div>}
          <button className="primary-button" onClick={runCipher} disabled={loading || !text.trim()}>
            {loading ? <span className="spinner"/> : <WandSparkles size={17}/>}
            {loading ? "Calculating…" : operation === "encrypt" ? "Encrypt & show calculations" : "Decrypt & show calculations"}
            {!loading && <ArrowRight size={16}/>}
          </button>
          <p className="panel-note"><ShieldCheck size={13}/> Educational cipher only. Not for protecting sensitive data.</p>
        </aside>

        <section className="results-column">
          <div className="result-overview panel">
            <div className="panel-heading"><div><span className="section-index">02</span><h2>Result overview</h2></div><span className="live-label"><span/> LIVE WORKSPACE</span></div>
            <div className="result-box">
              <div className="result-box-top"><span>{resultLabel}</span>{finalText && <button className="icon-button" title="Copy result" onClick={copyResult}>{copied ? <Check size={15}/> : <Copy size={15}/>}</button>}</div>
              <div className={`result-value ${finalText ? "has-result" : ""}`}>{finalText || <span>Run a calculation to see your result</span>}</div>
              {finalText && <div className="result-meta"><Check size={14}/> Calculation completed <span>·</span> {result?.blocks?.length || 0} block(s)</div>}
            </div>
            <div className="overview-footer">
              <div><span className="eyebrow">ALPHABET</span><strong>A = 0 → Z = 25</strong></div>
              <div><span className="eyebrow">MODULUS</span><strong>26</strong></div>
              <div><span className="eyebrow">KEY SIZE</span><strong>{dimension} × {dimension}</strong></div>
            </div>
          </div>

          <div className="steps-panel panel">
            <div className="panel-heading"><div><span className="section-index">03</span><h2>Mathematical walkthrough</h2></div><span className="steps-count">{steps.length ? `${String(stepIndex + 1).padStart(2,"0")} / ${String(steps.length).padStart(2,"0")}` : "READY"}</span></div>
            {!steps.length ? <div className="empty-state">
              <div className="empty-art"><div className="art-square"><span>3</span><span>3</span><span>2</span><span>5</span></div><span className="art-times">×</span><div className="art-vector"><span>7</span><span>4</span></div></div>
              <h3>Your calculations appear here</h3>
              <p>Enter a message and key, then run the cipher to explore each mathematical step.</p>
              <div className="empty-hint"><ChevronRight size={15}/> Each step includes the calculation, not just the answer.</div>
            </div> : <>
              <div className="step-progress"><div style={{width: `${progress}%`}}/></div>
              <div className="step-tabs">
                {steps.map((step, i) => <button key={i} onClick={() => setStepIndex(i)} className={stepIndex === i ? "current" : i < stepIndex ? "done" : ""} title={step.title}>
                  <span className="step-tab-number">{i < stepIndex ? <Check size={12}/> : String(i + 1).padStart(2, "0")}</span>
                  <span className="step-tab-title">{step.title}</span>
                </button>)}
              </div>
              <article className="active-step">
                <div className="active-step-heading"><div className="active-step-number">{String(stepIndex + 1).padStart(2,"0")}</div><div><span className="eyebrow">STEP {stepIndex + 1} OF {steps.length}</span><h3>{currentStep?.title}</h3></div></div>
                <StepVisual step={currentStep} operation={operation} keyMatrix={keyMatrix}/>
              </article>
              <div className="step-navigation">
                <button className="button-secondary" onClick={() => setStepIndex(Math.max(0, stepIndex - 1))} disabled={stepIndex === 0}><ChevronLeft size={16}/> Previous</button>
                <span>{Math.round(progress)}% explored</span>
                <button className="button-primary-small" onClick={() => setStepIndex(Math.min(steps.length - 1, stepIndex + 1))} disabled={stepIndex === steps.length - 1}>Next step <ChevronRight size={16}/></button>
              </div>
            </>}
          </div>
        </section>
      </section>

      <section className="concept-strip">
        <div className="concept-icon"><Fingerprint size={19}/></div>
        <div><strong>Why does the key need to be invertible?</strong><p>Decryption requires K⁻¹ modulo 26. That inverse exists only when gcd(det(K), 26) = 1.</p></div>
        <button onClick={() => {setShowKeyHelp(true); window.scrollTo({top: 0, behavior: "smooth"});}}>Explore key rules <ArrowUpRight size={14}/></button>
      </section>
      <footer><span>HILL CIPHER LAB <span className="footer-dot">·</span> A CLASSICAL CRYPTOGRAPHY EXPLORER</span><span>Built for learning matrix-based encryption</span></footer>
    </main>
  </div>;
}
