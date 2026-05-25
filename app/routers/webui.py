"""
SnapTube/VidMate-style mobile-first WebUI.
Served at / as a single-page HTML application.
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["webui"])


@router.get("/", response_class=HTMLResponse)
async def webui():
    return _HTML


_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<meta name="theme-color" content="#0a0a1a">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<title>YTDLP</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>&#x1f3b5;</text></svg>">
<style>
/* Variables */
:root{
  --bg:#0a0a1a;--bg2:#111128;--card:#1a1a3e;--card2:#222255;
  --input:#151530;--grad:linear-gradient(135deg,#667eea,#764ba2);
  --grad-h:linear-gradient(90deg,#667eea,#764ba2);
  --t1:#fff;--t2:#9999bb;--t3:#555577;
  --border:rgba(255,255,255,.06);--accent:#667eea;--accent2:#8b9cf7;
  --green:#00e676;--red:#ff5252;--yellow:#ffd740;--blue:#448aff;
  --r:14px;--rs:10px;--rx:6px;
  --sh:0 4px 24px rgba(0,0,0,.3);
}
*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{height:100%;overflow:hidden}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
  background:var(--bg);color:var(--t1);-webkit-font-smoothing:antialiased}

/* Layout */
#app{display:flex;flex-direction:column;height:100%;max-width:520px;margin:0 auto;position:relative}
header{display:flex;align-items:center;justify-content:space-between;padding:12px 16px;
  background:rgba(10,10,26,.95);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  border-bottom:1px solid var(--border);z-index:10;position:sticky;top:0}
.h-left{display:flex;align-items:center;gap:8px}
.logo{font-size:24px}
.app-name{font-size:20px;font-weight:800;background:var(--grad);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;letter-spacing:-.5px}
.h-right{color:var(--t2);text-decoration:none;padding:8px;border-radius:var(--rx);transition:.2s}
.h-right:hover{background:var(--card);color:var(--t1)}
main{flex:1;overflow-y:auto;overflow-x:hidden;-webkit-overflow-scrolling:touch;padding:16px 16px 24px}
.page{display:none;animation:fadeIn .3s ease}.page.active{display:block}

/* Icons */
.ic{display:inline-flex;align-items:center;justify-content:center}
.ic svg{width:100%;height:100%}
.ic-sm{width:18px;height:18px}
.ic-md{width:22px;height:22px}
.ic-lg{width:48px;height:48px}
.ic-xl{width:64px;height:64px}

/* Input Section */
.input-section{margin-bottom:20px}
.input-row{display:flex;gap:8px;margin-bottom:10px}
.input-row input{flex:1;background:var(--input);border:1.5px solid var(--border);
  border-radius:var(--rs);padding:14px 16px;color:var(--t1);font-size:15px;outline:none;
  transition:border .2s}
.input-row input:focus{border-color:var(--accent)}
.input-row input::placeholder{color:var(--t3)}
.btn-icon{width:48px;height:48px;border:none;border-radius:var(--rs);
  background:var(--card);color:var(--t2);cursor:pointer;display:flex;
  align-items:center;justify-content:center;transition:.2s;flex-shrink:0}
.btn-icon:active{transform:scale(.93);background:var(--card2)}
.btn-fetch{width:100%;padding:14px;border:none;border-radius:var(--rs);
  background:var(--grad);color:#fff;font-size:15px;font-weight:700;cursor:pointer;
  display:flex;align-items:center;justify-content:center;gap:8px;transition:.2s;
  letter-spacing:.3px}
.btn-fetch:disabled{opacity:.4;cursor:not-allowed;transform:none}
.btn-fetch:not(:disabled):active{transform:scale(.97)}

/* Skeleton */
.skeleton{background:linear-gradient(90deg,var(--card) 25%,var(--card2) 50%,var(--card) 75%);
  background-size:200% 100%;animation:shimmer 1.5s infinite;border-radius:var(--rx)}
.skel-thumb{width:100%;padding-top:56.25%;border-radius:var(--rs);margin-bottom:12px}
.skel-line{height:16px;border-radius:4px;margin-bottom:8px}
.skel-line.w80{width:80%}.skel-line.w60{width:60%}

/* Preview Card */
.preview-card{background:var(--card);border-radius:var(--r);overflow:hidden;
  margin-bottom:20px;border:1px solid var(--border);animation:slideUp .4s ease}
.thumb-wrap{position:relative;width:100%;padding-top:56.25%;background:var(--bg2);overflow:hidden}
.thumb-wrap img{position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover}
.dur-badge{position:absolute;bottom:8px;right:8px;background:rgba(0,0,0,.85);
  color:#fff;padding:3px 8px;border-radius:4px;font-size:12px;font-weight:700;
  letter-spacing:.3px}
.preview-info{padding:14px 16px}
.preview-info h3{font-size:16px;font-weight:700;line-height:1.3;
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;
  margin-bottom:4px}
.preview-info p{font-size:13px;color:var(--t2)}

/* Mode Tabs */
.mode-section{margin-bottom:16px}
.mode-tabs{display:flex;background:var(--card);border-radius:var(--rs);padding:3px;position:relative}
.mode-tab{flex:1;padding:10px;text-align:center;cursor:pointer;z-index:1;position:relative;
  transition:color .3s;border-radius:8px;border:none;background:none;
  color:var(--t2);font-size:14px;font-weight:600;display:flex;align-items:center;
  justify-content:center;gap:6px}
.mode-tab.active{color:#fff}
.mode-ind{position:absolute;top:3px;left:3px;width:calc(50% - 3px);height:calc(100% - 6px);
  background:var(--grad);border-radius:8px;transition:transform .3s ease}
.mode-ind.right{transform:translateX(100%)}

/* Audio Presets */
.preset-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.preset-card{background:var(--card);border:1.5px solid var(--border);border-radius:var(--rs);
  padding:16px 12px;text-align:center;cursor:pointer;transition:.2s;position:relative;overflow:hidden}
.preset-card:active{transform:scale(.96)}
.preset-card.selected{border-color:var(--accent);
  background:linear-gradient(135deg,rgba(102,126,234,.12),rgba(118,75,162,.12));
  box-shadow:0 0 20px rgba(102,126,234,.15)}
.preset-card .p-bitrate{font-size:22px;font-weight:800;margin-bottom:2px;
  background:var(--grad);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.preset-card .p-label{font-size:12px;color:var(--t2);margin-bottom:6px}
.preset-card .p-detail{font-size:11px;color:var(--t3)}
.preset-card.selected .p-label{color:var(--accent2)}
.preset-card .p-check{position:absolute;top:8px;right:8px;width:18px;height:18px;
  border-radius:50%;background:var(--grad);display:none;align-items:center;justify-content:center}
.preset-card.selected .p-check{display:flex}
.preset-card .p-check svg{width:12px;height:12px;color:#fff}

/* Video Formats */
.fmt-list{display:flex;flex-direction:column;gap:8px}
.fmt-row{display:flex;align-items:center;gap:12px;background:var(--card);
  border:1.5px solid var(--border);border-radius:var(--rs);padding:12px 14px;
  cursor:pointer;transition:.2s}
.fmt-row:active{transform:scale(.98)}
.fmt-row.selected{border-color:var(--accent);
  background:linear-gradient(135deg,rgba(102,126,234,.12),rgba(118,75,162,.12))}
.fmt-res{font-size:16px;font-weight:800;min-width:60px;
  background:var(--grad);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.fmt-meta{flex:1;display:flex;flex-direction:column;gap:2px}
.fmt-meta span{font-size:12px;color:var(--t2)}
.fmt-meta .fmt-codec{color:var(--t3)}
.fmt-badge{font-size:10px;font-weight:700;padding:3px 8px;border-radius:4px;
  background:rgba(102,126,234,.15);color:var(--accent2);text-transform:uppercase}
.fmt-row.selected .fmt-badge{background:var(--accent);color:#fff}

/* Download Button */
.dl-section{margin-top:20px}
.btn-dl{width:100%;padding:16px;border:none;border-radius:var(--rs);background:var(--grad);
  color:#fff;font-size:16px;font-weight:700;cursor:pointer;display:flex;align-items:center;
  justify-content:center;gap:8px;transition:.2s;letter-spacing:.3px;position:relative;overflow:hidden}
.btn-dl:active{transform:scale(.97)}
.btn-dl:disabled{opacity:.5;cursor:not-allowed;transform:none}
.btn-dl.pulsing::after{content:'';position:absolute;inset:0;border-radius:inherit;
  animation:ripple 2s infinite;border:2px solid rgba(255,255,255,.3)}

/* Progress */
.progress-card{background:var(--card);border-radius:var(--rs);padding:16px;
  border:1px solid var(--border);margin-top:16px;animation:slideUp .3s ease}
.progress-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}
.progress-head .p-status{font-size:13px;font-weight:600;color:var(--t2)}
.progress-head .p-pct{font-size:14px;font-weight:800;color:var(--accent2)}
.progress-bar{height:6px;border-radius:3px;background:var(--bg2);overflow:hidden}
.progress-fill{height:100%;border-radius:3px;background:var(--grad-h);
  transition:width .5s ease;width:0}
.progress-fill.complete{background:linear-gradient(90deg,var(--green),#00bfa5)}
.progress-fill.failed{background:linear-gradient(90deg,var(--red),#ee5a24)}

/* Downloads Page */
.page-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px}
.page-head h2{font-size:22px;font-weight:800}
.dl-item{display:flex;align-items:center;gap:12px;background:var(--card);
  border:1px solid var(--border);border-radius:var(--rs);padding:14px;margin-bottom:10px;
  animation:fadeIn .3s ease;transition:.2s}
.dl-item:active{background:var(--card2)}
.dl-icon{width:42px;height:42px;border-radius:var(--rx);display:flex;align-items:center;
  justify-content:center;flex-shrink:0}
.dl-icon.audio{background:linear-gradient(135deg,rgba(102,126,234,.2),rgba(118,75,162,.2));color:var(--accent2)}
.dl-icon.video{background:linear-gradient(135deg,rgba(0,230,118,.15),rgba(0,191,165,.15));color:var(--green)}
.dl-icon svg{width:20px;height:20px}
.dl-info{flex:1;min-width:0}
.dl-info h4{font-size:14px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.dl-info p{font-size:12px;color:var(--t2);margin-top:2px}
.dl-info .dl-progress{margin-top:8px}
.dl-info .dl-progress .progress-bar{height:4px}
.dl-actions{display:flex;gap:6px;flex-shrink:0}
.dl-btn{width:38px;height:38px;border:none;border-radius:var(--rx);cursor:pointer;
  display:flex;align-items:center;justify-content:center;transition:.2s}
.dl-btn:active{transform:scale(.9)}
.dl-btn.dl-get{background:var(--grad);color:#fff}
.dl-btn.dl-del{background:rgba(255,82,82,.12);color:var(--red)}
.dl-btn svg{width:16px;height:16px}
.status-dot{display:inline-block;width:6px;height:6px;border-radius:50%;margin-right:4px}
.status-dot.queued{background:var(--t3)}
.status-dot.downloading{background:var(--blue);animation:pulse 1.5s infinite}
.status-dot.processing{background:var(--yellow);animation:pulse 1.5s infinite}
.status-dot.completed{background:var(--green)}
.status-dot.failed{background:var(--red)}

/* Empty State */
.empty-state{text-align:center;padding:60px 20px;color:var(--t3)}
.empty-state .empty-ic{width:72px;height:72px;margin:0 auto 16px;opacity:.3}
.empty-state h3{font-size:16px;color:var(--t2);margin-bottom:6px;font-weight:600}
.empty-state p{font-size:13px}

/* Bottom Nav */
#nav{display:flex;background:rgba(10,10,26,.95);backdrop-filter:blur(20px);
  -webkit-backdrop-filter:blur(20px);border-top:1px solid var(--border);
  padding:6px 0 env(safe-area-inset-bottom,8px);z-index:10}
.nav-btn{flex:1;border:none;background:none;color:var(--t3);cursor:pointer;
  display:flex;flex-direction:column;align-items:center;gap:3px;padding:8px 0;
  transition:.2s;font-size:11px;font-weight:600}
.nav-btn svg{width:22px;height:22px;transition:.2s}
.nav-btn.active{color:var(--accent2)}
.nav-btn.active svg{transform:scale(1.1)}
.nav-btn:active{transform:scale(.92)}

/* Toast */
#toasts{position:fixed;top:16px;left:50%;transform:translateX(-50%);z-index:999;
  display:flex;flex-direction:column;gap:8px;max-width:400px;width:calc(100% - 32px)}
.toast{padding:12px 16px;border-radius:var(--rs);font-size:13px;font-weight:600;
  display:flex;align-items:center;gap:8px;animation:toastIn .3s ease;
  backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px)}
.toast.success{background:rgba(0,230,118,.15);color:var(--green);border:1px solid rgba(0,230,118,.2)}
.toast.error{background:rgba(255,82,82,.15);color:var(--red);border:1px solid rgba(255,82,82,.2)}
.toast.info{background:rgba(68,138,255,.15);color:var(--blue);border:1px solid rgba(68,138,255,.2)}
.toast.out{animation:toastOut .3s ease forwards}

/* Footer */
.footer{text-align:center;padding:24px 0 8px;font-size:11px;color:var(--t3)}
.footer a{color:var(--accent2);text-decoration:none}

/* Animations */
@keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
@keyframes slideUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
@keyframes shimmer{0%{background-position:200% 0}100%{background-position:-200% 0}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
@keyframes ripple{0%{transform:scale(1);opacity:.6}100%{transform:scale(1.5);opacity:0}}
@keyframes toastIn{from{opacity:0;transform:translateY(-20px)}to{opacity:1;transform:translateY(0)}}
@keyframes toastOut{from{opacity:1;transform:translateY(0)}to{opacity:0;transform:translateY(-20px)}}
@keyframes spin{from{transform:rotate(0)}to{transform:rotate(360deg)}}
.spinner{animation:spin 1s linear infinite}

/* Responsive */
@media(min-width:768px){#app{max-width:520px;border-left:1px solid var(--border);border-right:1px solid var(--border)}}
</style>
</head>
<body>
<div id="app">

<!-- Header -->
<header>
  <div class="h-left">
    <span class="logo">&#x1f3b5;</span>
    <span class="app-name">YTDLP</span>
  </div>
  <a href="/api/docs" class="h-right" title="API Docs">
    <span class="ic ic-sm"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg></span>
  </a>
</header>

<!-- Main -->
<main>

<!-- Home Page -->
<section id="page-home" class="page active">

  <!-- URL Input -->
  <div class="input-section">
    <div class="input-row">
      <input type="url" id="url-input" placeholder="Paste video URL here..." autocomplete="off" spellcheck="false">
      <button class="btn-icon" id="btn-paste" title="Paste">
        <span class="ic ic-sm"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg></span>
      </button>
      <button class="btn-icon" id="btn-clear" title="Clear" style="display:none">
        <span class="ic ic-sm"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></span>
      </button>
    </div>
    <button class="btn-fetch" id="btn-fetch" disabled>
      <span class="ic ic-sm"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg></span>
      Fetch Info
    </button>
  </div>

  <!-- Loading Skeleton -->
  <div id="loading-skeleton" style="display:none">
    <div class="skeleton skel-thumb"></div>
    <div class="skeleton skel-line w80"></div>
    <div class="skeleton skel-line w60"></div>
  </div>

  <!-- Preview Card -->
  <div id="preview" class="preview-card" style="display:none">
    <div class="thumb-wrap">
      <img id="thumb-img" src="" alt="">
      <span id="dur-badge" class="dur-badge"></span>
    </div>
    <div class="preview-info">
      <h3 id="preview-title"></h3>
      <p id="preview-artist"></p>
    </div>
  </div>

  <!-- Mode Tabs -->
  <div id="mode-section" class="mode-section" style="display:none">
    <div class="mode-tabs">
      <div class="mode-ind" id="mode-ind"></div>
      <button class="mode-tab active" data-mode="audio">
        <span class="ic ic-sm"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg></span>
        Audio
      </button>
      <button class="mode-tab" data-mode="video">
        <span class="ic ic-sm"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2"/></svg></span>
        Video
      </button>
    </div>
  </div>

  <!-- Audio Options -->
  <div id="audio-options" style="display:none">
    <div class="preset-grid" id="preset-grid"></div>
  </div>

  <!-- Video Options -->
  <div id="video-options" style="display:none">
    <div class="fmt-list" id="fmt-list"></div>
    <div id="fmt-empty" style="display:none" class="empty-state">
      <h3>No video formats found</h3>
      <p>Try downloading as audio instead</p>
    </div>
  </div>

  <!-- Download Button -->
  <div id="dl-section" class="dl-section" style="display:none">
    <button class="btn-dl" id="btn-dl">
      <span class="ic ic-sm"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg></span>
      Download
    </button>
  </div>

  <!-- Progress -->
  <div id="progress-section" style="display:none">
    <div class="progress-card">
      <div class="progress-head">
        <span class="p-status" id="p-status">Preparing...</span>
        <span class="p-pct" id="p-pct">0%</span>
      </div>
      <div class="progress-bar"><div class="progress-fill" id="p-fill"></div></div>
    </div>
  </div>

  <!-- Empty Home State -->
  <div id="home-empty" class="empty-state">
    <div class="empty-ic ic ic-xl">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
    </div>
    <h3>Paste a video URL</h3>
    <p>Supports YouTube, SoundCloud, Twitter, and 1000+ sites</p>
  </div>

  <div class="footer">Powered by <a href="/api/docs">yt-dlp</a></div>
</section>

<!-- Downloads Page -->
<section id="page-downloads" class="page">
  <div class="page-head">
    <h2>Downloads</h2>
    <button class="btn-icon" id="btn-refresh" title="Refresh">
      <span class="ic ic-sm"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg></span>
    </button>
  </div>
  <div id="dl-list"></div>
  <div id="dl-empty" class="empty-state">
    <div class="empty-ic ic ic-xl">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
    </div>
    <h3>No downloads yet</h3>
    <p>Go to Home and paste a URL</p>
  </div>
</section>

</main>

<!-- Bottom Nav -->
<nav id="nav">
  <button class="nav-btn active" data-tab="home">
    <span class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg></span>
    <span>Home</span>
  </button>
  <button class="nav-btn" data-tab="downloads">
    <span class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg></span>
    <span>Downloads</span>
  </button>
</nav>

<!-- Toasts -->
<div id="toasts"></div>

</div>

<script>
// State
var S = {
  tab:'home', mode:'audio', url:'', info:null, loading:false,
  preset:'128k', fmtId:null, fmts:[], task:null,
};
var polls = {};

// DOM
var urlInput = document.getElementById('url-input');
var btnPaste = document.getElementById('btn-paste');
var btnClear = document.getElementById('btn-clear');
var btnFetch = document.getElementById('btn-fetch');
var skel = document.getElementById('loading-skeleton');
var preview = document.getElementById('preview');
var modeSec = document.getElementById('mode-section');
var audioOpt = document.getElementById('audio-options');
var videoOpt = document.getElementById('video-options');
var dlSec = document.getElementById('dl-section');
var btnDl = document.getElementById('btn-dl');
var progSec = document.getElementById('progress-section');
var homeEmpty = document.getElementById('home-empty');

// API
var API = {
  info: function(url){
    return fetch('/api/video/info?url='+encodeURIComponent(url)+'&include_raw=false')
      .then(function(r){if(!r.ok) return r.json().then(function(e){throw new Error(e.detail||'Fetch failed')}); return r.json();});
  },
  audio: function(url,preset){
    return fetch('/api/audio',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url:url,preset:preset})})
      .then(function(r){if(!r.ok) return r.json().then(function(e){throw new Error(e.detail||'Start failed')}); return r.json();});
  },
  video: function(url,format_id){
    var b = {url:url}; if(format_id) b.format_id = format_id;
    return fetch('/api/video',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b)})
      .then(function(r){if(!r.ok) return r.json().then(function(e){throw new Error(e.detail||'Start failed')}); return r.json();});
  },
  status: function(type,id){
    return fetch('/api/'+type+'/'+id+'/status').then(function(r){if(!r.ok) throw new Error('Status failed'); return r.json();});
  },
  tasks: function(){
    return fetch('/api/tasks').then(function(r){if(!r.ok) throw new Error('Tasks failed'); return r.json();});
  },
  del: function(type,id){
    return fetch('/api/'+type+'/'+id,{method:'DELETE'}).then(function(r){if(!r.ok) throw new Error('Delete failed'); return r.json();});
  }
};

// Render
function renderPresets(){
  var presets = [
    {id:'48k',label:'Low',sr:'22.0kHz',ch:'Mono'},
    {id:'64k',label:'Medium',sr:'22.0kHz',ch:'Mono'},
    {id:'128k',label:'HQ',sr:'44.1kHz',ch:'Stereo'},
    {id:'320k',label:'Best',sr:'48kHz',ch:'Stereo'},
  ];
  document.getElementById('preset-grid').innerHTML = presets.map(function(p){
    return '<div class="preset-card'+(S.preset===p.id?' selected':'')+'" data-preset="'+p.id+'">'+
      '<div class="p-check"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg></div>'+
      '<div class="p-bitrate">'+p.id+'</div>'+
      '<div class="p-label">'+p.label+'</div>'+
      '<div class="p-detail">'+p.sr+' &middot; '+p.ch+'</div></div>';
  }).join('');
  document.querySelectorAll('.preset-card').forEach(function(el){
    el.addEventListener('click', function(){ S.preset=el.dataset.preset; renderPresets(); });
  });
}

function processFormats(formats){
  var video = formats.filter(function(f){return f.vcodec && f.vcodec!=='none';});
  var only = video.filter(function(f){return !f.acodec||f.acodec==='none';});
  var src = only.length>0?only:video;
  var byH = {};
  src.forEach(function(f){
    var h = parseInt(f.resolution)||0;
    if(!h) return;
    if(!byH[h]||(f.tbr||0)>(byH[h].tbr||0)) byH[h]=f;
  });
  return Object.values(byH).sort(function(a,b){return (parseInt(b.resolution)||0)-(parseInt(a.resolution)||0);});
}

function renderFormats(){
  var fmts = S.fmts;
  var list = document.getElementById('fmt-list');
  var empty = document.getElementById('fmt-empty');
  if(!fmts.length){ list.innerHTML=''; empty.style.display='block'; return; }
  empty.style.display='none';
  list.innerHTML = fmts.map(function(f){
    var res = f.resolution||'?';
    var ext = f.ext||'';
    var codec = f.vcodec?f.vcodec.split('.')[0].substring(0,6):'';
    var tbr = f.tbr?Math.round(f.tbr)+'kbps':'';
    var size = f.filesize?fmtSize(f.filesize):'';
    return '<div class="fmt-row'+(S.fmtId===f.format_id?' selected':'')+'" data-fid="'+f.format_id+'">'+
      '<div class="fmt-res">'+res+'p</div>'+
      '<div class="fmt-meta"><span>'+ext.toUpperCase()+(tbr?' &middot; '+tbr:'')+(size?' &middot; '+size:'')+'</span>'+
      '<span class="fmt-codec">'+codec+'</span></div>'+
      '<span class="fmt-badge">'+ext+'</span></div>';
  }).join('');
  document.querySelectorAll('.fmt-row').forEach(function(el){
    el.addEventListener('click', function(){ S.fmtId=el.dataset.fid; renderFormats(); });
  });
}

function renderDownloads(tasks){
  var list = document.getElementById('dl-list');
  var empty = document.getElementById('dl-empty');
  if(!tasks.length){ list.innerHTML=''; empty.style.display='block'; return; }
  empty.style.display='none';
  list.innerHTML = tasks.map(function(t){
    var isAudio = t.type==='audio';
    var iconSvg = isAudio
      ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>'
      : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2"/></svg>';
    var statusLabel = {queued:'Queued',downloading:'Downloading',processing:'Processing',completed:'Done',failed:'Failed'}[t.status]||t.status;
    var sub = [t.preset||t.format_id, t.file_size?fmtSize(t.file_size):'', statusLabel].filter(Boolean).join(' &middot; ');
    var dot = '<span class="status-dot '+t.status+'"></span>';
    var actions = '';
    if(t.status==='completed'){
      actions += '<button class="dl-btn dl-get" data-type="'+t.type+'" data-id="'+t.task_id+'" data-fname="'+escAttr(t.filename||'')+'" title="Download"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg></button>';
    }
    actions += '<button class="dl-btn dl-del" data-type="'+t.type+'" data-id="'+t.task_id+'" title="Delete"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg></button>';
    var prog = (t.status==='downloading'||t.status==='processing')
      ? '<div class="dl-progress"><div class="progress-bar"><div class="progress-fill" style="width:'+t.progress+'%"></div></div></div>' : '';
    var err = t.error ? '<p style="color:var(--red);font-size:11px;margin-top:2px">'+escHtml(t.error.substring(0,80))+'</p>' : '';
    return '<div class="dl-item" data-id="'+t.task_id+'">'+
      '<div class="dl-icon '+(isAudio?'audio':'video')+'">'+iconSvg+'</div>'+
      '<div class="dl-info"><h4>'+escHtml(t.title||t.task_id)+'</h4>'+
      '<p>'+dot+sub+'</p>'+prog+err+'</div>'+
      '<div class="dl-actions">'+actions+'</div></div>';
  }).join('');

  // Force download using <a download> trick
  list.querySelectorAll('.dl-get').forEach(function(b){
    b.addEventListener('click', function(){
      var url = '/api/'+b.dataset.type+'/'+b.dataset.id+'/download';
      var fname = b.dataset.fname || (b.dataset.id + (b.dataset.type==='audio'?'.mp3':'.mp4'));
      var a = document.createElement('a');
      a.href = url;
      a.download = fname;
      a.style.display = 'none';
      document.body.appendChild(a);
      a.click();
      setTimeout(function(){ document.body.removeChild(a); }, 1000);
      toast('Downloading to your device...','success');
    });
  });

  list.querySelectorAll('.dl-del').forEach(function(b){
    b.addEventListener('click', function(){
      API.del(b.dataset.type, b.dataset.id).then(function(){
        toast('Deleted','info'); loadDownloads();
      }).catch(function(){ toast('Delete failed','error'); });
    });
  });
}

// Actions
function handleFetch(){
  var url = urlInput.value.trim();
  if(!url) return;
  S.url=url; S.info=null; S.fmts=[]; S.fmtId=null; S.task=null;
  S.loading=true;
  updateUI();
  API.info(url).then(function(info){
    S.info=info;
    S.fmts=processFormats(info.formats||[]);
    S.fmtId=S.fmts.length?S.fmts[0].format_id:null;
    S.loading=false;
    updateUI();
  }).catch(function(e){
    S.loading=false;
    updateUI();
    toast(e.message||'Failed to fetch info','error');
  });
}

function handleDownload(){
  if(!S.url) return;
  btnDl.disabled=true;
  btnDl.classList.add('pulsing');
  var p;
  if(S.mode==='audio'){
    p = API.audio(S.url, S.preset);
  } else {
    p = API.video(S.url, S.fmtId||null);
  }
  p.then(function(res){
    S.task = {id:res.task_id, type:S.mode};
    startPoll(res.task_id, S.mode);
    progSec.style.display='block';
    dlSec.style.display='none';
    toast('Download started','info');
  }).catch(function(e){
    btnDl.disabled=false;
    btnDl.classList.remove('pulsing');
    toast(e.message||'Failed to start download','error');
  });
}

function updateUI(){
  var hasInfo = !!S.info;
  homeEmpty.style.display = hasInfo||S.loading?'none':'';
  skel.style.display = S.loading?'block':'none';
  preview.style.display = hasInfo?'block':'none';
  modeSec.style.display = hasInfo?'block':'none';
  audioOpt.style.display = hasInfo&&S.mode==='audio'?'block':'none';
  videoOpt.style.display = hasInfo&&S.mode==='video'?'block':'none';
  dlSec.style.display = hasInfo&&!S.task?'block':'none';
  progSec.style.display = S.task?'block':'none';
  if(hasInfo){
    document.getElementById('thumb-img').src = S.info.thumbnail||'';
    document.getElementById('preview-title').textContent = S.info.title||'Unknown';
    document.getElementById('preview-artist').textContent = [S.info.artist, S.info.duration?fmtDur(S.info.duration):''].filter(Boolean).join(' &middot; ');
    document.getElementById('dur-badge').textContent = S.info.duration?fmtDur(S.info.duration):'';
    renderPresets();
    renderFormats();
  }
  if(!S.task){ btnDl.disabled=false; btnDl.classList.remove('pulsing'); }
}

// Polling
function startPoll(id,type){
  if(polls[id]) return;
  polls[id] = setInterval(function(){
    API.status(type,id).then(function(s){
      updateProgress(s);
      if(s.status==='completed'){
        stopPoll(id);
        toast('Download complete!','success');
        btnDl.disabled=false; btnDl.classList.remove('pulsing');
        setTimeout(function(){ progSec.style.display='none'; S.task=null; dlSec.style.display='block'; },2000);
      } else if(s.status==='failed'){
        stopPoll(id);
        toast('Download failed: '+(s.error||'Unknown'),'error');
        btnDl.disabled=false; btnDl.classList.remove('pulsing');
        document.getElementById('p-fill').classList.add('failed');
      }
    }).catch(function(e){ console.error('poll err',e); });
  },1000);
}
function stopPoll(id){ if(polls[id]){clearInterval(polls[id]);delete polls[id];} }
function updateProgress(s){
  var labels={queued:'Queued...',downloading:'Downloading...',processing:'Processing...',completed:'Complete!',failed:'Failed'};
  document.getElementById('p-status').textContent = labels[s.status]||s.status;
  document.getElementById('p-pct').textContent = Math.round(s.progress)+'%';
  document.getElementById('p-fill').style.width = s.progress+'%';
  if(s.status==='completed') document.getElementById('p-fill').classList.add('complete');
}

// Downloads Page
function loadDownloads(){
  API.tasks().then(function(tasks){
    renderDownloads(tasks);
    tasks.forEach(function(t){
      if(t.status==='downloading'||t.status==='processing'||t.status==='queued'){
        if(!polls[t.task_id]) startPoll(t.task_id, t.type);
      }
    });
  }).catch(function(){ toast('Failed to load downloads','error'); });
}

// Navigation
function switchTab(tab){
  S.tab=tab;
  document.querySelectorAll('.page').forEach(function(p){p.classList.remove('active');});
  document.getElementById('page-'+tab).classList.add('active');
  document.querySelectorAll('.nav-btn').forEach(function(b){b.classList.toggle('active',b.dataset.tab===tab);});
  if(tab==='downloads') loadDownloads();
}
function switchMode(mode){
  S.mode=mode;
  document.querySelectorAll('.mode-tab').forEach(function(t){t.classList.toggle('active',t.dataset.mode===mode);});
  document.getElementById('mode-ind').classList.toggle('right',mode==='video');
  audioOpt.style.display = mode==='audio'?'block':'none';
  videoOpt.style.display = mode==='video'?'block':'none';
}

// Toast
function toast(msg,type){
  type=type||'info';
  var el = document.createElement('div');
  el.className = 'toast '+type;
  var icons={success:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="width:16px;height:16px"><polyline points="20 6 9 17 4 12"/></svg>',
    error:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="width:16px;height:16px"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
    info:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="width:16px;height:16px"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>'};
  el.innerHTML = (icons[type]||icons.info)+'<span>'+escHtml(msg)+'</span>';
  document.getElementById('toasts').appendChild(el);
  setTimeout(function(){el.classList.add('out');setTimeout(function(){el.remove();},300);},3000);
}

// Utils
function fmtSize(b){if(!b)return'';var u=['B','KB','MB','GB'];var i=0;while(b>=1024&&i<u.length-1){b/=1024;i++;}return b.toFixed(i?1:0)+u[i];}
function fmtDur(s){if(!s)return'';var m=Math.floor(s/60);var sec=Math.floor(s%60);return m+':'+(sec<10?'0':'')+sec;}
function escHtml(s){var d=document.createElement('div');d.textContent=s;return d.innerHTML;}
function escAttr(s){return s.replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/'/g,'&#39;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}

// Events
urlInput.addEventListener('input', function(){
  var v = urlInput.value.trim();
  btnFetch.disabled = !v;
  btnClear.style.display = v?'flex':'none';
});
btnPaste.addEventListener('click', function(){
  navigator.clipboard.readText().then(function(t){urlInput.value=t;urlInput.dispatchEvent(new Event('input'));}).catch(function(){toast('Cannot read clipboard','error');});
});
btnClear.addEventListener('click', function(){
  urlInput.value='';urlInput.dispatchEvent(new Event('input'));
  S.info=null;S.fmts=[];S.fmtId=null;S.task=null;S.url='';
  updateUI();
});
btnFetch.addEventListener('click', handleFetch);
btnDl.addEventListener('click', handleDownload);
document.querySelectorAll('.mode-tab').forEach(function(t){t.addEventListener('click',function(){switchMode(t.dataset.mode);});});
document.querySelectorAll('.nav-btn').forEach(function(b){b.addEventListener('click',function(){switchTab(b.dataset.tab);});});
document.getElementById('btn-refresh').addEventListener('click', loadDownloads);
urlInput.addEventListener('keydown',function(e){if(e.key==='Enter'&&urlInput.value.trim())handleFetch();});

// Init
updateUI();
</script>
</body>
</html>"""
