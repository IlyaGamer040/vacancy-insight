const DEFAULTS = {
  apiBase: "http://localhost:8090/api/v1",
  title: "python",
  location: "",
  minSalary: "",
  maxSalary: "",
  limit: 20,
  intervalMinutes: 1,
  enabled: true,
  lastChecked: null,
  lastCount: null,
  lastError: null
};

function scheduleAlarm(intervalMinutes) {
  const minutes = Math.max(1, Number(intervalMinutes) || 5);
  chrome.alarms.create("pollVacancies", { periodInMinutes: minutes });
}

async function getSettings() {
  return await chrome.storage.local.get(DEFAULTS);
}

function buildUrl(base, params, path) {
  const url = new URL(base.replace(/\/+$/, "") + path);
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && String(value).trim() !== "") {
      url.searchParams.set(key, value);
    }
  });
  return url.toString();
}

function toIsoWithOffset(date) {
  return date.toISOString().replace("Z", "+00:00");
}

async function pollNow() {
  const settings = await getSettings();
  if (!settings.enabled) {
    return;
  }

  const now = toIsoWithOffset(new Date());

  const params = {
    title: settings.title,
    location: settings.location,
    min_salary: settings.minSalary,
    max_salary: settings.maxSalary,
    limit: settings.limit
  };

  const countUrl = buildUrl(settings.apiBase, params, "/vacancies/count");

  try {
    const response = await fetch(countUrl);
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    const payload = await response.json();
    const count = Number(payload?.count ?? 0);
    const prevCount = Number(settings.lastCount ?? 0);

    if (prevCount && count > prevCount) {
      const delta = count - prevCount;
      chrome.notifications.create(`vacancy-${Date.now()}`, {
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
      lastError: null
    });
  } catch (error) {
    console.error("Polling failed", error);
    await chrome.storage.local.set({
      lastChecked: now,
      lastCount: 0,
      lastError: error?.message || "Ошибка запроса"
    });
  }
}

chrome.runtime.onInstalled.addListener(async () => {
  const settings = await getSettings();
  await chrome.storage.local.set(settings);
  scheduleAlarm(settings.intervalMinutes);
});

chrome.runtime.onStartup.addListener(async () => {
  const settings = await getSettings();
  scheduleAlarm(settings.intervalMinutes);
  pollNow();
});

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === "pollVacancies") {
    pollNow();
  }
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message?.type === "poll_now") {
    pollNow().then(() => sendResponse({ ok: true }));
    return true;
  }

  if (message?.type === "update_settings") {
    scheduleAlarm(message.intervalMinutes);
    pollNow();
    sendResponse({ ok: true });
    return true;
  }

  return false;
});
