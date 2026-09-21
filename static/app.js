const WEEKDAYS = ["So", "Mo", "Di", "Mi", "Do", "Fr", "Sa"];

// Favorites (US-9) live only in this browser: a list of act ids in localStorage, never sent
// to the server. The id is stable across re-seeding because the seed is deterministic and
// restarts the id sequences.
const FAVORITES_KEY = "festival-planner.favorites";
const favorites = loadFavorites();

// localStorage can be missing or throw (private mode, blocked site data). The page must work
// anyway, so favorites then only last until the next reload.
function loadFavorites() {
  try {
    const ids = JSON.parse(localStorage.getItem(FAVORITES_KEY));
    return new Set(Array.isArray(ids) ? ids : []);
  } catch {
    return new Set();
  }
}

function saveFavorites() {
  try {
    localStorage.setItem(FAVORITES_KEY, JSON.stringify([...favorites]));
  } catch {
    // Storage unavailable: keep the in-memory favorites for this page view.
  }
}

function toggleFavorite(id) {
  if (favorites.has(id)) {
    favorites.delete(id);
  } else {
    favorites.add(id);
  }
  saveFavorites();
  renderFavorites();
  return favorites.has(id);
}

// All acts, unfiltered (US-10): the personal schedule shows every favorite, independent of the
// day and stage filter, so it cannot use the filtered program list. Loaded once per page view.
let allActs = null;

async function loadAllActs() {
  const response = await fetch("/api/program");
  allActs = (await response.json()).items;
  renderFavorites();
}

// Items come sorted by start time from the API, so filtering keeps the chronological order.
// Stored ids without a matching act (e.g. after a data change) are simply skipped.
function renderFavorites() {
  if (allActs === null) return; // not loaded yet
  const items = allActs.filter((item) => favorites.has(item.id));
  const list = document.getElementById("favorites-list");

  list.innerHTML = "";
  for (const item of items) {
    list.appendChild(renderFavoriteItem(item));
  }
  list.hidden = items.length === 0;
  document.getElementById("favorites-empty").hidden = items.length > 0;
  // Visible in the collapsed accordion, so the count is known without opening it.
  document.getElementById("favorites-count").textContent = `(${items.length})`;
  document.getElementById("favorites").hidden = false;
}

// Favorites can span several festival days, so each entry shows the day as well.
function renderFavoriteItem(item) {
  const li = document.createElement("li");
  li.className = "flex flex-wrap items-baseline gap-x-3";

  const time = document.createElement("span");
  time.className = "shrink-0 text-gray-600 tabular-nums";
  time.textContent =
    `${formatDay(item.starts_at.slice(0, 10))} ${formatTime(item.starts_at)}–${formatTime(item.ends_at)}`;

  const title = document.createElement("span");
  title.className = "min-w-0 font-semibold break-words";
  title.textContent = item.title;

  const stage = document.createElement("span");
  stage.className = "text-gray-600";
  stage.textContent = item.stage;

  li.append(time, title, stage);
  return li;
}

async function loadFilters() {
  const [stages, days] = await Promise.all([
    fetch("/api/stages").then((response) => response.json()),
    fetch("/api/days").then((response) => response.json()),
  ]);
  fillSelect("stage-filter", stages.map((stage) => [stage, stage]));
  fillSelect("day-filter", days.map((day) => [day, formatDay(day)]));
  for (const id of ["stage-filter", "day-filter"]) {
    document.getElementById(id).addEventListener("change", loadProgram);
  }
}

function fillSelect(id, options) {
  const select = document.getElementById(id);
  for (const [value, label] of options) {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = label;
    select.appendChild(option);
  }
}

// Counts loadProgram() calls. On a fast filter change the answers can arrive out of order;
// only the answer to the latest request may render, otherwise the list would not match the filters.
let latestProgramRequest = 0;

async function loadProgram() {
  const request = ++latestProgramRequest;
  const params = new URLSearchParams();
  const stage = document.getElementById("stage-filter").value;
  const day = document.getElementById("day-filter").value;
  if (stage) params.set("stage", stage);
  if (day) params.set("day", day);

  const query = params.toString();
  const response = await fetch(query ? `/api/program?${query}` : "/api/program");
  const data = await response.json();
  if (request !== latestProgramRequest) return; // stale answer, a newer request is pending
  renderNow(data.now);
  renderProgram(data.items, Boolean(stage || day));
}

function renderNow(now) {
  document.getElementById("now-hint").textContent = `Festivalzeit: ${formatTime(now)} Uhr`;
}

// With a filter set, an empty list only means "nothing matches", not "no program at all".
const EMPTY_HINTS = {
  noProgram: "Es sind noch keine Programmpunkte vorhanden.",
  noMatch: "Für diese Auswahl gibt es keine Acts.",
};

function renderProgram(items, isFiltered) {
  const program = document.getElementById("program");
  const emptyHint = document.getElementById("empty-hint");

  program.innerHTML = "";
  emptyHint.hidden = items.length > 0;
  emptyHint.textContent = isFiltered ? EMPTY_HINTS.noMatch : EMPTY_HINTS.noProgram;

  for (const [day, dayItems] of groupByDay(items)) {
    program.appendChild(renderDay(day, dayItems));
  }
}

// Items arrive sorted by start time, so the groups are in chronological order as well.
// An act belongs to the day it starts on, even if it ends after midnight.
function groupByDay(items) {
  const groups = new Map();
  for (const item of items) {
    const day = item.starts_at.slice(0, 10);
    if (!groups.has(day)) groups.set(day, []);
    groups.get(day).push(item);
  }
  return groups;
}

function renderDay(day, items) {
  const section = document.createElement("section");

  const heading = document.createElement("h2");
  heading.className = "mb-2 text-lg font-semibold text-gray-800";
  heading.textContent = formatDay(day);

  const list = document.createElement("ul");
  list.className = "divide-y divide-gray-200 overflow-hidden rounded-lg bg-white shadow-sm";
  for (const item of items) {
    list.appendChild(renderItem(item));
  }

  section.append(heading, list);
  return section;
}

// Tailwind only generates classes it finds in static/, so they are written out in full here
// (no string building like `bg-${color}-100`).
const ITEM_CLASSES =
  "flex flex-wrap items-center gap-x-3 gap-y-1 border-l-4 px-4 py-3 " +
  "sm:grid sm:grid-cols-[7rem_1fr_10rem_2.75rem] sm:gap-4";
const STATUS_CLASSES = {
  now: "border-l-green-600 bg-green-50",
  next: "border-l-amber-500 bg-amber-50",
};
const NO_STATUS_CLASSES = "border-l-transparent";
// Text badge, so the status does not rely on color alone.
const BADGE_CLASSES = "ml-2 inline-block rounded-full px-2 py-0.5 align-middle text-xs font-medium";
const STATUS_BADGES = {
  now: { label: "läuft jetzt", classes: "bg-green-700 text-white" },
  next: { label: "als Nächstes", classes: "bg-amber-200 text-amber-900" },
};
// 44 px touch target; the negative margin keeps the row as compact as before.
// Filled vs. outlined star, so the state does not rely on color alone.
const FAVORITE_BUTTON_CLASSES =
  "-my-2 flex size-11 shrink-0 items-center justify-center rounded-full text-2xl leading-none " +
  "text-gray-400 hover:bg-gray-100 focus-visible:outline-2 focus-visible:outline-indigo-500 " +
  "aria-pressed:text-amber-500";

function renderItem(item) {
  const li = document.createElement("li");
  li.className = `${ITEM_CLASSES} ${STATUS_CLASSES[item.status] ?? NO_STATUS_CLASSES}`;

  const time = document.createElement("span");
  time.className = "shrink-0 text-sm text-gray-600 tabular-nums";
  time.textContent = `${formatTime(item.starts_at)}–${formatTime(item.ends_at)}`;

  const title = document.createElement("span");
  title.className = "min-w-0 flex-1 font-semibold break-words";
  title.textContent = item.title;
  const badge = STATUS_BADGES[item.status];
  if (badge) title.appendChild(renderBadge(badge));

  const stage = document.createElement("span");
  // Mobile: own line below time/title/star, so the star does not squeeze the title.
  stage.className =
    "order-last basis-full text-sm text-gray-600 sm:order-none sm:basis-auto sm:text-right";
  stage.textContent = item.stage;

  li.append(time, title, stage, renderFavoriteButton(item));
  return li;
}

function renderFavoriteButton(item) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = FAVORITE_BUTTON_CLASSES;
  button.setAttribute("aria-label", `${item.title} als Favorit merken`);
  showFavoriteState(button, favorites.has(item.id));
  button.addEventListener("click", () => showFavoriteState(button, toggleFavorite(item.id)));
  return button;
}

function showFavoriteState(button, isFavorite) {
  button.setAttribute("aria-pressed", String(isFavorite));
  button.textContent = isFavorite ? "★" : "☆";
}

function renderBadge({ label, classes }) {
  const badge = document.createElement("span");
  badge.className = `${BADGE_CLASSES} ${classes}`;
  badge.textContent = label;
  return badge;
}

function formatTime(isoString) {
  return isoString.slice(11, 16);
}

// "2026-09-18" -> "Fr, 18.09." – built by hand, the weekday comes from the date itself,
// independent of the device's time zone and locale.
function formatDay(isoDate) {
  const [year, month, day] = isoDate.split("-").map(Number);
  const weekday = WEEKDAYS[new Date(Date.UTC(year, month - 1, day)).getUTCDay()];
  return `${weekday}, ${String(day).padStart(2, "0")}.${String(month).padStart(2, "0")}.`;
}

loadFilters();
loadProgram();
loadAllActs();
