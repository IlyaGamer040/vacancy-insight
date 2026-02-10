const DEFAULTS = {
  apiBase: "http://localhost:8090/api/v1",
  title: "python",
  location: "",
  minSalary: "",
  maxSalary: "",
  limit: 20,
  intervalMinutes: 1,
  enabled: true
};

function $(id) {
  return document.getElementById(id);
}

function setStatus(text) {
  const status = $("status");
  status.textContent = text;
  if (text) {
    setTimeout(() => (status.textContent = ""), 2000);
  }
}

function setIndicator({ lastChecked, lastCount, lastError }) {
  $("lastCheck").textContent = lastChecked
    ? `Последняя проверка: ${new Date(lastChecked).toLocaleString()}`
    : "Последняя проверка: —";
  $("lastCount").textContent =
    typeof lastCount === "number" ? `Найдено: ${lastCount}` : "Найдено: —";
  $("lastError").textContent = lastError ? `Ошибка: ${lastError}` : "";
}

async function loadSettings() {
  const settings = await chrome.storage.local.get({
    ...DEFAULTS,
    lastChecked: null,
    lastCount: null,
    lastError: null
  });
  $("apiBase").value = settings.apiBase;
  $("title").value = settings.title;
  $("location").value = settings.location;
  $("minSalary").value = settings.minSalary;
  $("maxSalary").value = settings.maxSalary;
  $("limit").value = settings.limit;
  $("intervalMinutes").value = settings.intervalMinutes;
  $("enabled").checked = settings.enabled;
  setIndicator(settings);
}

async function saveSettings() {
  const settings = {
    apiBase: $("apiBase").value.trim(),
    title: $("title").value.trim(),
    location: $("location").value.trim(),
    minSalary: $("minSalary").value,
    maxSalary: $("maxSalary").value,
    limit: Number($("limit").value) || 20,
    intervalMinutes: Number($("intervalMinutes").value) || 5,
    enabled: $("enabled").checked
  };

  await chrome.storage.local.set(settings);
  await chrome.storage.local.set({ lastChecked: null });
  chrome.runtime.sendMessage({
    type: "update_settings",
    intervalMinutes: settings.intervalMinutes
  });
  setStatus("Сохранено");
}

async function checkNow() {
  chrome.runtime.sendMessage({ type: "poll_now" }, () => {
    setStatus("Проверка запущена");
  });
}

document.addEventListener("DOMContentLoaded", () => {
  loadSettings();
  $("save").addEventListener("click", saveSettings);
  $("check").addEventListener("click", checkNow);
});

chrome.storage.onChanged.addListener((changes) => {
  if (changes.lastChecked || changes.lastCount || changes.lastError) {
    chrome.storage.local
      .get({ lastChecked: null, lastCount: null, lastError: null })
      .then(setIndicator);
  }
});
