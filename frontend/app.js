const PROFILE_CONFIGS = {
  client: {
    id: "client-101",
    root: "Clients",
    crumb: "Client profile",
    status: "Active client",
    subtitle: "Home care · North District",
    summaryTab: "Profile summary",
    drawerTitle: "Client smart summary",
    noteTitle: "Add a client note",
    documentsTitle: "Client documents",
    nextTitle: "Next visit",
    nextDescription: "Personal care visit",
    teamTitle: "People supporting client",
    healthTitle: "Profile health",
    healthCopy: "Live data is loaded from backend sections.",
  },
  caregiver: {
    id: "caregiver-101",
    root: "Caregivers",
    crumb: "Caregiver profile",
    status: "Active caregiver",
    subtitle: "Home Health Aide · North District",
    summaryTab: "Caregiver summary",
    drawerTitle: "Caregiver smart summary",
    noteTitle: "Add a caregiver note",
    documentsTitle: "Caregiver documents",
    nextTitle: "Next assignment",
    nextDescription: "Client visit",
    teamTitle: "Caregiver activity",
    healthTitle: "Compliance status",
    healthCopy: "Training, ratings, and compatibility are loaded from backend sections.",
  },
  facility: {
    id: "facility-101",
    root: "Facilities",
    crumb: "Facility profile",
    status: "Active facility",
    subtitle: "Assisted Living",
    summaryTab: "Facility summary",
    drawerTitle: "Facility smart summary",
    noteTitle: "Add a facility note",
    documentsTitle: "Facility documents",
    nextTitle: "Next scheduled activity",
    nextDescription: "Operations activity",
    teamTitle: "Facility contacts",
    healthTitle: "Operational status",
    healthCopy: "Facility sections are loaded from backend profile data.",
  },
};

const state = { sections: {}, forms: [], notes: [], activeTab: "summary", profileType: "client" };
const content = document.querySelector("#tab-content");
const drawer = document.querySelector("#overview-drawer");
const scrim = document.querySelector("#scrim");
const toast = document.querySelector("#toast");

const icons = {
  profile: '<svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></svg>',
  care_plan: '<svg viewBox="0 0 24 24"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>',
  medications: '<svg viewBox="0 0 24 24"><path d="m10.5 20.5 10-10a4.24 4.24 0 0 0-6-6l-10 10a4.24 4.24 0 0 0 6 6Z"/><path d="m8.5 10.5 5 5"/></svg>',
  schedule: '<svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 11h18"/></svg>',
  schedule_visit_activity: '<svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 11h18"/></svg>',
  goals: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/></svg>',
  compliance: '<svg viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/><path d="m9 12 2 2 4-5"/></svg>',
  skills_restrictions: '<svg viewBox="0 0 24 24"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7H14a3.5 3.5 0 0 1 0 7H6"/></svg>',
  client_ratings: '<svg viewBox="0 0 24 24"><path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2-5.6-3-5.6 3 1.1-6.2L3 9.6l6.2-.9L12 3Z"/></svg>',
  default: '<svg viewBox="0 0 24 24"><path d="M4 4h16v16H4z"/><path d="M8 9h8M8 13h8M8 17h5"/></svg>',
};

function titleize(value) {
  return String(value).replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatValue(value) {
  if (Array.isArray(value)) {
    return value.map((item) => typeof item === "object" ? Object.values(item).join(" · ") : titleize(item)).join(", ");
  }
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (typeof value === "number") return value.toLocaleString();
  if (value === null || value === undefined || value === "") return "—";
  if (/^\d{4}-\d{2}-\d{2}/.test(value)) {
    return new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric", year: "numeric" }).format(new Date(value));
  }
  return titleize(String(value));
}

function initials(name) {
  return String(name || "NA").split(" ").map((part) => part[0]).slice(0, 2).join("").toUpperCase();
}

function showError(target, message) {
  target.innerHTML = `<div class="empty-state"><div><strong>Backend summary unavailable</strong><p>${message}</p></div></div>`;
}

function sectionCard(name, data, open = true) {
  const excluded = ["id", "profile_id"];
  const details = Object.entries(data).filter(([key]) => !excluded.includes(key));
  const plainDetails = details.filter(([key]) => !["tasks", "active_goals", "medications", "skills", "certifications", "restrictions"].includes(key));
  const list = data.tasks || data.active_goals || data.medications || data.skills || data.certifications || data.restrictions;
  return `
    <article class="card ${open ? "" : "collapsed"}">
      <header class="card-header">
        <div class="card-title"><span class="card-icon">${icons[name] || icons.default}</span><h2>${titleize(name)}</h2></div>
        <button class="card-toggle" aria-label="Toggle ${titleize(name)}">⌄</button>
      </header>
      <div class="card-body">
        ${plainDetails.length ? `<div class="detail-grid">${plainDetails.map(([key, value]) => `
          <div class="detail"><label>${titleize(key)}</label><strong class="${["status", "overall_status", "level_of_care", "next_visit"].includes(key) ? "accent" : ""}">${formatValue(value)}</strong></div>
        `).join("")}</div>` : ""}
        ${list ? `<div class="task-list">${list.map((item) => {
          const text = typeof item === "object" ? (item.goal || item.name || Object.values(item)[0]) : item;
          const meta = typeof item === "object" ? (item.progress || item.schedule || "") : "";
          return `<div class="task-row"><span class="check">✓</span><p><strong>${titleize(text)}</strong>${meta ? `<small>${titleize(meta)}</small>` : ""}</p><span class="tag">Current</span></div>`;
        }).join("")}</div>` : ""}
      </div>
    </article>`;
}

function renderSummary() {
  const order = [
    "profile",
    "health_updates",
    "updates",
    "schedule",
    "schedule_visit_activity",
    "care_plan",
    "medications",
    "goals",
    "client_ratings",
    "compliance",
    "skills_restrictions",
    "compatibility",
    "authorizations",
    "invoices",
    "forms",
    "documents",
  ];
  const cards = order.filter((name) => state.sections[name]).map((name, index) => sectionCard(name, state.sections[name], index < 4)).join("");
  content.innerHTML = (state.profileType === "caregiver" ? caregiverActivityPanel() : "") + (cards || `<div class="empty-state"><div><strong>No profile sections yet</strong><p>No backend sections returned for this profile.</p></div></div>`);
  bindCardToggles();
}

function caregiverActivityPanel() {
  const schedule = state.sections.schedule_visit_activity || {};
  const ratings = state.sections.client_ratings || {};
  const compliance = state.sections.compliance || {};
  return `
    <article class="card smart-ticket-card">
      <header class="card-header">
        <div class="card-title"><span class="card-icon">${icons.schedule_visit_activity}</span><h2>Caregiver activity</h2></div>
        <button class="button button-primary" onclick="openDrawer()">AI Smart Summary</button>
      </header>
      <div class="card-body">
        <div class="assessment-table">
          <div class="assessment-row assessment-head"><span>ID</span><span>Name</span><span>Scheduled</span><span>Completed</span><span>Rating</span><span>Status</span></div>
          <div class="assessment-row"><a>${PROFILE_CONFIGS.caregiver.id}</a><strong>Visit activity</strong><span>${formatValue(schedule.next_visit)}</span><span>${formatValue(schedule.completed_visits_this_month)}</span><span>${formatValue(ratings.average_rating)}</span><span class="tag">${formatValue(compliance.overall_status)}</span></div>
        </div>
      </div>
    </article>`;
}

function renderNotes() {
  content.innerHTML = `
    <article class="card smart-ticket-card">
      <header class="card-header">
        <div class="card-title"><span class="card-icon">${icons.default}</span><h2>Notes summary</h2></div>
        <button class="button button-primary" onclick="generateNotesSummary()">Generate notes summary</button>
      </header>
      <div class="card-body">
        <div class="summary-preview" id="notes-summary-preview">
          <span class="section-kicker">AI NOTES SUMMARY</span>
          <p>This calls <strong>POST /summaries/notes</strong>. Summary text comes only from backend Groq output.</p>
        </div>
        <div class="note-list">${state.notes.length ? state.notes.map((note) => `
          <div class="list-row">
            <span class="avatar avatar-small">${String(note.note_type || "N").slice(0, 2).toUpperCase()}</span>
            <p><strong style="white-space: pre-wrap; font-weight: 500; line-height: 1.5; margin-bottom: 8px;">${note.content || "No note content returned"}</strong><small>${titleize(note.note_type || "note")} · ${formatValue(note.created_at)} · ${note.published ? "Published" : "Unpublished"}</small></p>
            <span class="tag ${note.published ? "" : "amber"}">${note.published ? "Published" : "Draft"}</span>
          </div>
        `).join("") : `<div class="empty-state"><div><strong>No backend notes available</strong><p>No note records returned by backend dummy data.</p></div></div>`}</div>
      </div>
    </article>`;
}

function renderDocuments() {
  const config = PROFILE_CONFIGS[state.profileType];
  const documents = state.sections.documents || {};
  content.innerHTML = `<article class="card"><header class="card-header"><div class="card-title"><span class="card-icon">${icons.default}</span><h2>${config.documentsTitle}</h2></div></header><div class="card-body">${sectionCard("documents", documents, true)}</div></article>`;
}

function renderForms() {
  content.innerHTML = `
    <article class="card smart-ticket-card">
      <header class="card-header">
        <div class="card-title"><span class="card-icon">${icons.default}</span><h2>Forms & assessments</h2></div>
        <button class="button button-primary" onclick="generateFormsSummary()">Generate chart summary</button>
      </header>
      <div class="card-body">
        <div class="summary-preview" id="forms-summary-preview">
          <span class="section-kicker">AI FORM SUMMARY</span>
          <p>Chart and individual summaries call backend Groq endpoints only.</p>
        </div>
        <div class="form-list">${state.forms.length ? state.forms.map((form) => `
          <div class="list-row form-row">
            <span class="check">${form.status === "in_progress" ? "·" : "✓"}</span>
            <p><strong>${form.form_name}</strong><small>${form.form_category} · ${formatValue(form.completed_date)} · ${form.is_fixed ? "Fixed form" : "Custom form"}</small></p>
            <span class="tag ${form.is_fixed ? "" : "amber"}">${form.is_fixed ? "Fixed" : "Custom"}</span>
            <button class="button button-compact" onclick="generateSingleFormSummary('${form.id}')">AI Summary</button>
          </div>
        `).join("") : `<div class="empty-state"><div><strong>No backend forms available</strong><p>This owner type has no individual form records returned by backend.</p></div></div>`}</div>
      </div>
    </article>`;
}

function renderActiveTab() {
  ({ summary: renderSummary, notes: renderNotes, documents: renderDocuments, forms: renderForms })[state.activeTab]();
}

function bindCardToggles() {
  document.querySelectorAll(".card-toggle").forEach((button) => button.addEventListener("click", () => button.closest(".card").classList.toggle("collapsed")));
}

function renderProfileShell() {
  const config = PROFILE_CONFIGS[state.profileType];
  const profile = state.sections.profile || {};
  const schedule = state.sections.schedule || state.sections.schedule_visit_activity || {};
  const displayName = profile.name || config.id;

  document.querySelector("#breadcrumb-root").textContent = config.root;
  document.querySelector("#breadcrumb-current").textContent = config.crumb;
  document.querySelector("#profile-avatar").textContent = initials(displayName);
  document.querySelector("#profile-status").innerHTML = `<i></i>${config.status}`;
  document.querySelector("#profile-id-label").textContent = `ID · ${config.id}`;
  document.querySelector("#profile-name").textContent = displayName;
  document.querySelector("#profile-subtitle").textContent = config.subtitle;
  document.querySelector("#summary-tab").textContent = config.summaryTab;
  document.querySelector("#drawer-title").textContent = config.drawerTitle;
  document.querySelector(".modal-heading h2").textContent = config.noteTitle;
  document.querySelector("#next-card-title").textContent = config.nextTitle;
  document.querySelector("#next-description").textContent = config.nextDescription;
  document.querySelector("#next-meta").innerHTML = `<span class="avatar avatar-tiny">AI</span> Backend data`;
  document.querySelector("#team-title").textContent = config.teamTitle;
  document.querySelector("#team-list").innerHTML = Object.entries(profile).slice(0, 3).map(([key, value]) => `<div><span class="avatar avatar-small">${key.slice(0, 2).toUpperCase()}</span><p><strong>${titleize(key)}</strong><small>${formatValue(value)}</small></p><button>•••</button></div>`).join("");
  document.querySelector("#health-title").textContent = config.healthTitle;
  document.querySelector("#health-copy").textContent = config.healthCopy;

  const nextVisit = schedule.next_visit ? new Date(schedule.next_visit) : new Date();
  document.querySelector("#next-day").textContent = new Intl.DateTimeFormat("en-US", { day: "2-digit" }).format(nextVisit);
  document.querySelector("#next-month").textContent = new Intl.DateTimeFormat("en-US", { month: "short" }).format(nextVisit).toUpperCase();
  document.querySelector("#next-time").textContent = schedule.next_visit ? new Intl.DateTimeFormat("en-US", { weekday: "short", hour: "numeric", minute: "2-digit" }).format(nextVisit) : "No date returned";
}

async function fetchForms() {
  state.forms = [];
  if (!["client", "caregiver"].includes(state.profileType)) return;
  const config = PROFILE_CONFIGS[state.profileType];
  const response = await fetch("/summaries/forms/list", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      owner_type: state.profileType,
      owner_id: config.id,
      requesting_user_id: "user-1",
    }),
  });
  if (response.ok) {
    const payload = await response.json();
    state.forms = payload.forms || [];
  }
}

async function fetchNotes() {
  state.notes = [];
  if (state.profileType !== "client") return;
  const response = await fetch("/summaries/notes/list", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      client_id: PROFILE_CONFIGS.client.id,
      requesting_user_id: "user-1",
      time_filter: "last_90",
      include_care_notes: true,
      include_care_published: true,
      include_care_unpublished: true,
      include_family_notes: true,
      include_family_published: true,
      include_family_unpublished: true,
      include_office_notes: false,
    }),
  });
  if (response.ok) {
    const payload = await response.json();
    state.notes = payload.notes || [];
  }
}

async function loadProfile() {
  const config = PROFILE_CONFIGS[state.profileType];
  content.innerHTML = `<div class="loading-card"><span class="spinner"></span><p>Loading ${state.profileType} details...</p></div>`;
  try {
    const response = await fetch("/summaries/profile/data", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        profile_type: state.profileType,
        profile_id: config.id,
        requesting_user_id: "user-1",
      }),
    });
    if (!response.ok) throw new Error(await response.text());
    const payload = await response.json();
    state.sections = Object.fromEntries(payload.sections.map((section) => [section.section_name, section.data]));
    await fetchForms();
    await fetchNotes();
    renderProfileShell();
    renderActiveTab();
  } catch (error) {
    content.innerHTML = `<div class="empty-state"><div><strong>Profile unavailable</strong><p>${error.message}</p></div></div>`;
  }
}

function renderSummaryObject(summaryText) {
  return Object.entries(summaryText).map(([heading, text]) => `<section class="summary-section"><h3>${heading}</h3><p>${text}</p></section>`).join("");
}

async function openDrawer() {
  const config = PROFILE_CONFIGS[state.profileType];
  document.querySelector("#drawer-title").textContent = config.drawerTitle;
  drawer.classList.add("open");
  scrim.classList.add("show");
  drawer.setAttribute("aria-hidden", "false");
  document.body.style.overflow = "hidden";
  document.querySelector("#drawer-body").innerHTML = '<div class="drawer-loading"><span class="spinner"></span><p>Generating with Groq...</p></div>';
  document.querySelector("#generated-time").textContent = "Generating summary...";
  document.querySelector("#source-list").textContent = "Backend profile sections";

  try {
    const response = await fetch("/summaries/profile", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        profile_type: state.profileType,
        profile_id: config.id,
        requesting_user_id: "user-1",
      }),
    });
    if (!response.ok) throw new Error(await response.text());
    const payload = await response.json();
    document.querySelector("#generated-time").textContent = `Generated ${new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric", year: "numeric", hour: "numeric", minute: "2-digit" }).format(new Date(payload.generated_at))}`;
    document.querySelector("#source-list").textContent = payload.sources.map(titleize).join(" · ");
    document.querySelector("#drawer-body").innerHTML = renderSummaryObject(payload.summary_text);
  } catch (error) {
    document.querySelector("#drawer-body").innerHTML = `<div class="empty-state"><div><strong>Groq summary failed</strong><p>${error.message}</p></div></div>`;
  }
}

async function generateNotesSummary() {
  const preview = document.querySelector("#notes-summary-preview");
  if (!preview) return;
  if (state.profileType !== "client") {
    showError(preview, "Notes summary endpoint currently accepts client_id only.");
    return;
  }
  preview.innerHTML = '<span class="spinner"></span><p>Generating notes summary with Groq...</p>';
  try {
    const response = await fetch("/summaries/notes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        client_id: PROFILE_CONFIGS.client.id,
        requesting_user_id: "user-1",
        time_filter: "last_90",
        include_care_notes: true,
        include_care_published: true,
        include_care_unpublished: true,
        include_family_notes: true,
        include_family_published: true,
        include_family_unpublished: true,
        include_office_notes: false,
      }),
    });
    if (!response.ok) throw new Error(await response.text());
    const payload = await response.json();
    preview.innerHTML = `
      <span class="section-kicker">AI NOTES SUMMARY</span>
      <p class="context-line">${payload.context_line}</p>
      ${Object.entries(payload.sections).map(([heading, text]) => `<div class="mini-summary-block"><strong>${heading}</strong><p>${text}</p></div>`).join("")}`;
  } catch (error) {
    showError(preview, error.message);
  }
}

async function generateFormsSummary() {
  const preview = document.querySelector("#forms-summary-preview");
  if (!preview) return;
  if (!["client", "caregiver"].includes(state.profileType)) {
    showError(preview, "Chart form summary endpoint supports client/caregiver/applicant/prospective_client owners, not facility.");
    return;
  }
  preview.innerHTML = '<span class="spinner"></span><p>Generating chart summary with Groq...</p>';
  try {
    const config = PROFILE_CONFIGS[state.profileType];
    const response = await fetch("/summaries/forms/chart", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        owner_type: state.profileType,
        owner_id: config.id,
        requesting_user_id: "user-1",
      }),
    });
    if (!response.ok) throw new Error(await response.text());
    const payload = await response.json();
    preview.innerHTML = `
      <span class="section-kicker">AI FORM SUMMARY</span>
      <div class="metric-row">
        <div class="metric"><strong>${payload.total_forms}</strong><span>Total</span></div>
        <div class="metric"><strong>${payload.completed_forms}</strong><span>Completed</span></div>
        <div class="metric"><strong>${payload.in_progress_forms}</strong><span>In progress</span></div>
      </div>
      <div class="mini-summary-block"><strong>Executive synthesis</strong><p>${payload.executive_synthesis}</p></div>
      ${payload.group_summaries.map((group) => `<div class="mini-summary-block"><strong>${group.form_category}</strong><p>${group.summary_text}</p></div>`).join("")}`;
  } catch (error) {
    showError(preview, error.message);
  }
}

async function generateSingleFormSummary(formId) {
  const form = state.forms.find((item) => item.id === formId);
  if (!form) return;
  document.querySelector("#drawer-title").textContent = `${form.form_name} summary`;
  drawer.classList.add("open");
  scrim.classList.add("show");
  drawer.setAttribute("aria-hidden", "false");
  document.body.style.overflow = "hidden";
  document.querySelector("#generated-time").textContent = "Generating summary...";
  document.querySelector("#source-list").textContent = `${form.form_category} · ${form.is_fixed ? "Fixed form" : "Custom form"} · ${form.id}`;
  document.querySelector("#drawer-body").innerHTML = '<div class="drawer-loading"><span class="spinner"></span><p>Generating single form summary with Groq...</p></div>';

  try {
    const response = await fetch(`/summaries/forms/${formId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ requesting_user_id: "user-1" }),
    });
    if (!response.ok) throw new Error(await response.text());
    const payload = await response.json();
    document.querySelector("#generated-time").textContent = `Generated ${new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric", year: "numeric", hour: "numeric", minute: "2-digit" }).format(new Date(payload.generated_at))}`;
    document.querySelector("#drawer-body").innerHTML = `
      <section class="summary-section form-summary-intro">
        <h3>${payload.is_fixed ? "Fixed form summary" : "Custom form summary"}</h3>
        <p>${payload.is_fixed ? "Backend used the fixed-form Groq prompt with Jira-defined sections." : "Backend used the custom-form Groq prompt."}</p>
      </section>
      ${renderSummaryObject(payload.summary_text)}`;
  } catch (error) {
    document.querySelector("#drawer-body").innerHTML = `<div class="empty-state"><div><strong>Groq form summary failed</strong><p>${error.message}</p></div></div>`;
  }
}

function closeDrawer() {
  drawer.classList.remove("open");
  scrim.classList.remove("show");
  drawer.setAttribute("aria-hidden", "true");
  document.body.style.overflow = "";
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 1900);
}

function openNoteModal() {
  document.querySelector("#note-modal").classList.add("show");
  setTimeout(() => document.querySelector("#note-content").focus(), 100);
}

function closeNoteModal() {
  document.querySelector("#note-modal").classList.remove("show");
}

document.querySelectorAll(".tabs button").forEach((button) => button.addEventListener("click", () => {
  document.querySelector(".tabs button.active").classList.remove("active");
  button.classList.add("active");
  state.activeTab = button.dataset.tab;
  renderActiveTab();
}));

document.querySelectorAll(".profile-switcher button").forEach((button) => button.addEventListener("click", () => {
  document.querySelector(".profile-switcher button.active").classList.remove("active");
  button.classList.add("active");
  state.profileType = button.dataset.profileType;
  state.activeTab = "summary";
  document.querySelector(".tabs button.active").classList.remove("active");
  document.querySelector('[data-tab="summary"]').classList.add("active");
  loadProfile();
}));

document.querySelector("#generate-button").addEventListener("click", openDrawer);
document.querySelector("#close-drawer").addEventListener("click", closeDrawer);
scrim.addEventListener("click", closeDrawer);
document.addEventListener("keydown", (event) => { if (event.key === "Escape") { closeDrawer(); closeNoteModal(); } });
document.querySelector("#copy-button").addEventListener("click", async () => {
  await navigator.clipboard.writeText(document.querySelector("#drawer-body").innerText);
  showToast("Copied to clipboard");
});
document.querySelector("#add-note-button").addEventListener("click", openNoteModal);
document.querySelector("#close-note").addEventListener("click", closeNoteModal);
document.querySelector("#cancel-note").addEventListener("click", closeNoteModal);
document.querySelector("#note-modal").addEventListener("click", (event) => { if (event.target.id === "note-modal") closeNoteModal(); });
document.querySelector("#note-form").addEventListener("submit", (event) => {
  event.preventDefault();
  closeNoteModal();
  showToast("Note save UI only; summary data comes from backend.");
});

loadProfile();
