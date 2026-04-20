const refreshBtn = document.getElementById("refreshBtn");
const autoRefresh = document.getElementById("autoRefresh");
const APP_BASE_PATH = window.__APP_BASE_PATH__ || "";

function withAppBasePath(path) {
  if (/^(?:[a-z]+:)?\/\//i.test(path)) {
    return path;
  }
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return APP_BASE_PATH ? `${APP_BASE_PATH}${normalizedPath}` : normalizedPath;
}

function toText(value, fallback = "-") {
  if (value === null || value === undefined || value === "") return fallback;
  return String(value);
}

function escapeHtml(value) {
  return toText(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function fmtBool(v) {
  return v ? "sí" : "no";
}

function fmtBytes(bytes) {
  const n = Number(bytes || 0);
  if (!n) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  let i = 0;
  let value = n;
  while (value >= 1024 && i < units.length - 1) {
    value /= 1024;
    i += 1;
  }
  return `${value.toFixed(i === 0 ? 0 : 1)} ${units[i]}`;
}

async function fetchJson(url) {
  const res = await fetch(withAppBasePath(url), { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`${url} -> HTTP ${res.status}`);
  }
  return res.json();
}

function renderWarnings(warnings) {
  const panel = document.getElementById("warningsPanel");
  const list = document.getElementById("warningsList");
  if (!warnings || warnings.length === 0) {
    panel.hidden = true;
    list.innerHTML = "";
    return;
  }
  panel.hidden = false;
  list.innerHTML = warnings.map((w) => `<li>${escapeHtml(w)}</li>`).join("");
}

function renderSummary(summary) {
  const counts = summary?.counts || {};
  const tasks = counts.tasks || {};
  const appointments = counts.appointments || {};
  const reminders = counts.reminders || {};

  document.getElementById("nowValue").textContent = toText(summary?.now);
  document.getElementById("modeValue").textContent = toText(summary?.mode?.primary_mode);

  document.getElementById("tasksTotal").textContent = toText(tasks.total, "0");
  document.getElementById("tasksDetails").textContent = `overdue: ${toText(tasks.overdue, "0")} · 24h: ${toText(tasks.due_next_24h, "0")}`;

  document.getElementById("appointmentsTotal").textContent = toText(appointments.total, "0");
  document.getElementById("appointmentsDetails").textContent = `1h: ${toText(appointments.upcoming_1h, "0")} · 24h: ${toText(appointments.upcoming_24h, "0")}`;

  document.getElementById("remindersTotal").textContent = toText(reminders.total, "0");
  document.getElementById("remindersDetails").textContent = `vencidos/ahora: ${toText(reminders.due_now_or_past, "0")}`;

  document.getElementById("queueTotal").textContent = toText(counts.hindsight_queue_pending, "0");

  renderWarnings(summary?.warnings || []);
}

function renderFiles(files) {
  const tbody = document.getElementById("filesTableBody");
  const rows = [
    ["state.json", files?.state],
    ["config.yaml", files?.config],
    ["hindsight_queue.jsonl", files?.hindsight_queue],
    ["logs_dir", files?.logs_dir],
    ["legacy tasks.json", files?.legacy_tasks],
  ];

  tbody.innerHTML = rows
    .map(([name, info]) => {
      const exists = info?.exists ?? false;
      return `
        <tr>
          <td>${escapeHtml(name)}</td>
          <td>${escapeHtml(fmtBool(exists))}</td>
          <td>${escapeHtml(fmtBytes(info?.size_bytes || 0))}</td>
          <td>${escapeHtml(toText(info?.modified_at))}</td>
        </tr>
      `;
    })
    .join("");
}

function renderPolicies(catalog) {
  const tbody = document.getElementById("policiesTableBody");
  const activeIds = new Set(catalog?.active_policy_ids || []);
  const allPolicies = catalog?.all_policies || [];
  const activePolicies = allPolicies.filter((p) => activeIds.has(p.id));

  tbody.innerHTML = activePolicies
    .map(
      (p) => `
      <tr>
        <td>${escapeHtml(p.id)}</td>
        <td>${escapeHtml(toText(p.priority))}</td>
        <td>${escapeHtml(toText(p.urgency))}</td>
        <td>${escapeHtml(toText(p.trigger))}</td>
      </tr>
    `,
    )
    .join("");
}

function renderLogs(logsPayload) {
  const tbody = document.getElementById("logsTableBody");
  const entries = logsPayload?.entries || [];

  tbody.innerHTML = entries
    .slice(0, 30)
    .map(
      (e) => `
      <tr>
        <td>${escapeHtml(toText(e.at || e._source_file))}</td>
        <td>${escapeHtml(toText(e.status))}</td>
        <td>${escapeHtml(toText(e.reason || e.error || ""))}</td>
        <td>${escapeHtml(toText(e.sent))}</td>
      </tr>
    `,
    )
    .join("");
}

function renderQueue(queuePayload) {
  const tbody = document.getElementById("queueTableBody");
  const entries = queuePayload?.entries || [];

  tbody.innerHTML = entries
    .slice(0, 30)
    .map((e) => {
      const preview = JSON.stringify(e).slice(0, 120);
      return `
        <tr>
          <td>${escapeHtml(toText(e._line))}</td>
          <td>${escapeHtml(toText(e.context))}</td>
          <td>${escapeHtml(preview)}</td>
        </tr>
      `;
    })
    .join("");
}

async function refreshDashboard() {
  try {
    const [summary, files, catalog, logs, queue] = await Promise.all([
      fetchJson("/api/summary"),
      fetchJson("/api/files"),
      fetchJson("/api/catalog"),
      fetchJson("/api/logs?limit=40"),
      fetchJson("/api/hindsight-queue?limit=40"),
    ]);

    renderSummary(summary);
    renderFiles(files);
    renderPolicies(catalog);
    renderLogs(logs);
    renderQueue(queue);
  } catch (error) {
    console.error(error);
    renderWarnings([`Error actualizando dashboard: ${error.message}`]);
  }
}

let intervalId = null;
function setupAutoRefresh() {
  if (intervalId) {
    clearInterval(intervalId);
    intervalId = null;
  }
  if (autoRefresh.checked) {
    intervalId = setInterval(refreshDashboard, 15000);
  }
}

refreshBtn.addEventListener("click", refreshDashboard);
autoRefresh.addEventListener("change", setupAutoRefresh);

refreshDashboard();
setupAutoRefresh();
