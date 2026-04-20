const bootstrap = window.__BOOTSTRAP__ || { summary: {}, facets: {}, activities: [], featured: [] };

const state = {
  query: "",
  activityType: "",
  context: "",
  origin: "",
  age: "",
  maxDuration: "",
  activeSlug: bootstrap.featured?.[0]?.slug || bootstrap.activities?.[0]?.slug || null,
};

const els = {
  statTotal: document.getElementById("statTotal"),
  statOriginal: document.getElementById("statOriginal"),
  statAdapted: document.getElementById("statAdapted"),
  statExternal: document.getElementById("statExternal"),
  quickChips: document.getElementById("quickChips"),
  searchInput: document.getElementById("searchInput"),
  typeSelect: document.getElementById("typeSelect"),
  contextSelect: document.getElementById("contextSelect"),
  originSelect: document.getElementById("originSelect"),
  ageSelect: document.getElementById("ageSelect"),
  durationSelect: document.getElementById("durationSelect"),
  resetButton: document.getElementById("resetButton"),
  resultsMeta: document.getElementById("resultsMeta"),
  cardsGrid: document.getElementById("cardsGrid"),
  detailEmpty: document.getElementById("detailEmpty"),
  detailContent: document.getElementById("detailContent"),
};

const ORIGIN_LABELS = {
  internal_original: "Original",
  adapted_from_source: "Adaptada",
  external_reference: "Fuente externa",
};

const LABELS = {
  "algo-tranquilo": "Algo tranquilo",
  "algo-rapido": "Algo rápido",
  "antes-de-cenar": "Antes de cenar",
  "antes-de-dormir": "Antes de dormir",
  "bajar-revoluciones": "Bajar revoluciones",
  "con-lo-que-ya-tienes": "Con lo que ya tienes",
  "construccion": "Construcción",
  "construir-juntos": "Construir juntos",
  "cuento": "Cuento",
  "dia-de-lluvia": "Día de lluvia",
  "experimento": "Experimento",
  "external-link": "Explicación externa",
  "hermanos": "Hermanos",
  "imaginacion": "Imaginación",
  "juego-simbolico": "Juego simbólico",
  "manualidad": "Manualidad",
  "manualidades": "Manualidades",
  "movimiento": "Movimiento",
  "naturaleza": "Naturaleza",
  "sensorial": "Sensorial",
  "sin-pantallas": "Sin pantallas",
  "sorpresa-visual": "Sorpresa visual",
  "stem": "STEM",
  "subir-energia": "Subir energía",
};

const CONTEXT_SHORTLIST = [
  "antes-de-cenar",
  "dia-de-lluvia",
  "bajar-revoluciones",
  "con-lo-que-ya-tienes",
  "manualidades",
  "algo-tranquilo",
];

function humanize(value) {
  const raw = String(value || "").trim();
  const key = raw.toLowerCase().replaceAll("_", "-");
  if (LABELS[key]) return LABELS[key];
  if (raw.includes(" ")) {
    return raw.charAt(0).toUpperCase() + raw.slice(1);
  }
  return key
    .split("-")
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function populateSelect(select, values, labelFn = humanize) {
  values.forEach((item) => {
    const option = document.createElement("option");
    option.value = String(item.value);
    option.textContent = `${labelFn(item.value)}${item.count ? ` (${item.count})` : ""}`;
    select.appendChild(option);
  });
}

function renderSummary() {
  els.statTotal.textContent = bootstrap.summary.total || 0;
  els.statOriginal.textContent = bootstrap.summary.internal_original || 0;
  els.statAdapted.textContent = bootstrap.summary.adapted_from_source || 0;
  els.statExternal.textContent = bootstrap.summary.external_reference || 0;
}

function renderQuickChips() {
  const facets = bootstrap.facets.contexts || [];
  const chosen = facets.filter((item) => CONTEXT_SHORTLIST.includes(item.value));
  els.quickChips.innerHTML = "";
  chosen.forEach((item) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `quick-chip ${state.context === item.value ? "active" : ""}`;
    button.textContent = humanize(item.value);
    button.addEventListener("click", () => {
      state.context = state.context === item.value ? "" : item.value;
      els.contextSelect.value = state.context;
      renderQuickChips();
      renderResults();
    });
    els.quickChips.appendChild(button);
  });
}

function filterActivities() {
  return (bootstrap.activities || []).filter((item) => {
    const query = state.query.trim().toLowerCase();
    if (query) {
      const haystack = [
        item.title,
        item.summary,
        ...(item.materials || []),
        ...(item.activity_types || []),
        ...(item.contexts || []),
        ...(item.search_tags || []),
      ].join(" ").toLowerCase();
      if (!haystack.includes(query)) {
        return false;
      }
    }

    if (state.activityType && !(item.activity_types || []).includes(state.activityType)) {
      return false;
    }
    if (state.context && !(item.contexts || []).includes(state.context)) {
      return false;
    }
    if (state.origin && item.origin_type !== state.origin) {
      return false;
    }
    if (state.age) {
      const age = Number(state.age);
      if (age < item.ages.min || age > item.ages.max) {
        return false;
      }
    }
    if (state.maxDuration) {
      const duration = Number(state.maxDuration);
      if (item.duration.max > duration) {
        return false;
      }
    }
    return true;
  });
}

function cardTemplate(item) {
  const type = item.activity_types?.[0] || "actividad";
  const meta = [item.age_label, item.duration_label, item.prep_level && `prep ${item.prep_level}`, item.mess_level && `lío ${item.mess_level}`]
    .filter(Boolean)
    .slice(0, 4);
  const tags = (item.contexts || []).slice(0, 3);
  return `
    <article class="activity-card ${state.activeSlug === item.slug ? "active" : ""}" data-slug="${item.slug}">
      <div class="card-cover">
        <div class="badge-row">
          <span class="badge type">${humanize(type)}</span>
          <span class="badge origin">${item.provenance_label}</span>
          <span class="badge delivery">${item.delivery_label}</span>
        </div>
      </div>
      <div class="card-body">
        <h3>${item.title}</h3>
        <div class="meta-row">
          ${meta.map((value) => `<span class="meta-pill">${value}</span>`).join("")}
        </div>
        <p class="card-summary">${item.summary}</p>
        <div class="tag-row">
          ${tags.map((value) => `<span class="tag-pill">${humanize(value)}</span>`).join("")}
        </div>
      </div>
    </article>
  `;
}

function renderDetail(item) {
  if (!item) {
    els.detailEmpty.classList.remove("hidden");
    els.detailContent.classList.add("hidden");
    els.detailContent.innerHTML = "";
    return;
  }

  const assets = (item.graphics || []).map((asset) => {
    const preview = asset.kind === "image"
      ? `<img class="asset-image" src="${asset.url}" alt="${asset.label || 'Imagen de referencia'}" />`
      : "";
    return `
      <div class="asset-card">
        ${preview}
        <a class="asset-link" href="${asset.url}" target="_blank" rel="noreferrer noopener">
          <span>${asset.label || humanize(asset.kind)}</span>
          <span>↗</span>
        </a>
      </div>
    `;
  }).join("");

  const sourceBlock = item.source
    ? `<p><strong>Fuente:</strong> ${item.source.publisher} · <a href="${item.source.url}" target="_blank" rel="noreferrer noopener">abrir</a></p>`
    : `<p><strong>Fuente:</strong> idea original del catálogo.</p>`;

  els.detailEmpty.classList.add("hidden");
  els.detailContent.classList.remove("hidden");
  els.detailContent.innerHTML = `
    <section class="detail-title">
      <div class="badge-row">
        <span class="badge type">${humanize(item.activity_types?.[0] || "actividad")}</span>
        <span class="badge origin">${item.provenance_label}</span>
        <span class="badge delivery">${item.delivery_label}</span>
      </div>
      <h2>${item.title}</h2>
      <p class="detail-summary">${item.summary}</p>
      <div class="meta-row">
        <span class="meta-pill">${item.age_label}</span>
        <span class="meta-pill">${item.duration_label}</span>
        <span class="meta-pill">prep ${item.prep_level}</span>
        <span class="meta-pill">lío ${item.mess_level}</span>
        <span class="meta-pill">energía ${item.energy_level}</span>
      </div>
    </section>

    <section class="detail-box">
      <h4>Materiales</h4>
      <div class="tag-row">
        ${(item.materials || []).map((value) => `<span class="tag-pill">${value}</span>`).join("")}
      </div>
    </section>

    <section class="detail-box">
      <h4>Por qué funciona</h4>
      <p>${item.why_it_works || ""}</p>
    </section>

    <section class="detail-box">
      <h4>Pasos</h4>
      <ol class="detail-list">
        ${(item.steps || []).map((step) => `<li>${step}</li>`).join("")}
      </ol>
    </section>

    <section class="detail-box">
      <h4>Variantes</h4>
      <ul class="detail-list">
        ${(item.variations || []).map((step) => `<li>${step}</li>`).join("")}
      </ul>
    </section>

    <section class="detail-box">
      <h4>Desarrolla</h4>
      <div class="tag-row">
        ${(item.what_develops || []).map((value) => `<span class="tag-pill">${humanize(value)}</span>`).join("")}
      </div>
    </section>

    <section class="detail-box">
      <h4>Procedencia y materiales gráficos</h4>
      ${sourceBlock}
      <div class="asset-list">${assets || '<p>No hay assets enlazados todavía.</p>'}</div>
    </section>
  `;
}

function renderResults() {
  const results = filterActivities();
  els.resultsMeta.textContent = `${results.length} actividades encontradas`;

  if (!results.length) {
    els.cardsGrid.innerHTML = `<div class="empty-results">No hay resultados para estos filtros.</div>`;
    renderDetail(null);
    return;
  }

  els.cardsGrid.innerHTML = results.map(cardTemplate).join("");
  if (!results.some((item) => item.slug === state.activeSlug)) {
    state.activeSlug = results[0].slug;
  }
  const active = results.find((item) => item.slug === state.activeSlug) || results[0];
  renderDetail(active);

  els.cardsGrid.querySelectorAll(".activity-card").forEach((card) => {
    card.addEventListener("click", () => {
      state.activeSlug = card.dataset.slug;
      renderResults();
    });
  });
}

function initControls() {
  populateSelect(els.typeSelect, bootstrap.facets.types || []);
  populateSelect(els.contextSelect, bootstrap.facets.contexts || []);
  populateSelect(els.originSelect, bootstrap.facets.origins || [], (value) => ORIGIN_LABELS[value] || humanize(value));
  populateSelect(els.ageSelect, bootstrap.facets.ages || [], (value) => `${value} años`);
  populateSelect(els.durationSelect, bootstrap.facets.durations || [], (value) => `${value} min`);

  els.searchInput.addEventListener("input", (event) => {
    state.query = event.target.value;
    renderResults();
  });
  els.typeSelect.addEventListener("change", (event) => {
    state.activityType = event.target.value;
    renderResults();
  });
  els.contextSelect.addEventListener("change", (event) => {
    state.context = event.target.value;
    renderQuickChips();
    renderResults();
  });
  els.originSelect.addEventListener("change", (event) => {
    state.origin = event.target.value;
    renderResults();
  });
  els.ageSelect.addEventListener("change", (event) => {
    state.age = event.target.value;
    renderResults();
  });
  els.durationSelect.addEventListener("change", (event) => {
    state.maxDuration = event.target.value;
    renderResults();
  });

  els.resetButton.addEventListener("click", () => {
    state.query = "";
    state.activityType = "";
    state.context = "";
    state.origin = "";
    state.age = "";
    state.maxDuration = "";
    els.searchInput.value = "";
    els.typeSelect.value = "";
    els.contextSelect.value = "";
    els.originSelect.value = "";
    els.ageSelect.value = "";
    els.durationSelect.value = "";
    renderQuickChips();
    renderResults();
  });
}

renderSummary();
initControls();
renderQuickChips();
renderResults();
