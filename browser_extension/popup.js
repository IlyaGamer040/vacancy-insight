const DEFAULTS = {
  apiBase: "http://localhost:8090/api/v1",
  title: "python",
  location: "",
  minSalary: "",
  maxSalary: "",
  limit: 20,
  intervalSeconds: 60,
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
    lastError: null,
    pollingStatus: null
  });
  if (!settings.intervalSeconds && settings.intervalMinutes) {
    settings.intervalSeconds = Number(settings.intervalMinutes) * 60;
  }
  $("apiBase").value = settings.apiBase;
  $("title").value = settings.title;
  $("location").value = settings.location;
  $("minSalary").value = settings.minSalary;
  $("maxSalary").value = settings.maxSalary;
  $("limit").value = settings.limit;
  $("intervalSeconds").value = settings.intervalSeconds;
  $("enabled").checked = settings.enabled;
  setIndicator(settings);
  $("pollingStatus").textContent = settings.pollingStatus || "Polling: —";
}

async function saveSettings() {
  const intervalSeconds = Math.max(10, Number($("intervalSeconds").value) || 60);
  const settings = {
    apiBase: $("apiBase").value.trim(),
    title: $("title").value.trim(),
    location: $("location").value.trim(),
    minSalary: $("minSalary").value,
    maxSalary: $("maxSalary").value,
    limit: Number($("limit").value) || 20,
    intervalSeconds,
    enabled: $("enabled").checked
  };

  await chrome.storage.local.set(settings);
  await chrome.storage.local.set({ lastChecked: null });
  try {
    await fetch(`${settings.apiBase.replace(/\/+$/, "")}/vacancies/polling-settings`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        enabled: settings.enabled,
        title: settings.title || null,
        location: settings.location || null,
        min_salary: settings.minSalary ? Number(settings.minSalary) : null,
        max_salary: settings.maxSalary ? Number(settings.maxSalary) : null,
        limit: settings.limit,
        area: 1,
        only_with_salary: Boolean(settings.minSalary || settings.maxSalary)
      })
    });
  } catch (error) {
    setStatus("Не удалось сохранить критерии в API");
  }
  chrome.runtime.sendMessage({
    type: "update_settings",
    intervalSeconds: settings.intervalSeconds
  });
  if (intervalSeconds > Number($("intervalSeconds").value || 0)) {
    setStatus("Минимум 10 сек, применено 10");
  } else {
    setStatus("Сохранено");
  }
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
  if (
    changes.lastChecked ||
    changes.lastCount ||
    changes.lastError ||
    changes.pollingStatus
  ) {
    chrome.storage.local
      .get({
        lastChecked: null,
        lastCount: null,
        lastError: null,
        pollingStatus: null
      })
      .then((data) => {
        setIndicator(data);
        $("pollingStatus").textContent = data.pollingStatus || "Polling: —";
      });
  }
});
