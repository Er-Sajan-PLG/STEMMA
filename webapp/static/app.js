"use strict";

const state = { selectedDoc: null, candidates: {} };

async function api(path, options = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const text = await res.text();
  let data = null;
  try { data = text ? JSON.parse(text) : null; } catch (_) { data = null; }
  if (!res.ok) throw new Error((data && data.error) || `HTTP ${res.status}`);
  return data;
}

function el(tag, attrs = {}, text = "") {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "onclick") node.onclick = v;
    else node.setAttribute(k, v);
  }
  node.textContent = text;
  return node;
}

function clear(node) { node.replaceChildren(); }

function jsonPre(obj) {
  return el("pre", { class: "jsonpre" }, JSON.stringify(obj, null, 2));
}

const PROVIDER_DEFAULTS = {
  antigravity: { base_url: "http://127.0.0.1:6012/v1", model: "gemini-3-pro" },
  google: { base_url: "https://generativelanguage.googleapis.com/v1beta", model: "gemini-3-pro-preview" },
  openai: { base_url: "https://api.openai.com/v1", model: "gpt-4o-mini" },
};

function applyProviderDefaults(provider, force) {
  const base = document.getElementById("cfg-base");
  const model = document.getElementById("cfg-model");
  if (force || !base.value) base.value = (PROVIDER_DEFAULTS[provider] || {}).base_url || "";
  if (force || !model.value) model.value = (PROVIDER_DEFAULTS[provider] || {}).model || "";
  const hint = document.getElementById("cfg-hint");
  const hints = {
    antigravity: "Run a harness that is already signed in to your Google AI Pro / Antigravity account (and exposes OpenAI-compatible /v1). Press Sign in to get its login URL, then Load models. In the Arena preview the base URL must be the harness's public/tunneled URL — or run the webapp on the same machine: python3 webapp/server.py --host 0.0.0.0 --port 8080.",
    google: "Google AI Studio/GenAI API keys start with AIza… and use the Gemini generateContent endpoint. It cannot log in to a Google AI Pro account by itself — use the Antigravity / local harness option for subscription models.",
    openai: "OpenAI-compatible endpoint: POST {base_url}/chat/completions with a Bearer key.",
  };
  hint.textContent = hints[provider] || "";
}

async function loadConfig() {
  try {
    const cfg = await api("/api/config");
    const provider = (cfg.provider || "antigravity");
    document.getElementById("cfg-provider").value = provider;
    document.getElementById("cfg-base").value = cfg.base_url || (PROVIDER_DEFAULTS[provider] || {}).base_url || "";
    document.getElementById("cfg-model").value = cfg.model || (PROVIDER_DEFAULTS[provider] || {}).model || "";
    document.getElementById("cfg-key").value = cfg.api_key || "";
    applyProviderDefaults(provider, false);
  } catch (e) { alert(e.message); }
}

async function saveConfig(event) {
  event.preventDefault();
  const status = document.getElementById("cfg-status");
  status.textContent = "saving…";
  status.className = "status";
  try {
    const cfg = await api("/api/config", {
      method: "POST",
      body: JSON.stringify({
        provider: document.getElementById("cfg-provider").value,
        base_url: document.getElementById("cfg-base").value,
        model: document.getElementById("cfg-model").value,
        api_key: document.getElementById("cfg-key").value,
      }),
    });
    document.getElementById("cfg-key").value = cfg.api_key;
    status.textContent = (cfg.configured ? "configured ✓" : "configured (missing key/base_url/model?)");
    status.className = "status ok";
  } catch (e) {
    status.textContent = e.message;
    status.className = "status err";
  }
}

async function signIn() {
  const status = document.getElementById("cfg-status");
  status.textContent = "contacting harness for sign-in…";
  status.className = "status";
  try {
    const res = await api("/api/config/login", {
      method: "POST",
      body: JSON.stringify({
        provider: document.getElementById("cfg-provider").value,
        base_url: document.getElementById("cfg-base").value,
        api_key: document.getElementById("cfg-key").value,
      }),
    });
    if (res.ok && res.url) {
      status.textContent = "Sign-in URL ready — opening it in a new tab. After you sign in, press Load models.";
      status.className = "status ok";
      window.open(res.url, "_blank", "noopener");
    } else {
      status.textContent = res.message || "No sign-in URL returned.";
      status.className = "status err";
    }
  } catch (e) {
    status.textContent = `sign-in failed: ${e.message}`;
    status.className = "status err";
  }
}

async function loadModels() {
  const status = document.getElementById("cfg-status");
  status.textContent = "loading models from harness…";
  status.className = "status";
  try {
    const res = await api("/api/config/models", {
      method: "POST",
      body: JSON.stringify({
        provider: document.getElementById("cfg-provider").value,
        base_url: document.getElementById("cfg-base").value,
        api_key: document.getElementById("cfg-key").value,
      }),
    });
    const datalist = document.getElementById("cfg-model-list");
    clear(datalist);
    (res.models || []).forEach((m) => {
      const opt = document.createElement("option");
      opt.value = m;
      datalist.appendChild(opt);
    });
    status.textContent = `Loaded ${res.count} models from ${res.provider} — pick one above.`;
    status.className = "status ok";
  } catch (e) {
    status.textContent = `load models failed: ${e.message}`;
    status.className = "status err";
  }
}

async function testConfig() {
  const status = document.getElementById("cfg-status");
  status.textContent = "saving then testing provider…";
  status.className = "status";
  try {
    await saveConfig(new Event("submit"));
    const res = await api("/api/config/test", { method: "POST", body: "{}" });
    status.textContent = res.ok ? `provider ok ✓ (${res.model})` : `provider failed: ${res.error}`;
    status.className = res.ok ? "status ok" : "status err";
  } catch (e) {
    status.textContent = `provider failed: ${e.message}`;
    status.className = "status err";
  }
}

async function uploadFile(file) {
  const status = document.getElementById("upload-status");
  status.textContent = `uploading ${file.name}…`;
  status.className = "status";
  const dataBase64 = await new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result).split(",")[1] || "");
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
  try {
    await api("/api/documents", {
      method: "POST",
      body: JSON.stringify({ filename: file.name, mime: file.type || "", data_base64: dataBase64 }),
    });
    status.textContent = `${file.name} uploaded.`;
    status.className = "status ok";
    await refresh();
  } catch (e) {
    status.textContent = `upload failed: ${e.message}`;
    status.className = "status err";
  }
}

function docStatus(doc) {
  const badges = { uploaded: "grey", ready: "blue", generated: "green", staged: "purple", error: "red", unsupported: "orange" };
  return el("span", { class: `badge ${badges[doc.status] || "grey"}` }, doc.status);
}

async function refreshDocs() {
  const container = document.getElementById("docs");
  let docs = [];
  try { docs = (await api("/api/documents")).documents || []; } catch (e) { alert(e.message); }
  clear(container);
  if (!docs.length) { container.appendChild(el("p", { class: "hint" }, "No documents yet.")); return; }
  docs.reverse().forEach((doc) => {
    const row = el("article", { class: "item" });
    row.appendChild(el("div", { class: "item-title" }, doc.original_name));
    const meta = el("div", { class: "item-meta" },
      `${doc.kind || "…"} · ${(doc.size_bytes || 0).toLocaleString()} bytes · ${doc.status}`);
    row.appendChild(meta);
    row.appendChild(docStatus(doc));
    const actions = el("div", { class: "row-actions" });
    const view = el("button", { class: "btn sm" }, "View");
    view.onclick = () => selectDoc(doc.id);
    actions.appendChild(view);
    const ex = el("button", { class: "btn sm" }, "Extract");
    ex.onclick = () => extract(doc.id);
    actions.appendChild(ex);
    const gen = el("button", { class: "btn sm primary" }, "Draft");
    gen.onclick = () => generate(doc.id);
    actions.appendChild(gen);
    row.appendChild(actions);
    container.appendChild(row);
  });
}

async function extract(docId) {
  try {
    await api(`/api/documents/${docId}/extract`, { method: "POST", body: "{}" });
    await refresh();
    await selectDoc(docId);
  } catch (e) { alert(`extract failed: ${e.message}`); }
}

async function generate(docId) {
  if (!confirm("Run the configured LLM Draft to propose candidates? It will not write canonical content.")) return;
  try {
    await api(`/api/documents/${docId}/generate`, {
      method: "POST",
      body: JSON.stringify({ target_kinds: ["entity", "connection"] }),
    });
    await refresh();
    await selectDoc(docId);
  } catch (e) { alert(`draft failed: ${e.message}`); }
}

async function selectDoc(docId) {
  const panel = document.getElementById("document-panel");
  let doc;
  try { doc = await api(`/api/documents/${docId}`); } catch (e) { alert(e.message); return; }
  state.selectedDoc = doc.id;
  panel.classList.remove("hidden");
  document.getElementById("doc-title").textContent = `Document: ${doc.original_name}`;
  const meta = document.getElementById("doc-meta");
  clear(meta);
  const labels = [["Kind", doc.kind || "…"], ["Status", doc.status], ["Size", `${(doc.size_bytes || 0).toLocaleString()} bytes`],
    ["Path", doc.stored_path], ["Uploaded", doc.created_at]];
  labels.forEach(([k, v]) => {
    meta.appendChild(el("div", { class: "meta-key" }, k));
    meta.appendChild(el("div", { class: "meta-val" }, String(v)));
  });
  const text = document.getElementById("doc-text");
  text.textContent = (doc.extraction && doc.extraction.text_path) ? "Loading…" : "No extracted text yet. Run Extract.";
  fetch(`/api/documents/${doc.id}/text`).then(r => r.json()).then(d => {
    text.textContent = d.text || "(no rendered text)";
  }).catch(() => { text.textContent = "unable to load extracted text"; });
  await refreshCandidates(doc.id);
}

async function refreshCandidates(docId) {
  const container = document.getElementById("candidates");
  let data;
  try { data = await api(`/api/candidates?doc_id=${encodeURIComponent(docId)}`); } catch (e) { data = { candidates: [] }; }
  state.candidates = data.candidates || [];
  clear(container);
  if (!state.candidates.length) { container.appendChild(el("p", { class: "hint" }, "No candidates yet. Configure a Draft provider and press Draft.")); return; }
  state.candidates.forEach((candidate) => renderCandidate(container, candidate));
}

function renderCandidate(container, candidate) {
  const tpl = document.getElementById("candidate-template");
  const node = tpl.content.cloneNode(true).querySelector(".candidate");
  node.querySelector("[data-kind]").textContent = candidate.kind;
  node.querySelector("[data-kind]").classList.add("badge", candidate.kind === "connection" ? "purple" : "blue");
  const body = node.querySelector("[data-body]");
  const proposal = candidate.proposal || {};
  body.appendChild(el("div", { class: "candidate-fields" },
    `ID: ${proposal.id || "…"} · Domain: ${proposal.domain || "…"} · Relation: ${proposal.relation || "…"} · ${proposal.name || ""}`));
  const destination = candidate.kind === "entity" ? "content/" : "connections/";
  body.appendChild(el("div", { class: "candidate-fields destination-note" },
    `Destination: ${destination} — NOT written by this app; a human must review and a later canonical gate applies.`));
  if (candidate.findings && candidate.findings.length) {
    body.appendChild(el("div", { class: "findings" },
      candidate.findings.slice(0, 8).join("\n")));
  }
  body.appendChild(jsonPre(proposal));
  const stage = node.querySelector("[data-stage]");
  stage.onclick = () => stageCandidate(candidate);
  const del = node.querySelector("[data-delete]");
  del.onclick = async () => {
    if (!confirm("Delete this candidate? (It is not in canonical.)")) return;
    try { await api(`/api/candidates/${candidate.id}`, { method: "DELETE" }); await refreshCandidates(state.selectedDoc); }
    catch (e) { alert(e.message); }
  };
  const edit = node.querySelector("[data-edit]");
  edit.onclick = () => editCandidate(candidate);
  container.appendChild(node);
}

function editCandidate(candidate) {
  const body = document.getElementById("document-panel");
  const editor = el("textarea", { class: "json-editor" }, JSON.stringify(candidate.proposal, null, 2));
  const wrapper = el("div", { class: "card" });
  wrapper.appendChild(el("h3", {}, `Edit ${candidate.kind} candidate`));
  wrapper.appendChild(editor);
  const save = el("button", { class: "btn primary" }, "Save candidate");
  const cancel = el("button", { class: "btn ghost" }, "Cancel");
  const status = el("span", { class: "status" });
  save.onclick = async () => {
    try {
      const proposal = JSON.parse(editor.value);
      await api(`/api/candidates/${candidate.id}`, {
        method: "PATCH",
        body: JSON.stringify({ proposal }),
      });
      wrapper.remove();
      await refreshCandidates(state.selectedDoc);
    } catch (e) { status.textContent = e.message; status.className = "status err"; }
  };
  cancel.onclick = () => wrapper.remove();
  wrapper.appendChild(el("div", { class: "row-actions" }, ""));
  wrapper.appendChild(save); wrapper.appendChild(cancel); wrapper.appendChild(status);
  body.appendChild(wrapper);
  editor.focus();
}

async function stageCandidate(candidate) {
  const reviewer = prompt("Human reviewer (e.g. human:reviewer.physics-001):");
  if (!reviewer) return;
  const note = prompt("Review note / evidence decision:", "") || "";
  try {
    const result = await api(`/api/candidates/${candidate.id}/stage`, {
      method: "POST",
      body: JSON.stringify({ reviewer, note }),
    });
    alert(`Staged proposal: ${result.path}`);
    await refreshCandidates(state.selectedDoc);
    await refreshProposals();
  } catch (e) { alert(`stage failed: ${e.message}`); }
}

async function refreshProposals() {
  const container = document.getElementById("proposals");
  let data;
  try { data = await api("/api/proposals"); } catch (e) { data = { proposals: [] }; }
  clear(container);
  if (!data.proposals.length) { container.appendChild(el("p", { class: "hint" }, "No staged proposals yet.")); return; }
  data.proposals.reverse().forEach((proposal) => {
    const row = el("article", { class: "item" });
    const rec = proposal.record || {};
    row.appendChild(el("div", { class: "item-title" },
      `${rec.kind || "…"} · ${((rec.candidate || {}).id || "proposal")}`));
    row.appendChild(el("div", { class: "item-meta" },
      `${proposal.path} · reviewed by ${((rec.human_review || {}).reviewer || "…")}`));
    row.appendChild(jsonPre(rec.destination || {}));
    container.appendChild(row);
  });
}

async function refreshAudit() {
  const container = document.getElementById("audit");
  let data;
  try { data = await api("/api/audit"); } catch (e) { data = { events: [] }; }
  clear(container);
  if (!data.events.length) { container.appendChild(el("p", { class: "hint" }, "No audit events yet.")); return; }
  container.appendChild(el("pre", { class: "jsonpre" }, JSON.stringify(data.events.slice(-40), null, 2)));
}

async function refresh() {
  await refreshDocs();
  await refreshProposals();
  await refreshAudit();
  if (state.selectedDoc) await selectDoc(state.selectedDoc);
}

document.addEventListener("DOMContentLoaded", () => {
  const settings = document.getElementById("settings");
  document.getElementById("settings-toggle").onclick = () => settings.classList.toggle("hidden");
  document.getElementById("settings-form").onsubmit = saveConfig;
  document.getElementById("cfg-provider").onchange = (e) => applyProviderDefaults(e.target.value, true);
  document.getElementById("cfg-test").onclick = testConfig;
  document.getElementById("cfg-login").onclick = signIn;
  document.getElementById("cfg-models").onclick = loadModels;
  const input = document.getElementById("file-input");
  const drop = document.getElementById("drop");
  drop.onclick = () => input.click();
  input.onchange = () => { if (input.files.length) uploadFile(input.files[0]); };
  drop.ondragover = (e) => { e.preventDefault(); drop.classList.add("over"); };
  drop.ondragleave = () => drop.classList.remove("over");
  drop.ondrop = (e) => {
    e.preventDefault();
    drop.classList.remove("over");
    if (e.dataTransfer.files.length) uploadFile(e.dataTransfer.files[0]);
  };
  loadConfig();
  refresh();
});
