const templateFields = {
  IRAC: ["issue", "rule", "analysis", "conclusion"],
  FIRAC: ["facts", "issue", "rule", "analysis", "conclusion"],
  CREAC: ["conclusion", "rule", "explanation", "analysis", "conclusionRestated"],
};

const fieldLabels = {
  facts: "Facts",
  issue: "Issue",
  rule: "Rule",
  analysis: "Analysis",
  conclusion: "Conclusion",
  conclusionRestated: "Conclusion Restated",
  explanation: "Explanation",
  holding: "Holding",
  reasoning: "Reasoning",
  notes: "Notes",
};

const sample = {
  caseName: "Example v. Student",
  citation: "123 F.3d 456",
  court: "Sample Court",
  course: "Contracts",
  facts: "A student promised to submit a case brief before class, then changed the format after reviewing the professor's instructions.",
  issue: "Whether the brief should prioritize the assigned course framework over a generic online structure.",
  rule: "A useful law school brief should follow the professor's required analytical framework and preserve the key facts, rule, reasoning, and holding.",
  analysis: "The generic structure helps organize the answer, but the professor's framework controls the final format. The student should keep the template flexible and label sections clearly.",
  conclusion: "Use the course framework first, then adapt the template fields as needed.",
  conclusionRestated: "The brief should be built from the assigned framework rather than copied from a generic form.",
  explanation: "CREAC starts with the conclusion, states the rule, explains authority, applies the rule, and then restates the conclusion.",
  holding: "Template structure is useful only when it supports the assigned legal analysis.",
  reasoning: "A brief is a study tool, so clarity, consistency, and professor-specific expectations matter more than decorative formatting.",
  notes: "Educational writing aid only. Replace this sample with your own reading notes.",
};

let activeTemplate = "FIRAC";
let outputMode = "preview";

const form = document.querySelector("#brief-form");
const tabs = document.querySelectorAll("[data-template]");
const outputTabs = document.querySelectorAll("[data-output]");
const preview = document.querySelector("#brief-preview");
const exportBox = document.querySelector("#export-box");
const copyButton = document.querySelector("#copy-output");
const sampleButton = document.querySelector("#load-sample");
const clearButton = document.querySelector("#clear-form");

function trackEvent(name, params = {}) {
  if (typeof window.gtag === "function") {
    window.gtag("event", name, params);
  }
}

function getValue(name) {
  const field = form?.elements[name];
  return field ? field.value.trim() : "";
}

function setValue(name, value) {
  const field = form?.elements[name];
  if (field) field.value = value;
}

function currentData() {
  return {
    caseName: getValue("caseName") || "Untitled Case Brief",
    citation: getValue("citation"),
    court: getValue("court"),
    course: getValue("course"),
    facts: getValue("facts"),
    issue: getValue("issue"),
    rule: getValue("rule"),
    analysis: getValue("analysis"),
    conclusion: getValue("conclusion"),
    conclusionRestated: getValue("conclusionRestated"),
    explanation: getValue("explanation"),
    holding: getValue("holding"),
    reasoning: getValue("reasoning"),
    notes: getValue("notes"),
  };
}

function sectionsForTemplate(data) {
  const keys = templateFields[activeTemplate];
  const core = keys.map((key) => [fieldLabels[key], data[key]]);
  const extras = [
    ["Holding", data.holding],
    ["Reasoning", data.reasoning],
    ["Notes", data.notes],
  ].filter(([, value]) => value);
  return [...core, ...extras];
}

function markdownOutput(data) {
  const meta = [data.citation, data.court, data.course].filter(Boolean).join(" | ");
  const lines = [`# ${data.caseName}`];
  if (meta) lines.push("", meta);
  lines.push("", `Template: ${activeTemplate}`, "");
  for (const [label, value] of sectionsForTemplate(data)) {
    lines.push(`## ${label}`, value || "_Add notes here._", "");
  }
  lines.push("> Educational writing aid. Not legal advice.");
  return lines.join("\n");
}

function plainOutput(data) {
  return markdownOutput(data)
    .replace(/^# /gm, "")
    .replace(/^## /gm, "")
    .replace(/^> /gm, "");
}

function wordReadyOutput(data) {
  const body = sectionsForTemplate(data)
    .map(([label, value]) => `<h2>${escapeHtml(label)}</h2>\n<p>${escapeHtml(value || "Add notes here.")}</p>`)
    .join("\n");
  return `<h1>${escapeHtml(data.caseName)}</h1>\n<p>${escapeHtml([data.citation, data.court, data.course].filter(Boolean).join(" | "))}</p>\n<p><strong>Template:</strong> ${activeTemplate}</p>\n${body}\n<p><em>Educational writing aid. Not legal advice.</em></p>`;
}

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function renderPreview(data) {
  if (!preview) return;
  const meta = [data.citation, data.court, data.course].filter(Boolean).join(" | ");
  preview.innerHTML = `
    <article class="document-sheet" aria-label="Case brief preview">
      <div class="document-topline">
        <div>
          <h2 class="document-title">${escapeHtml(data.caseName)}</h2>
          <div class="document-meta">${escapeHtml(meta || "Citation | Court | Course")}</div>
        </div>
        <div class="status-pill">${activeTemplate}</div>
      </div>
      <div class="brief-sections">
        ${sectionsForTemplate(data)
          .map(
            ([label, value]) => `
              <section class="brief-section">
                <div class="brief-label">${escapeHtml(label)}</div>
                <div class="brief-content">${escapeHtml(value || "Add notes here.")}</div>
              </section>
            `,
          )
          .join("")}
      </div>
    </article>
  `;
}

function renderOutput() {
  const data = currentData();
  renderPreview(data);
  if (!exportBox) return;
  let text = markdownOutput(data);
  if (outputMode === "plain") text = plainOutput(data);
  if (outputMode === "word") text = wordReadyOutput(data);
  exportBox.textContent = text;
  localStorage.setItem("casebriefkit-draft", JSON.stringify({ activeTemplate, outputMode, data }));
}

function loadDraft() {
  const raw = localStorage.getItem("casebriefkit-draft");
  if (!raw) return;
  try {
    const draft = JSON.parse(raw);
    activeTemplate = draft.activeTemplate || activeTemplate;
    outputMode = draft.outputMode || outputMode;
    Object.entries(draft.data || {}).forEach(([key, value]) => setValue(key, value));
  } catch {
    localStorage.removeItem("casebriefkit-draft");
  }
}

tabs.forEach((button) => {
  button.addEventListener("click", () => {
    activeTemplate = button.dataset.template;
    tabs.forEach((tab) => tab.classList.toggle("active", tab.dataset.template === activeTemplate));
    trackEvent("template_switch", { template: activeTemplate });
    renderOutput();
  });
});

outputTabs.forEach((button) => {
  button.addEventListener("click", () => {
    outputMode = button.dataset.output;
    outputTabs.forEach((tab) => tab.classList.toggle("active", tab.dataset.output === outputMode));
    trackEvent("output_switch", { output_mode: outputMode });
    renderOutput();
  });
});

form?.addEventListener("input", renderOutput);

copyButton?.addEventListener("click", async () => {
  trackEvent("copy_output", { output_mode: outputMode, template: activeTemplate });
  try {
    await navigator.clipboard.writeText(exportBox.textContent);
    copyButton.textContent = "Copied";
  } catch {
    const selection = window.getSelection();
    const range = document.createRange();
    range.selectNodeContents(exportBox);
    selection.removeAllRanges();
    selection.addRange(range);
    copyButton.textContent = "Selected";
  }
  setTimeout(() => {
    copyButton.textContent = "Copy Output";
  }, 1400);
});

sampleButton?.addEventListener("click", () => {
  Object.entries(sample).forEach(([key, value]) => setValue(key, value));
  activeTemplate = "FIRAC";
  tabs.forEach((tab) => tab.classList.toggle("active", tab.dataset.template === activeTemplate));
  trackEvent("load_sample", { template: activeTemplate });
  renderOutput();
});

clearButton?.addEventListener("click", () => {
  form.reset();
  localStorage.removeItem("casebriefkit-draft");
  trackEvent("clear_form", { template: activeTemplate });
  renderOutput();
});

loadDraft();
tabs.forEach((tab) => tab.classList.toggle("active", tab.dataset.template === activeTemplate));
outputTabs.forEach((tab) => tab.classList.toggle("active", tab.dataset.output === outputMode));
renderOutput();
