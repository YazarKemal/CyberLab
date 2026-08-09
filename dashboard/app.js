const state = { data: null };

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];

function setText(selector, value) {
  const el = $(selector);
  if (el) el.textContent = value;
}

function escapeHtml(value = "") {
  return String(value).replace(/[&<>'"]/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "'": "&#39;",
    '"': "&quot;",
  })[char]);
}

function formatPhase(phase) {
  return `P${String(phase.number).padStart(2, "0")}`;
}

function renderMetrics(data) {
  const completed = data.labs.filter((lab) => lab.complete).length;
  const total = data.labs.length;
  const verified = data.labs.reduce((sum, lab) => sum + (lab.verified_count || 0), 0);
  const activePhase = data.phases.find((phase) => phase.status === "active") || data.phases.find((phase) => phase.status === "pending") || data.phases.at(-1);

  setText("#metric-completed", completed);
  setText("#metric-total", `of ${total} discovered`);
  setText("#metric-verified", verified);
  setText("#metric-phase", activePhase ? formatPhase(activePhase) : "—");
  setText("#metric-phase-name", activePhase ? activePhase.name : "no phase");
  setText("#metric-git", data.git.dirty ? "DIRTY" : "CLEAN");
  setText("#metric-branch", data.git.branch || "unknown branch");

  const progress = data.phases.length ? Math.round((data.phases.filter((p) => p.status === "done").length / data.phases.length) * 100) : 0;
  setText("#progress-label", `${progress}%`);
}

function renderMission(data) {
  const incomplete = data.labs.find((lab) => !lab.complete);
  const latest = data.labs.at(-1);
  if (incomplete) {
    setText("#mission-title", `${incomplete.id} — ${incomplete.title}`);
    setText("#mission-subtitle", "Sıradaki keşfedilen laboratuvar henüz tamamlanmamış görünüyor.");
  } else if (latest) {
    setText("#mission-title", `${latest.id} tamamlandı`);
    setText("#mission-subtitle", "Repo temiz. Bir sonraki laboratuvar için hazır.");
  } else {
    setText("#mission-title", "CyberLab hazır");
    setText("#mission-subtitle", "Henüz laboratuvar keşfedilmedi.");
  }
}

function renderPhases(data) {
  const container = $("#phase-list");
  container.innerHTML = data.phases.map((phase) => {
    const width = phase.status === "done" ? 100 : phase.status === "active" ? Math.max(18, phase.progress || 35) : 0;
    return `
      <div class="phase-row ${phase.status === "done" ? "done" : ""}">
        <div class="phase-num">${escapeHtml(formatPhase(phase))}</div>
        <div>
          <div class="phase-name">${escapeHtml(phase.name)}</div>
          <div class="bar"><span style="width:${width}%"></span></div>
        </div>
        <div class="phase-state">${escapeHtml(phase.status.toUpperCase())}</div>
      </div>`;
  }).join("");
}

function renderTelemetry(data) {
  const lines = [
    `[server] ${data.server.host}:${data.server.port}`,
    `[repo] ${data.git.branch} @ ${data.git.head_short || "unknown"}`,
    `[tree] ${data.labs.length} lab(s) discovered`,
    `[findings] ${data.labs.reduce((sum, lab) => sum + (lab.verified_count || 0), 0)} VERIFIED marker(s)`,
    `[workspace] ${data.git.dirty ? "uncommitted changes present" : "working tree clean"}`,
    `[mode] localhost educational environment`,
  ];
  const el = $("#telemetry");
  el.innerHTML = lines.map((line) => `<div><span class="prompt">›</span>${escapeHtml(line)}</div>`).join("");
}

function renderLabs(data, query = "") {
  const q = query.trim().toLowerCase();
  const labs = data.labs.filter((lab) => `${lab.id} ${lab.title} ${lab.phase_name}`.toLowerCase().includes(q));
  const container = $("#lab-grid");

  if (!labs.length) {
    container.innerHTML = `<article class="lab-card"><h3>Sonuç yok</h3><p>Arama ölçütüne uyan laboratuvar bulunamadı.</p></article>`;
    return;
  }

  container.innerHTML = labs.map((lab) => `
    <article class="lab-card ${lab.complete ? "done" : ""}">
      <span class="badge ${lab.complete ? "" : "dim"}">${lab.complete ? "COMPLETE" : "IN PROGRESS"}</span>
      <h3>${escapeHtml(lab.id)} — ${escapeHtml(lab.title)}</h3>
      <p>${escapeHtml(lab.summary || "Laboratuvar klasörü keşfedildi.")}</p>
      <div class="lab-meta">
        <span>${escapeHtml(lab.phase_name)}</span>
        <span>${lab.verified_count || 0} VERIFIED</span>
      </div>
    </article>`).join("");
}

function renderActivity(data) {
  const container = $("#activity-list");
  if (!data.git.commits.length) {
    container.innerHTML = `<div class="activity-item"><span class="sha">—</span><span class="activity-msg">Commit bulunamadı</span></div>`;
    return;
  }
  container.innerHTML = data.git.commits.map((commit) => `
    <div class="activity-item">
      <span class="sha">${escapeHtml(commit.sha)}</span>
      <span class="activity-msg">${escapeHtml(commit.message)}</span>
      <span class="activity-time">${escapeHtml(commit.date || "")}</span>
    </div>`).join("");
}

function render(data) {
  state.data = data;
  setText("#server-status", "ONLINE");
  setText("#last-sync", `sync ${new Date().toLocaleTimeString("tr-TR", { hour: "2-digit", minute: "2-digit", second: "2-digit" })}`);
  renderMission(data);
  renderMetrics(data);
  renderPhases(data);
  renderTelemetry(data);
  renderLabs(data, $("#lab-search")?.value || "");
  renderActivity(data);
}

async function refresh() {
  setText("#server-status", "SYNCING");
  try {
    const response = await fetch("/api/status", { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    render(await response.json());
  } catch (error) {
    setText("#server-status", "OFFLINE");
    const telemetry = $("#telemetry");
    if (telemetry) telemetry.innerHTML = `<div><span class="prompt">!</span>${escapeHtml(error.message)}</div><div>Dashboard'u dashboard/serve.py üzerinden çalıştır.</div>`;
  }
}

const roleContent = {
  red: {
    icon: "R",
    kicker: "OFFENSIVE VIEW",
    title: "Red Team",
    copy: "Yetkili laboratuvar hedeflerinde saldırı yüzeyini, protokol davranışını ve kontrollü sömürü zincirini anlamak.",
  },
  victim: {
    icon: "V",
    kicker: "IMPACT VIEW",
    title: "Victim Perspective",
    copy: "Aynı olayın hedef sistemde oluşturduğu belirtileri, servis davranışını, logları ve kullanıcı etkisini gözlemlemek.",
  },
  blue: {
    icon: "B",
    kicker: "DEFENSIVE VIEW",
    title: "Blue Team",
    copy: "Saldırıyı tespit etmek, kanıtları yorumlamak, olayı sınırlandırmak, sistemi sertleştirmek ve tekrarını önlemek.",
  },
};

$$('.nav-item').forEach((button) => {
  button.addEventListener('click', () => {
    $$('.nav-item').forEach((item) => item.classList.remove('active'));
    button.classList.add('active');
    const target = button.dataset.target;
    $$('.view').forEach((view) => view.classList.toggle('active-view', view.id === target));
  });
});

$$('.role-tab').forEach((button) => {
  button.addEventListener('click', () => {
    $$('.role-tab').forEach((item) => item.classList.remove('active'));
    button.classList.add('active');
    const content = roleContent[button.dataset.role];
    $('.role-icon').textContent = content.icon;
    setText('#role-kicker', content.kicker);
    setText('#role-title', content.title);
    setText('#role-copy', content.copy);
  });
});

$('#refresh-btn').addEventListener('click', refresh);
$('#lab-search').addEventListener('input', (event) => {
  if (state.data) renderLabs(state.data, event.target.value);
});

refresh();
