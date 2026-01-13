function deepCopy(obj) {
  return JSON.parse(JSON.stringify(obj));
}
function setError(msg) {
  const box = document.getElementById("advError");
  if (!box) return;
  if (!msg) {
    box.textContent = "";
    box.style.display = "none";
  } else {
    box.textContent = msg;
    box.style.display = "block";
  }
  const ok = document.getElementById("advOk");
  if (ok) ok.style.display = "none";
}

const advBtn = document.getElementById("toggleAdvanced");
const advBlock = document.getElementById("advancedBlock");
const advOn = document.getElementById("advanced_on");

const tpHidden = document.getElementById("avg_touchpoints_json");
const allocHidden = document.getElementById("allocated_minutes_json");
const popHidden = document.getElementById("population_params_json");

const form = document.getElementById("simForm");

let shown = false;
let cfg = deepCopy(DEFAULT_CFG);

function buildTouchpointsTable() {
  const tbody = document.querySelector("#touchpointsTable tbody");
  tbody.innerHTML = "";
  Object.entries(cfg.avg_touchpoints_by_method).forEach(([method, mean]) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td class="mono">${method}</td>
      <td>
        <input class="form-control form-control-sm"
               type="number" step="0.01" min="0"
               data-tp-method="${method}"
               value="${mean}">
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function buildAllocTable() {
  const tbody = document.querySelector("#allocTable tbody");
  tbody.innerHTML = "";
  Object.entries(cfg.allocated_minutes_by_visit_category).forEach(([cat, minutes]) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td class="mono">${cat}</td>
      <td>
        <input class="form-control form-control-sm"
               type="number" step="1" min="0"
               data-alloc-cat="${cat}"
               value="${minutes}">
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function buildPopulationAccordion() {
  const container = document.getElementById("popAccordion");
  container.innerHTML = "";

  const popNames = Object.keys(cfg.population_params);

  popNames.forEach((pop, idx) => {
    const popId = `pop_${idx}`;
    const methods = cfg.population_params[pop].methods;
    const visits = cfg.population_params[pop].visit_categories;

    const card = document.createElement("div");
    card.className = "accordion mb-2";
    card.innerHTML = `
      <div class="accordion-item">
        <h2 class="accordion-header" id="${popId}_h">
          <button class="accordion-button ${idx === 0 ? "" : "collapsed"}"
                  type="button"
                  data-bs-toggle="collapse"
                  data-bs-target="#${popId}_c"
                  aria-expanded="${idx === 0 ? "true" : "false"}"
                  aria-controls="${popId}_c">
            ${pop}
          </button>
        </h2>
        <div id="${popId}_c" class="accordion-collapse collapse ${idx === 0 ? "show" : ""}"
             aria-labelledby="${popId}_h">
          <div class="accordion-body">
            <h6 class="mb-2">Methods</h6>
            <div class="table-responsive mb-3">
              <table class="table table-sm align-middle">
                <thead>
                  <tr>
                    <th>Method</th>
                    <th>Likelihood</th>
                    <th>p(schedule)</th>
                    <th>p(complete)</th>
                    <th>mu</th>
                    <th>sigma</th>
                    <th>mu2</th>
                    <th>sigma2</th>
                  </tr>
                </thead>
                <tbody id="${popId}_methods"></tbody>
              </table>
            </div>

            <h6 class="mb-2">Visit categories</h6>
            <div class="table-responsive">
              <table class="table table-sm align-middle">
                <thead>
                  <tr>
                    <th>Category</th>
                    <th>Probability</th>
                  </tr>
                </thead>
                <tbody id="${popId}_visits"></tbody>
              </table>
            </div>

            <div class="text-muted mini mt-2">
              Validation: method likelihoods sum to 1, visit-category probabilities sum to 1.
            </div>
          </div>
        </div>
      </div>
    `;
    container.appendChild(card);

    const mBody = document.getElementById(`${popId}_methods`);
    methods.forEach((m, mi) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td class="mono">${m.method}</td>
        <td><input class="form-control form-control-sm" type="number" step="0.001" min="0"
                   data-pop="${pop}" data-kind="method" data-idx="${mi}" data-field="likelihood"
                   value="${m.likelihood}"></td>
        <td><input class="form-control form-control-sm" type="number" step="0.001" min="0" max="1"
                   data-pop="${pop}" data-kind="method" data-idx="${mi}" data-field="p_schedule"
                   value="${m.p_schedule}"></td>
        <td><input class="form-control form-control-sm" type="number" step="0.001" min="0" max="1"
                   data-pop="${pop}" data-kind="method" data-idx="${mi}" data-field="p_complete"
                   value="${m.p_complete}"></td>
        <td><input class="form-control form-control-sm" type="number" step="0.001"
                   data-pop="${pop}" data-kind="method" data-idx="${mi}" data-field="mu"
                   value="${m.mu}"></td>
        <td><input class="form-control form-control-sm" type="number" step="0.001" min="0"
                   data-pop="${pop}" data-kind="method" data-idx="${mi}" data-field="sigma"
                   value="${m.sigma}"></td>
        <td><input class="form-control form-control-sm" type="number" step="0.001"
                   data-pop="${pop}" data-kind="method" data-idx="${mi}" data-field="mu2"
                   value="${m.mu2}"></td>
        <td><input class="form-control form-control-sm" type="number" step="0.001" min="0"
                   data-pop="${pop}" data-kind="method" data-idx="${mi}" data-field="sigma2"
                   value="${m.sigma2}"></td>
      `;
      mBody.appendChild(tr);
    });

    const vBody = document.getElementById(`${popId}_visits`);
    visits.forEach((v, vi) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td class="mono">${v.category}</td>
        <td>
          <input class="form-control form-control-sm" type="number" step="0.001" min="0"
                 data-pop="${pop}" data-kind="visit" data-idx="${vi}" data-field="prob"
                 value="${v.prob}">
        </td>
      `;
      vBody.appendChild(tr);
    });
  });

  if (!document.getElementById("bsjs")) {
    const s = document.createElement("script");
    s.src = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js";
    s.id = "bsjs";
    document.body.appendChild(s);
  }
}

function pullAdvancedInputsIntoCfg() {
  document.querySelectorAll("[data-tp-method]").forEach(inp => {
    const method = inp.getAttribute("data-tp-method");
    const v = Number(inp.value);
    cfg.avg_touchpoints_by_method[method] = isFinite(v) ? v : 0;
  });

  document.querySelectorAll("[data-alloc-cat]").forEach(inp => {
    const cat = inp.getAttribute("data-alloc-cat");
    const v = Number(inp.value);
    cfg.allocated_minutes_by_visit_category[cat] = isFinite(v) ? v : 0;
  });

  document.querySelectorAll("input[data-pop][data-kind][data-idx][data-field]").forEach(inp => {
    const pop = inp.getAttribute("data-pop");
    const kind = inp.getAttribute("data-kind");
    const idx = Number(inp.getAttribute("data-idx"));
    const field = inp.getAttribute("data-field");
    const v = Number(inp.value);

    if (!cfg.population_params[pop]) return;
    if (kind === "method") cfg.population_params[pop].methods[idx][field] = isFinite(v) ? v : 0;
    else cfg.population_params[pop].visit_categories[idx][field] = isFinite(v) ? v : 0;
  });
}

function sum(arr) {
  return arr.reduce((a, b) => a + b, 0);
}

function validateAdvanced() {
  setError("");
  pullAdvancedInputsIntoCfg();

  const popNames = Object.keys(cfg.population_params);

  for (const pop of popNames) {
    const methods = cfg.population_params[pop].methods;
    const visits = cfg.population_params[pop].visit_categories;

    for (const m of methods) {
      if (m.likelihood < 0) return setError(`${pop}: method likelihood cannot be negative.`);
      if (m.p_schedule < 0 || m.p_schedule > 1) return setError(`${pop}: p(schedule) must be between 0 and 1.`);
      if (m.p_complete < 0 || m.p_complete > 1) return setError(`${pop}: p(complete) must be between 0 and 1.`);
      if (m.sigma < 0) return setError(`${pop}: sigma must be ≥ 0.`);
      if (m.sigma2 < 0) return setError(`${pop}: sigma2 must be ≥ 0.`);
    }
    for (const v of visits) {
      if (v.prob < 0) return setError(`${pop}: visit-category probability cannot be negative.`);
    }

    const mSum = sum(methods.map(m => Number(m.likelihood)));
    const vSum = sum(visits.map(v => Number(v.prob)));

    if (Math.abs(mSum - 1.0) > 1e-3) return setError(`${pop}: method likelihoods must sum to 1 (currently ${mSum.toFixed(4)}).`);
    if (Math.abs(vSum - 1.0) > 1e-3) return setError(`${pop}: visit-category probabilities sum to 1 (currently ${vSum.toFixed(4)}).`);
  }

  for (const [k, v] of Object.entries(cfg.avg_touchpoints_by_method)) {
    if (Number(v) < 0) return setError(`Avg touchpoints for "${k}" cannot be negative.`);
  }
  for (const [k, v] of Object.entries(cfg.allocated_minutes_by_visit_category)) {
    if (Number(v) < 0) return setError(`Allocated minutes for "${k}" cannot be negative.`);
  }

  const ok = document.getElementById("advOk");
  if (ok) ok.style.display = "inline";
  return true;
}

function writeHiddenJsonFields() {
  tpHidden.value = JSON.stringify(cfg.avg_touchpoints_by_method);
  allocHidden.value = JSON.stringify(cfg.allocated_minutes_by_visit_category);
  popHidden.value = JSON.stringify(cfg.population_params);
}

function showAdvanced() {
  shown = true;
  advBlock.style.display = "block";
  advBtn.textContent = "Advanced ▲";
  advOn.value = "1";
  setError("");

  buildTouchpointsTable();
  buildAllocTable();
  buildPopulationAccordion();
}

function hideAdvanced() {
  shown = false;
  advBlock.style.display = "none";
  advBtn.textContent = "Advanced ▼";
  advOn.value = "0";
  setError("");
}

advBtn?.addEventListener("click", () => {
  if (shown) hideAdvanced();
  else showAdvanced();
});

document.getElementById("resetTouchpoints")?.addEventListener("click", () => {
  cfg.avg_touchpoints_by_method = deepCopy(DEFAULT_CFG.avg_touchpoints_by_method);
  buildTouchpointsTable();
  setError("");
});
document.getElementById("resetAlloc")?.addEventListener("click", () => {
  cfg.allocated_minutes_by_visit_category = deepCopy(DEFAULT_CFG.allocated_minutes_by_visit_category);
  buildAllocTable();
  setError("");
});
document.getElementById("resetPopParams")?.addEventListener("click", () => {
  cfg.population_params = deepCopy(DEFAULT_CFG.population_params);
  buildPopulationAccordion();
  setError("");
});

document.getElementById("validateAdvanced")?.addEventListener("click", () => {
  validateAdvanced();
});

form?.addEventListener("submit", (e) => {
  if (advOn.value === "1") {
    const ok = validateAdvanced();
    if (!ok) {
      e.preventDefault();
      return;
    }
    writeHiddenJsonFields();
  }
});
