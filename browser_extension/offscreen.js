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
  lastError: null
};

let intervalId = null;

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

async function pollNow(settings) {
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

async function startPolling(settings) {
  const seconds = Math.max(10, Number(settings.intervalSeconds) || 60);
  if (intervalId) {
    clearInterval(intervalId);
  }
  await chrome.storage.local.set({
    pollingStatus: `Polling: offscreen (${seconds} сек)`
  });
  intervalId = setInterval(() => pollNow(settings), seconds * 1000);
  pollNow(settings);
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message?.type === "start_poll") {
    startPolling({ ...DEFAULTS, ...message.settings }).then(() =>
      sendResponse({ ok: true })
    );
    return true;
  }
  return false;
});
