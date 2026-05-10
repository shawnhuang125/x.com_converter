let socket = null;
const LANG_MAP = {
    "en": {
        "ui-title": "Comma - Youtube Downloader",
        "url-input-placeholder": "Paste YouTube link here...",
        "btn-download-v": "Download Video (MP4)",
        "btn-download-a": "Download Audio (MP3)",
        "btn-stop": "Stop",
        "video-title-default": "Loading video title...",
        "video-uploader-default": "Channel Name",
        "video-duration-default": "Duration: 00:00",
        "stat-speed-default": "Speed: 0 MB/s",
        "stat-eta-default": "ETA: --:--",
        "lang-url": "Video URL",
        "lang-toggle": "繁體中文", // 在英文介面，按鈕讓你切換回中文

        "welcome-title": "Welcome to Comma",
        "welcome-text": "Your minimalist media download companion.",
        "welcome-start-btn": "Start Now"
    },
    "zh-TW": {
        "ui-title": "Comma - Youtube 下載器",
        "url-input-placeholder": "貼上 YouTube 連結...",
        "btn-download-v": "下載影片 (MP4)",
        "btn-download-a": "下載音訊 (MP3)",
        "btn-stop": "停止",
        "video-title-default": "影片標題正在載入...",
        "video-uploader-default": "頻道名稱",
        "video-duration-default": "時長: 00:00",
        "stat-speed-default": "速度: 0 MB/s",
        "stat-eta-default": "剩餘時間: --:--",
        "lang-url": "影片網址",
        "lang-toggle": "English",
        "welcome-title": "歡迎來到 Comma",
        "welcome-text": "您的極簡多媒體下載夥伴。",
        "welcome-start-btn": "立即開始"
    }
};


/**
 * 載入 Partial 頁面
 * @param {string} page 頁面名稱 (welcome, downloader)
 */
async function loadPartial(pageName) {
    const contentArea = document.getElementById('app-content');
    
    try {
        // 改為請求你在後端定義的 API 路由
        const response = await fetch(`/page/${pageName}`);
        if (!response.ok) throw new Error("Page not found");
        
        const html = await response.text();
        contentArea.innerHTML = html;

        // 重新初始化下載器邏輯
        if (pageName === 'downloader') {
            initDownloaderEvents();
        }
        // --- 加上這行讓導覽列底線會動 ---
        updateNavActiveState(pageName);

        // 套用語系
        applyLanguage(currentLang);

    } catch (err) {
        console.error("Load failed:", err);
    }
}

function updateNavActiveState(pageName) {
    const items = document.querySelectorAll('.nav-item');
    items.forEach(item => item.classList.remove('active'));
    
    const activeItem = document.getElementById(`nav-${pageName}`);
    if (activeItem) activeItem.classList.add('active');
}

// 由於 HTML 是動態插入的，按鈕事件需要重新綁定
function initDownloaderEvents() {
    const btnV = document.getElementById("btn-download-v");
    const btnA = document.getElementById("btn-download-a");
    
    if (btnV) btnV.onclick = () => startDownload(false);
    if (btnA) btnA.onclick = () => startDownload(true);
    
    // 如果之前有正在下載的狀態，可以從這裡恢復 UI 邏輯
}

// 修改初始化邏輯
window.addEventListener("DOMContentLoaded", () => {
    // 優先讀取紀錄的頁面，預設為 welcome
    const savedPage = localStorage.getItem('current_page') || 'welcome';
    loadPartial(savedPage);
    applyLanguage(currentLang);
});

function startDownload(as_mp3) {
    const url = document.getElementById('url-input').value;
    if (!url) {
        alert("請輸入網址");
        return;
    }

    // 初始化介面
    document.getElementById("dynamic-card").style.display = "block";
    const stopBtn = document.getElementById("btn-stop");
    stopBtn.style.display = "inline-block"; // 顯示停止按鈕
    stopBtn.disabled = false;

    socket = new WebSocket(`ws://${window.location.host}/ws/download`);

    socket.onopen = () => {
        // 第一階段：僅獲取資訊與解析度
        socket.send(JSON.stringify({ action: "get_meta", url: url }));
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === "meta_and_res") {
            // 更新影片標題、封面等資訊
            updateMeta(data);
            
            // 判斷是否需要顯示解析度選擇器
            if (!as_mp3 && data.resolutions && data.resolutions.length > 0) {
                // 下載影片且有解析度選項 -> 顯示選單
                showResolutionSelector(data.resolutions, url, as_mp3);
            } else {
                // 下載音訊或是沒抓到解析度清單 -> 直接發送下載指令
                socket.send(JSON.stringify({ 
                    action: "start_download", 
                    url: url, 
                    as_mp3: as_mp3,
                    resolution: null // 音訊不需要解析度
                }));
            }
        }
        else if (data.type === "progress") {
            // 隱藏選單（如果有的話），開始跑進度條
            const resContainer = document.getElementById("res-selector-container");
            if (resContainer) resContainer.style.display = "none";

            document.getElementById("progress-bar-fill").style.width = data.percent + "%";
            document.getElementById("stat-percent").innerText = data.percent + "%";
            document.getElementById("stat-speed").innerText = "速度: " + data.speed;
            document.getElementById("stat-eta").innerText = "剩餘: " + data.eta;
        } 
        else if (data.type === "done") {
            // 觸發瀏覽器下載
            const link = document.createElement("a");
            link.href = data.download_url;
            link.download = data.filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            setTimeout(resetUI, 2000); // 2秒後重置
        } 
        else if (data.type === "error") {
            alert("錯誤: " + data.msg);
            resetUI();
        }
    };
}

let currentLang = localStorage.getItem("comma_lang") || "en";

function applyLanguage(lang) {
    const dict = LANG_MAP[lang];
    if (!dict) return;

    // 取得所有需要變更文字的元素
    const elements = {
        "ui-title": document.getElementById("ui-title"),
        "url-input": document.getElementById("url-input"),
        "btn-download-v": document.getElementById("btn-download-v"),
        "btn-download-a": document.getElementById("btn-download-a"),
        "btn-stop": document.getElementById("btn-stop"),
        "lang-toggle": document.getElementById("lang-toggle"),
        "url-label": document.querySelector(".lang-url"),
        "welcome-title": dict["welcome-title"],
        "welcome-text": dict["welcome-text"],
        "welcome-start-btn": dict["welcome-start-btn"]
    };

    // 批量更新文字
    if (elements["ui-title"]) elements["ui-title"].innerText = dict["ui-title"];
    if (elements["url-input"]) elements["url-input"].placeholder = dict["url-input-placeholder"];
    if (elements["btn-download-v"]) elements["btn-download-v"].innerText = dict["btn-download-v"];
    if (elements["btn-download-a"]) elements["btn-download-a"].innerText = dict["btn-download-a"];
    if (elements["btn-stop"]) elements["btn-stop"].innerText = dict["btn-stop"];
    if (elements["lang-toggle"]) elements["lang-toggle"].innerText = dict["lang-toggle"];
    if (elements["url-label"]) elements["url-label"].innerText = dict["lang-url"];

    // 儲存狀態
    currentLang = lang;
    localStorage.setItem("comma_lang", lang);
}

// 3. 綁定切換按鈕
document.getElementById("lang-toggle").onclick = () => {
    const nextLang = (currentLang === "en") ? "zh-TW" : "en";
    applyLanguage(nextLang);
};

// 4. 網頁載入後執行一次初始化
window.addEventListener("DOMContentLoaded", () => {
    applyLanguage(currentLang);
});

function showResolutionSelector(resList, url, as_mp3) {
    const container = document.getElementById("res-selector-container");
    const pillsWrapper = document.getElementById("res-pills-container");
    const progressSection = document.getElementById("progress-section");

    // 1. 隱藏進度條，顯示按鈕區
    progressSection.style.display = "none";
    container.style.display = "block";
    pillsWrapper.innerHTML = "";

    // 2. 只顯示到 4K (2160p) 以下的解析度
    const filteredRes = resList.filter(res => res <= 2160);

    filteredRes.forEach(res => {
        const btn = document.createElement("button");
        btn.className = "res-pill-btn";
        btn.innerText = res + "P";
        
        btn.onclick = () => {
            // A. 隱藏按鈕區，顯示進度條
            container.style.display = "none";
            progressSection.style.display = "block";

            // B. 發送下載請求
            socket.send(JSON.stringify({ 
                action: "start_download", 
                url: url, 
                as_mp3: as_mp3, 
                resolution: res 
            }));
        };
        
        pillsWrapper.appendChild(btn);
    });
}

// 修改 resetUI 確保狀態重置
function resetUI() {
    // ... 原有邏輯 ...
    const resContainer = document.getElementById("res-selector-container");
    const progressSection = document.getElementById("progress-section");
    
    if (resContainer) resContainer.style.display = "none";
    if (progressSection) progressSection.classList.add("u-hidden");
    
    // 重置進度條數值
    document.getElementById("progress-bar-fill").style.width = "0%";
    // ...
}
function updateMeta(data) {
    document.getElementById("video-title").innerText = data.title || "未知標題";
    document.getElementById("video-uploader").innerText = data.uploader || "未知頻道";
    if (data.thumb) {
        document.getElementById("preview-img").src = data.thumb;
    }
    if (data.duration) {
        const mins = Math.floor(data.duration / 60);
        const secs = data.duration % 60;
        document.getElementById("video-duration").innerText = `時長: ${mins}:${secs.toString().padStart(2, '0')}`;
    }
}

function resetUI() {
    const dict = LANG_MAP[currentLang]; // 抓當前語系字典

    document.getElementById("dynamic-card").style.display = "none";
    document.getElementById("btn-stop").style.display = "none";
    document.getElementById("res-selector-container").style.display = "none";
    document.getElementById("progress-section").style.display = "none";
    
    document.getElementById("url-input").value = "";
    document.getElementById("progress-bar-fill").style.width = "0%";
    document.getElementById("stat-percent").innerText = "0%";
    
    // 恢復該語系的預設佔位文字
    document.getElementById("video-title").innerText = dict["video-title-default"];
    document.getElementById("video-uploader").innerText = dict["video-uploader-default"];
    document.getElementById("video-duration").innerText = dict["video-duration-default"];
    document.getElementById("preview-img").src = "https://via.placeholder.com/240x135/111/fff?text=Waiting";
    
    if (socket) {
        socket.close();
        socket = null;
    }
}

document.getElementById("btn-download-v").onclick = () => startDownload(false);
document.getElementById("btn-download-a").onclick = () => startDownload(true);