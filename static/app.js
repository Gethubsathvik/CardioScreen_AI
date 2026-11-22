// CardioScreen AI - Application JavaScript
// Medical Risk Prediction UI

const SAMPLE = {
  age: 58,
  sex: 1,
  cp: 0,
  trestbps: 140,
  chol: 240,
  fbs: 0,
  restecg: 1,
  thalach: 122,
  exang: 1,
  oldpeak: 2.0,
  slope: 1,
  ca: 1,
  thal: 3,
};

const $ = (s) => document.querySelector(s);
const esc = (s) =>
  String(s).replace(/[&<>"]/g, (c) => ({
    "&": "&",
    "<": "<",
    ">": ">",
    '"': """,
  }[c]));

let spec = [];

async function init() {
  try {
    spec = await (await fetch("/api/features")).json();
    renderForm();
    loadExamplePatient();
    loadModelInfo();
  } catch (error) {
    console.error("Failed to initialize:", error);
    showError("Failed to load application. Please refresh the page.");
  }
}

function renderForm() {
  const form = $("#f");
  if (!form) return;

  form.innerHTML = spec
    .map((f) => {
      const unit = f.unit ? ` (${f.unit})` : "";
      const field = f.choices.length
        ? `<select name="${f.name}">${f.choices
            .map((c) => `<option value="${c.value}">${esc(c.label)}</option>`)
            .join("")}</select>`
        : `<input name="${f.name}" type="number" min="${f.min}" max="${f.max}" step="${f.name === "oldpeak" ? 0.1 : 1}" required>`;
      return `<div><label>${esc(f.label)}${unit}</label>${field}</div>`;
    })
    .join("") +
    `<button type="submit">🔍 Predict</button><button type="button" class="secondary" id="ex">👤 Load example patient</button>`;

  const exampleBtn = $("#ex");
  if (exampleBtn) {
    exampleBtn.onclick = () => fill(SAMPLE);
  }

  form.addEventListener("submit", handlePredict);
}

function fill(values) {
  for (const [key, value] of Object.entries(values)) {
    const el = document.querySelector(`[name=${key}]`);
    if (el) el.value = value;
  }
}

function loadExamplePatient() {
  fill(SAMPLE);
}

async function loadModelInfo() {
  try {
    const response = await fetch("/api/model");
    if (response.ok) {
      const model = await response.json();
      const modelEl = $("#model");
      if (modelEl) {
        modelEl.textContent = `Model: ${model.model_name} · test ROC-AUC ${model.test_roc_auc.toFixed(2)} · sensitivity ${(model.test_recall_sensitivity * 100).toFixed(0)}% · specificity ${(model.test_specificity * 100).toFixed(0)}%`;
      }
    }
  } catch (error) {
    console.warn("Could not load model info:", error);
  }
}

async function handlePredict(event) {
  event.preventDefault();

  const body = {};
  for (const f of spec) {
    const input = document.querySelector(`[name=${f.name}]`);
    if (input) {
      body[f.name] = Number(input.value);
    }
  }

  const out = $("#out");
  if (!out) return;

  out.innerHTML = '<p class="small">Predicting…</p>';

  try {
    const response = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    const data = await response.json();

    if (!response.ok) {
      const detail = Array.isArray(data.detail)
        ? data.detail.map((x) => `${x.loc.slice(-1)}: ${x.msg}`).join("<br>")
        : esc(data.detail);
      out.innerHTML = `<p class="err"><b>Invalid input</b><br>${detail}</p>`;
      return;
    }

    renderResult(data, out);
  } catch (error) {
    console.error("Prediction error:", error);
    out.innerHTML = `<p class="err"><b>Error</b><br>Failed to get prediction. Please try again.</p>`;
  }
}

function renderResult(data, container) {
  const color = { low: "var(--low)", moderate: "var(--mod)", high: "var(--high)" }[data.risk_band];
  const pct = Math.round(data.disease_probability * 100);
  const maxEffect = Math.max(0.01, ...data.contributions.map((c) => Math.abs(c.effect)));

  const riskIcon = {
    high: "🚨",
    moderate: "⚠️",
    low: "✅",
  }[data.risk_band];

  const contributionsHtml = data.contributions
    .map((c) => {
      const width = (Math.abs(c.effect) / maxEffect) * 50;
      const style =
        c.effect >= 0
          ? `left:50%;width:${width}%;background:var(--high)`
          : `left:${50 - width}%;width:${width}%;background:var(--low)`;
      return `<div class="bar"><span class="n">${esc(c.label)}</span><span class="t"><i style="${style}"></i></span><span class="pct">${c.effect > 0 ? "+" : ""}${(c.effect * 100).toFixed(0)}%</span></div>`;
    })
    .join("");

  const warningsHtml = data.warnings.map((w) => `<p class="warn">⚠️ ${esc(w)}</p>`).join("");

  container.innerHTML = `
    <div class="big" style="color:${color}">${pct}%</div>
    <span class="band" style="background:${color}">${riskIcon} ${data.risk_band} risk</span>
    <div class="meter"><div style="width:${pct}%;background:${color}"></div></div>
    <div class="msg-box">🩺 ${esc(data.message)}</div>
    ${warningsHtml}
    <hr class="divider">
    <h3 style="font-size:13px;margin:0 0 2px;text-transform:uppercase;letter-spacing:0.6px;color:var(--mute);font-weight:700;">🧠 What drove this prediction</h3>
    <div class="small" style="margin-bottom:10px;">📊 Change in risk vs. a typical patient value (right = raises risk)</div>
    ${contributionsHtml}
  `;
}

function showError(message) {
  const out = $("#out");
  if (out) {
    out.innerHTML = `<p class="err"><b>Error</b><br>${esc(message)}</p>`;
  }
}

// Initialize on DOM ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}

// Export for testing
window.CardioScreen = {
  init,
  fill,
  renderResult,
  esc,
};