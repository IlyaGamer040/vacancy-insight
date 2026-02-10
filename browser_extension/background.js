const DEFAULTS = {
  apiBase: "http://localhost:8090/api/v1",
  title: "python",
  location: "",
  minSalary: "",
  maxSalary: "",
  limit: 20,
  intervalSeconds: 60,
  enabled: true,
  lastChecked: null,
  lastCount: null,
  lastError: null,
  pollingStatus: null
};

const ALARM_NAME = "pollVacancies";

async function getSettings() {
  return await chrome.storage.local.get(DEFAULTS);
}

function buildCountUrl(settings) {
  const base = settings.apiBase.replace(/\/+$/, "");
  const url = new URL(base + "/vacancies/count");
  if (settings.title) url.searchParams.set("title", settings.title);
  if (settings.location) url.searchParams.set("location", settings.location);
  if (settings.minSalary) url.searchParams.set("min_salary", settings.minSalary);
  if (settings.maxSalary) url.searchParams.set("max_salary", settings.maxSalary);
  if (settings.limit) url.searchParams.set("limit", settings.limit);
  return url.toString();
}

async function pollNow() {
  const settings = await getSettings();
  if (!settings.enabled) return;

  const now = new Date().toISOString().replace("Z", "+00:00");
  const countUrl = buildCountUrl(settings);

  try {
    const response = await fetch(countUrl);
    if (!response.ok) throw new Error(`API ${response.status}`);
    const data = await response.json();
    const count = Number(data?.count ?? 0);
    const prevCount = Number(settings.lastCount ?? 0);

    if (prevCount > 0 && count > prevCount) {
      const delta = count - prevCount;
      chrome.notifications.create(`vac-${Date.now()}`, {
        type: "basic",
        iconUrl: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAQAAAC1+jfqAAAAKklEQVR42mNgGAXUADYyYGBg+M+ABgaG/0M0I1CqgCkGAAAjUQkZJ6Q2cAAAAASUVORK5CYII=",
        title: "Новые вакансии",
        message: `Появилось новых: ${delta}`
      });
      chrome.action.setBadgeBackgroundColor({ color: "#E11D48" });
      chrome.action.setBadgeText({ text: String(delta) });
    } else {
      chrome.action.setBadgeText({ text: "" });
    }

    await chrome.storage.local.set({
      lastChecked: now,
      lastCount: count,
      lastError: null,
      pollingStatus: `Polling: OK (${new Date().toLocaleTimeString()})`
    });
  } catch (error) {
    await chrome.storage.local.set({
      lastChecked: now,
      lastError: error?.message || "Ошибка",
      pollingStatus: `Polling: ошибка (${new Date().toLocaleTimeString()})`
    });
  }
}

// --- Alarm ---
chrome.alarms.create(ALARM_NAME, { delayInMinutes: 0.5, periodInMinutes: 1 });

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === ALARM_NAME) {
    pollNow();
  }
});

// --- При установке / запуске ---
chrome.runtime.onInstalled.addListener(() => {
  chrome.alarms.create(ALARM_NAME, { delayInMinutes: 0.5, periodInMinutes: 1 });
  pollNow();
});

chrome.runtime.onStartup.addListener(() => {
  chrome.alarms.create(ALARM_NAME, { delayInMinutes: 0.5, periodInMinutes: 1 });
  pollNow();
});

// --- Сообщения из popup ---
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message?.type === "poll_now") {
    pollNow().then(() => sendResponse({ ok: true }));
    return true;
  }
  if (message?.type === "update_settings") {
    pollNow().then(() => sendResponse({ ok: true }));
    return true;
  }
  return false;
});
