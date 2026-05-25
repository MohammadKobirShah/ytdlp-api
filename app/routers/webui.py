"""
Premium responsive WebUI with playlist, subtitle, and health support.
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["webui"])


@router.get("/", response_class=HTMLResponse)
async def webui():
    return _HTML


_HTML = r"""<!DOCTYPE html>
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
:root{--bg:#0a0a1a;--bg2:#0d0d24;--card:#14143a;--card2:#1c1c4a;--input:#12122e;--grad:linear-gradient(135deg,#667eea,#764ba2);--grad-h:linear-gradient(90deg,#667eea,#764ba2);--t1:#f0f0f5;--t2:#8888aa;--t3:#555577;--border:rgba(255,255,255,.06);--accent:#667eea;--accent2:#8b9cf7;--green:#00e676;--red:#ff5252;--yellow:#ffd740;--blue:#448aff;--orange:#ff9100;--r:16px;--rs:12px;--rx:8px;--head-h:56px;--safe-bottom:env(safe-area-inset-bottom,8px)}
*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{height:100%;overflow:hidden}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:var(--bg);color:var(--t1);-webkit-font-smoothing:antialiased}
#app{display:flex;flex-direction:column;height:100%;max-width:480px;margin:0 auto;position:relative;background:var(--bg2);box-shadow:0 0 60px rgba(0,0,0,.4)}
header{display:flex;align-items:center;justify-content:space-between;padding:8px 16px;height:var(--head-h);background:rgba(10,10,26,.92);backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);border-bottom:1px solid var(--border);z-index:20;position:sticky;top:0}
.h-left{display:flex;align-items:center;gap:10px}
.logo{width:32px;height:32px;border-radius:8px;background:var(--grad);display:flex;align-items:center;justify-content:center;font-size:18px;box-shadow:0 4px 12px rgba(102,126,234,.3)}
.app-name{font-size:18px;font-weight:800;background:var(--grad);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;letter-spacing:-.3px}
.h-right{display:flex;align-items:center;gap:2px}
.h-btn{color:var(--t2);text-decoration:none;padding:7px;border-radius:var(--rx);transition:.2s;background:none;border:none;cursor:pointer;display:flex;align-items:center;justify-content:center}
.h-btn:hover{background:var(--card);color:var(--t1)}
.h-btn svg{width:17px;height:17px}
main{flex:1;overflow-y:auto;overflow-x:hidden;-webkit-overflow-scrolling:touch;padding:16px 14px calc(16px + var(--safe-bottom));scroll-behavior:smooth}
.page{display:none;animation:fadeIn .35s ease}.page.active{display:block}
.ic{display:inline-flex;align-items:center;justify-content:center}
.ic svg{width:100%;height:100%}
.ic-sm{width:18px;height:18px}.ic-md{width:22px;height:22px}.ic-xl{width:64px;height:64px}
.input-section{margin-bottom:18px}
.input-row{display:flex;gap:8px;margin-bottom:10px}
.input-row input{flex:1;background:var(--input);border:1.5px solid var(--border);border-radius:var(--rs);padding:13px 16px;color:var(--t1);font-size:15px;outline:none;transition:border .25s,box-shadow .25s}
.input-row input:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(102,126,234,.1)}
.input-row input::placeholder{color:var(--t3)}
.btn-icon{width:46px;height:46px;border:none;border-radius:var(--rs);background:var(--card);color:var(--t2);cursor:pointer;display:flex;align-items:center;justify-content:center;transition:.2s;flex-shrink:0}
.btn-icon:active{transform:scale(.92);background:var(--card2)}
.btn-primary{width:100%;padding:14px;border:none;border-radius:var(--rs);background:var(--grad);color:#fff;font-size:15px;font-weight:700;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:8px;transition:.2s;letter-spacing:.2px;position:relative;overflow:hidden}
.btn-primary:disabled{opacity:.4;cursor:not-allowed;transform:none}
.btn-primary:not(:disabled):active{transform:scale(.97)}
.btn-primary.pulsing::after{content:'';position:absolute;inset:0;border-radius:inherit;animation:ripple 2s infinite;border:2px solid rgba(255,255,255,.25)}
.skeleton{background:linear-gradient(90deg,var(--card) 25%,var(--card2) 50%,var(--card) 75%);background-size:200% 100%;animation:shimmer 1.5s infinite;border-radius:8px}
.skel-thumb{width:100%;padding-top:56.25%;border-radius:var(--rs);margin-bottom:14px}
.skel-line{height:14px;border-radius:4px;margin-bottom:10px}
.skel-line.w80{width:80%}.skel-line.w60{width:60%}
.preview-card{background:var(--card);border-radius:var(--r);overflow:hidden;margin-bottom:18px;border:1px solid var(--border);animation:slideUp .4s ease}
.thumb-wrap{position:relative;width:100%;padding-top:56.25%;background:var(--bg2);overflow:hidden}
.thumb-wrap img{position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover}
.thumb-wrap .grad-overlay{position:absolute;bottom:0;left:0;right:0;height:50%;background:linear-gradient(transparent,rgba(0,0,0,.7))}
.dur-badge{position:absolute;bottom:10px;right:10px;background:rgba(0,0,0,.85);color:#fff;padding:3px 9px;border-radius:5px;font-size:12px;font-weight:700;letter-spacing:.3px;backdrop-filter:blur(4px)}
.preview-info{padding:14px 16px}
.preview-info h3{font-size:16px;font-weight:700;line-height:1.35;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;margin-bottom:4px}
.preview-info p{font-size:13px;color:var(--t2)}
.preview-badges{display:flex;gap:6px;margin-top:6px;flex-wrap:wrap}
.preview-badge{font-size:10px;font-weight:700;padding:3px 8px;border-radius:4px;background:rgba(102,126,234,.12);color:var(--accent2);text-transform:uppercase}
.playlist-card{background:var(--card);border-radius:var(--r);overflow:hidden;margin-bottom:18px;border:1px solid var(--border);animation:slideUp .4s ease}
.pl-header{display:flex;gap:14px;padding:16px;border-bottom:1px solid var(--border)}
.pl-thumb{width:80px;height:80px;border-radius:8px;object-fit:cover;flex-shrink:0}
.pl-info{flex:1;min-width:0}
.pl-info h3{font-size:16px;font-weight:700;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;margin-bottom:3px}
.pl-info p{font-size:12px;color:var(--t2)}
.pl-count{font-size:12px;color:var(--accent2);font-weight:600;margin-top:4px}
.pl-entry{display:flex;align-items:center;gap:10px;padding:10px 16px;border-bottom:1px solid var(--border);cursor:pointer;transition:.15s}
.pl-entry:last-child{border-bottom:none}
.pl-entry:hover{background:rgba(255,255,255,.02)}
.pl-entry:active{background:rgba(255,255,255,.04)}
.pl-entry .pl-idx{width:24px;font-size:12px;color:var(--t3);flex-shrink:0;text-align:center;font-weight:600}
.pl-entry .pl-e-thumb{width:40px;height:28px;border-radius:4px;object-fit:cover;flex-shrink:0;background:var(--bg2)}
.pl-entry .pl-e-info{flex:1;min-width:0}
.pl-entry .pl-e-info h4{font-size:13px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.pl-entry .pl-e-info span{font-size:11px;color:var(--t3)}
.pl-entry .pl-e-dur{font-size:11px;color:var(--t3);flex-shrink:0}
.pl-actions{display:flex;gap:8px;padding:12px 16px}
.pl-actions button{flex:1}
.mode-section{margin-bottom:16px}
.mode-tabs{display:flex;background:var(--card);border-radius:var(--rs);padding:3px;position:relative}
.mode-tab{flex:1;padding:10px;text-align:center;cursor:pointer;z-index:1;position:relative;transition:color .3s;border-radius:8px;border:none;background:none;color:var(--t2);font-size:13px;font-weight:600;display:flex;align-items:center;justify-content:center;gap:5px}
.mode-tab.active{color:#fff}
.mode-tab .mode-sub{font-size:10px;color:var(--t3);font-weight:400;display:none}
.mode-tab.active .mode-sub{color:rgba(255,255,255,.5)}
.mode-ind{position:absolute;top:3px;bottom:3px;left:3px;width:calc(25% - 3px);background:var(--grad);border-radius:8px;transition:transform .3s cubic-bezier(.4,0,.2,1)}
.mode-ind.a2{transform:translateX(100%)}.mode-ind.a3{transform:translateX(200%)}.mode-ind.a4{transform:translateX(300%)}
.preset-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.preset-card{background:var(--card);border:1.5px solid var(--border);border-radius:var(--rs);padding:14px 12px;text-align:center;cursor:pointer;transition:.2s;position:relative;overflow:hidden}
.preset-card:active{transform:scale(.96)}
.preset-card.selected{border-color:var(--accent);background:linear-gradient(135deg,rgba(102,126,234,.12),rgba(118,75,162,.12));box-shadow:0 0 24px rgba(102,126,234,.12)}
.preset-card .p-bitrate{font-size:20px;font-weight:800;margin-bottom:2px;background:var(--grad);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.preset-card .p-label{font-size:11px;color:var(--t2);margin-bottom:4px}
.preset-card .p-detail{font-size:10px;color:var(--t3)}
.preset-card.selected .p-label{color:var(--accent2)}
.preset-card .p-check{position:absolute;top:7px;right:7px;width:16px;height:16px;border-radius:50%;background:var(--grad);display:none;align-items:center;justify-content:center}
.preset-card.selected .p-check{display:flex}
.preset-card .p-check svg{width:10px;height:10px;color:#fff}
.fmt-list{display:flex;flex-direction:column;gap:7px}
.fmt-row{display:flex;align-items:center;gap:10px;background:var(--card);border:1.5px solid var(--border);border-radius:var(--rs);padding:11px 13px;cursor:pointer;transition:.2s}
.fmt-row:active{transform:scale(.98)}
.fmt-row.selected{border-color:var(--accent);background:linear-gradient(135deg,rgba(102,126,234,.12),rgba(118,75,162,.12))}
.fmt-res{font-size:15px;font-weight:800;min-width:56px;background:var(--grad);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.fmt-meta{flex:1;display:flex;flex-direction:column;gap:2px}
.fmt-meta span{font-size:11px;color:var(--t2)}
.fmt-meta .fmt-codec{color:var(--t3)}
.fmt-badge{font-size:9px;font-weight:700;padding:2px 7px;border-radius:4px;background:rgba(102,126,234,.12);color:var(--accent2);text-transform:uppercase}
.fmt-row.selected .fmt-badge{background:var(--accent);color:#fff}
.dl-section{margin-top:18px}
.btn-dl{width:100%;padding:15px;border:none;border-radius:var(--rs);background:var(--grad);color:#fff;font-size:16px;font-weight:700;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:8px;transition:.2s;letter-spacing:.2px;position:relative;overflow:hidden}
.btn-dl:active{transform:scale(.97)}
.btn-dl:disabled{opacity:.5;cursor:not-allowed;transform:none}
.btn-dl.pulsing::after{content:'';position:absolute;inset:0;border-radius:inherit;animation:ripple 2s infinite;border:2px solid rgba(255,255,255,.25)}
.sub-opts{display:flex;gap:8px;margin-top:12px}
.sub-opts select{flex:1;background:var(--card);border:1.5px solid var(--border);border-radius:var(--rs);padding:10px 12px;color:var(--t1);font-size:13px;outline:none;cursor:pointer}
.sub-opts select:focus{border-color:var(--accent)}
.progress-card{background:var(--card);border-radius:var(--rs);padding:16px 18px;border:1px solid var(--border);margin-top:16px;animation:slideUp .3s ease}
.progress-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}
.progress-head .p-status{font-size:13px;font-weight:600;color:var(--t2)}
.progress-head .p-pct{font-size:14px;font-weight:800;color:var(--accent2)}
.progress-bar{height:6px;border-radius:3px;background:var(--bg2);overflow:hidden}
.progress-fill{height:100%;border-radius:3px;background:var(--grad-h);transition:width .5s ease;width:0}
.progress-fill.complete{background:linear-gradient(90deg,var(--green),#00bfa5)}
.progress-fill.failed{background:linear-gradient(90deg,var(--red),#ee5a24)}
.page-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}
.page-head h2{font-size:20px;font-weight:800}
.page-filters{display:flex;gap:6px;margin-bottom:14px;overflow-x:auto;padding-bottom:4px}
.filter-btn{padding:6px 14px;border:1.5px solid var(--border);border-radius:20px;background:var(--card);color:var(--t2);font-size:12px;font-weight:600;cursor:pointer;white-space:nowrap;transition:.2s}
.filter-btn.active{background:var(--grad);color:#fff;border-color:transparent}
.filter-btn:active{transform:scale(.95)}
.dl-item{display:flex;align-items:center;gap:10px;background:var(--card);border:1px solid var(--border);border-radius:var(--rs);padding:12px 14px;margin-bottom:8px;animation:fadeIn .3s ease;transition:.2s}
.dl-item:active{background:var(--card2)}
.dl-icon{width:40px;height:40px;border-radius:6px;display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:18px}
.dl-icon.audio{background:linear-gradient(135deg,rgba(102,126,234,.2),rgba(118,75,162,.2));color:var(--accent2)}
.dl-icon.video{background:linear-gradient(135deg,rgba(0,230,118,.15),rgba(0,191,165,.15));color:var(--green)}
.dl-icon.subtitle{background:linear-gradient(135deg,rgba(255,215,64,.15),rgba(255,152,0,.15));color:var(--yellow)}
.dl-icon.playlist{background:linear-gradient(135deg,rgba(255,145,0,.15),rgba(255,87,34,.15));color:var(--orange)}
.dl-info{flex:1;min-width:0}
.dl-info h4{font-size:14px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.dl-info p{font-size:11px;color:var(--t2);margin-top:1px}
.dl-info .dl-progress{margin-top:7px}
.dl-info .dl-progress .progress-bar{height:4px}
.dl-actions{display:flex;gap:5px;flex-shrink:0}
.dl-btn{width:36px;height:36px;border:none;border-radius:6px;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:.2s}
.dl-btn:active{transform:scale(.88)}
.dl-btn.dl-get{background:var(--grad);color:#fff}
.dl-btn.dl-del{background:rgba(255,82,82,.1);color:var(--red)}
.dl-btn svg{width:15px;height:15px}
.status-dot{display:inline-block;width:6px;height:6px;border-radius:50%;margin-right:4px}
.status-dot.queued{background:var(--t3)}
.status-dot.downloading{background:var(--blue);animation:pulse 1.5s infinite}
.status-dot.processing{background:var(--yellow);animation:pulse 1.5s infinite}
.status-dot.completed{background:var(--green)}
.status-dot.failed{background:var(--red)}
.dl-entries{font-size:11px;color:var(--accent2);font-weight:600}
.empty-state{text-align:center;padding:50px 20px;color:var(--t3)}
.empty-state .empty-ic{width:64px;height:64px;margin:0 auto 14px;opacity:.25}
.empty-state h3{font-size:15px;color:var(--t2);margin-bottom:4px;font-weight:600}
.empty-state p{font-size:12px}
.health-grid{display:flex;flex-direction:column;gap:10px}
.health-card{background:var(--card);border:1px solid var(--border);border-radius:var(--rs);padding:14px 16px;display:flex;align-items:center;gap:12px;animation:fadeIn .3s ease}
.health-dot{width:10px;height:10px;border-radius:50%;flex-shrink:0}
.health-dot.ok{background:var(--green);box-shadow:0 0 8px rgba(0,230,118,.3)}
.health-dot.warning{background:var(--yellow);box-shadow:0 0 8px rgba(255,215,64,.3)}
.health-dot.critical,.health-dot.not_found,.health-dot.error{background:var(--red);box-shadow:0 0 8px rgba(255,82,82,.3)}
.health-info{flex:1;min-width:0}
.health-info h4{font-size:14px;font-weight:700;text-transform:capitalize}
.health-info p{font-size:11px;color:var(--t2);margin-top:1px}
.health-info .health-version{font-size:10px;color:var(--t3);font-family:monospace}
.health-bar-wrap{background:var(--bg2);border-radius:4px;height:8px;overflow:hidden;margin:8px 0 2px;width:100%}
.health-bar{height:100%;border-radius:4px;background:var(--grad-h);transition:width .8s ease}
.health-bar.warn{background:linear-gradient(90deg,var(--yellow),var(--orange))}
.health-bar.crit{background:linear-gradient(90deg,var(--red),#ee5a24)}
.health-footer{margin-top:14px;text-align:center;font-size:12px;color:var(--t3)}
.health-footer a{color:var(--accent2);text-decoration:none}
.check-row{display:flex;align-items:center;gap:8px;margin-top:10px;padding:0 2px}
.check-row input[type=checkbox]{width:16px;height:16px;accent-color:var(--accent);cursor:pointer}
.check-row label{font-size:12px;color:var(--t2);cursor:pointer;user-select:none}
.url-history{background:var(--card);border:1px solid var(--border);border-radius:var(--rs);margin-top:-8px;margin-bottom:10px;overflow:hidden;animation:fadeIn .15s ease;display:none}
.url-history.show{display:block}
.url-h-item{padding:10px 14px;font-size:13px;color:var(--t2);cursor:pointer;border-bottom:1px solid var(--border);transition:.1s;display:flex;align-items:center;gap:8px}
.url-h-item:last-child{border:none}
.url-h-item:hover{background:rgba(255,255,255,.03);color:var(--t1)}
.url-h-item .h-del{margin-left:auto;color:var(--t3);padding:2px;border-radius:4px;cursor:pointer}
.url-h-item .h-del:hover{color:var(--red)}
#nav{display:flex;background:rgba(10,10,26,.92);backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);border-top:1px solid var(--border);padding:4px 0 var(--safe-bottom);z-index:20}
.nav-btn{flex:1;border:none;background:none;color:var(--t3);cursor:pointer;display:flex;flex-direction:column;align-items:center;gap:2px;padding:6px 0;transition:.2s;font-size:10px;font-weight:600}
.nav-btn svg{width:20px;height:20px;transition:.2s}
.nav-btn.active{color:var(--accent2)}.nav-btn.active svg{transform:scale(1.1)}
.nav-btn:active{transform:scale(.92)}
#toasts{position:fixed;top:12px;left:50%;transform:translateX(-50%);z-index:999;display:flex;flex-direction:column;gap:8px;max-width:380px;width:calc(100% - 24px);pointer-events:none}
.toast{padding:11px 15px;border-radius:var(--rx);font-size:13px;font-weight:600;display:flex;align-items:center;gap:8px;animation:toastIn .3s ease;backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);pointer-events:auto}
.toast.success{background:rgba(0,230,118,.12);color:var(--green);border:1px solid rgba(0,230,118,.15)}
.toast.error{background:rgba(255,82,82,.12);color:var(--red);border:1px solid rgba(255,82,82,.15)}
.toast.info{background:rgba(68,138,255,.12);color:var(--blue);border:1px solid rgba(68,138,255,.15)}
.toast.out{animation:toastOut .3s ease forwards}
.toast .toast-bar{position:absolute;bottom:0;left:0;height:2px;border-radius:0 0 var(--rx) var(--rx);animation:toastBar 3s linear forwards}
.toast.success .toast-bar{background:var(--green)}
.toast.error .toast-bar{background:var(--red)}
.toast.info .toast-bar{background:var(--blue)}
.cookie-ind{width:8px;height:8px;border-radius:50%;display:inline-block;margin-left:4px}
.cookie-ind.on{background:var(--green);box-shadow:0 0 6px rgba(0,230,118,.3)}
.cookie-ind.off{background:var(--t3)}
@keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
@keyframes slideUp{from{opacity:0;transform:translateY(24px)}to{opacity:1;transform:translateY(0)}}
@keyframes shimmer{0%{background-position:200% 0}100%{background-position:-200% 0}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.35}}
@keyframes ripple{0%{transform:scale(1);opacity:.5}100%{transform:scale(1.6);opacity:0}}
@keyframes toastIn{from{opacity:0;transform:translateY(-16px)}to{opacity:1;transform:translateY(0)}}
@keyframes toastOut{from{opacity:1;transform:translateY(0)}to{opacity:0;transform:translateY(-16px)}}
@keyframes toastBar{from{width:100%}to{width:0%}}
@keyframes spin{to{transform:rotate(360deg)}}
@media(min-width:768px){
  #app{max-width:860px;border-left:1px solid var(--border);border-right:1px solid var(--border)}
  main{padding:20px 20px calc(20px + var(--safe-bottom))}
  .home-grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}
  .home-col-left,.home-col-right{min-width:0}
  .input-row input{padding:14px 18px;font-size:16px}
  .mode-tab{padding:12px;font-size:14px}
  .mode-tab .mode-sub{display:inline}
  .preset-grid{grid-template-columns:repeat(4,1fr)}
  .pl-thumb{width:100px;height:100px}
}
</style>
</head>
<body>
<div id="app">
<header>
  <div class="h-left">
    <div class="logo">&#x1f3b5;</div>
    <span class="app-name">YTDLP</span>
    <span id="cookie-ind" class="cookie-ind off"></span>
  </div>
  <div class="h-right">
    <button class="h-btn" id="btn-cookies" title="Upload cookies.txt">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2zm0 14v-4m0-4h.01"/></svg>
    </button>
    <a href="/api/docs" class="h-btn" title="API Docs">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
    </a>
  </div>
  <input type="file" id="cookie-file" accept=".txt,.cookies" style="display:none">
</header>
<main>
<section id="page-home" class="page active">
<div class="home-grid">
<div class="home-col-left">
  <div class="input-section">
    <div class="input-row">
      <input type="url" id="url-input" placeholder="Paste URL here..." autocomplete="off" spellcheck="false">
      <button class="btn-icon" id="btn-paste" title="Paste"><span class="ic ic-sm"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg></span></button>
      <button class="btn-icon" id="btn-clear" title="Clear" style="display:none"><span class="ic ic-sm"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></span></button>
    </div>
    <div class="url-history" id="url-history"></div>
    <button class="btn-primary" id="btn-fetch" disabled><span class="ic ic-sm"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg></span> Fetch Info</button>
  </div>
  <div id="loading-skeleton" style="display:none">
    <div class="skeleton skel-thumb"></div>
    <div class="skeleton skel-line w80"></div>
    <div class="skeleton skel-line w60"></div>
  </div>
  <div id="preview" class="preview-card" style="display:none">
    <div class="thumb-wrap">
      <img id="thumb-img" src="" alt="">
      <div class="grad-overlay"></div>
      <span id="dur-badge" class="dur-badge"></span>
    </div>
    <div class="preview-info">
      <h3 id="preview-title"></h3>
      <p id="preview-artist"></p>
      <div class="preview-badges" id="preview-badges"></div>
    </div>
  </div>
  <div id="playlist-view" style="display:none">
    <div class="playlist-card">
      <div class="pl-header">
        <img class="pl-thumb" id="pl-thumb" src="" alt="">
        <div class="pl-info">
          <h3 id="pl-title"></h3>
          <p id="pl-uploader"></p>
          <div class="pl-count" id="pl-count"></div>
        </div>
      </div>
      <div id="pl-entries"></div>
      <div class="pl-actions">
        <button class="btn-primary" id="btn-pl-dl-all">Download All</button>
      </div>
    </div>
  </div>
</div>
<div class="home-col-right">
  <div id="mode-section" class="mode-section" style="display:none">
    <div class="mode-tabs">
      <div class="mode-ind" id="mode-ind"></div>
      <button class="mode-tab active" data-mode="audio"><span class="ic ic-sm"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg></span> Audio <span class="mode-sub">MP3</span></button>
      <button class="mode-tab" data-mode="video"><span class="ic ic-sm"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2"/></svg></span> Video <span class="mode-sub">MP4</span></button>
      <button class="mode-tab" data-mode="subtitle"><span class="ic ic-sm"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 7v10a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2z"/><line x1="6" y1="12" x2="8" y2="12"/><line x1="10" y1="12" x2="16" y2="12"/></svg></span> Subs <span class="mode-sub">VTT</span></button>
      <button class="mode-tab" data-mode="playlist"><span class="ic ic-sm"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h12M9 12h12M9 6h12"/><circle cx="4" cy="6" r="1"/><circle cx="4" cy="12" r="1"/><circle cx="4" cy="18" r="1"/></svg></span> Playlist <span class="mode-sub">Zip</span></button>
    </div>
  </div>
  <div id="audio-options" style="display:none"><div class="preset-grid" id="preset-grid"></div></div>
  <div id="video-options" style="display:none">
    <div class="fmt-list" id="fmt-list"></div>
    <div id="fmt-empty" style="display:none" class="empty-state"><h3>No video formats</h3><p>Try audio mode instead</p></div>
  </div>
  <div id="sub-options" style="display:none">
    <div class="sub-opts">
      <select id="sub-lang">
        <option value="en">English</option><option value="ar">Arabic</option><option value="de">German</option><option value="es">Spanish</option><option value="fr">French</option><option value="hi">Hindi</option><option value="id">Indonesian</option><option value="ja">Japanese</option><option value="ko">Korean</option><option value="pt">Portuguese</option><option value="ru">Russian</option><option value="tr">Turkish</option><option value="vi">Vietnamese</option><option value="zh">Chinese</option>
      </select>
      <select id="sub-fmt">
        <option value="vtt">VTT</option><option value="srt">SRT</option><option value="ass">ASS</option><option value="lrc">LRC</option>
      </select>
    </div>
  </div>
  <div id="pl-info" style="display:none">
    <div class="check-row">
      <input type="checkbox" id="pl-playlist-mode" checked>
      <label for="pl-playlist-mode">Download as playlist (zip archive)</label>
    </div>
  </div>
  <div id="dl-section" class="dl-section" style="display:none">
    <button class="btn-dl" id="btn-dl">
      <span class="ic ic-sm"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg></span>
      <span id="btn-dl-text">Download</span>
    </button>
  </div>
  <div id="progress-section" style="display:none">
    <div class="progress-card">
      <div class="progress-head">
        <span class="p-status" id="p-status">Preparing...</span>
        <span class="p-pct" id="p-pct">0%</span>
      </div>
      <div class="progress-bar"><div class="progress-fill" id="p-fill"></div></div>
    </div>
  </div>
  <div id="home-empty" class="empty-state">
    <div class="empty-ic ic ic-xl"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg></div>
    <h3>Paste a URL to start</h3>
    <p>YouTube, SoundCloud, Twitter, and 1000+ sites</p>
  </div>
</div>
</div>
</section>
<section id="page-downloads" class="page">
  <div class="page-head">
    <h2>Downloads</h2>
    <button class="btn-icon" id="btn-refresh" title="Refresh"><span class="ic ic-sm"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg></span></button>
  </div>
  <div class="page-filters" id="dl-filters">
    <button class="filter-btn active" data-filter="all">All</button>
    <button class="filter-btn" data-filter="audio">Audio</button>
    <button class="filter-btn" data-filter="video">Video</button>
    <button class="filter-btn" data-filter="subtitle">Subtitles</button>
    <button class="filter-btn" data-filter="completed">Done</button>
    <button class="filter-btn" data-filter="failed">Failed</button>
  </div>
  <div id="dl-list"></div>
  <div id="dl-empty" class="empty-state">
    <div class="empty-ic ic ic-xl"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg></div>
    <h3>No downloads yet</h3>
    <p>Go to Home and paste a URL</p>
  </div>
</section>
<section id="page-settings" class="page">
  <div class="page-head">
    <h2>System</h2>
    <button class="btn-icon" id="btn-health-refresh" title="Refresh"><span class="ic ic-sm"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg></span></button>
  </div>
  <div id="health-loading" class="empty-state">
    <div class="empty-ic ic ic-xl" style="animation:spin 1s linear infinite"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg></div>
    <h3>Loading system info...</h3>
  </div>
  <div class="health-grid" id="health-grid"></div>
  <div class="health-footer" id="health-footer"></div>
  <div style="margin-top:16px">
    <div class="health-card">
      <div class="health-info">
        <h4>Cookies</h4>
        <p id="health-cookie-status">Checking...</p>
      </div>
      <button class="dl-btn dl-get" id="health-cookie-upload" title="Upload cookies"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg></button>
      <button class="dl-btn dl-del" id="health-cookie-delete" title="Delete cookies"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg></button>
    </div>
  </div>
</section>
</main>
<nav id="nav">
  <button class="nav-btn active" data-tab="home"><span class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg></span><span>Home</span></button>
  <button class="nav-btn" data-tab="downloads"><span class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg></span><span>Downloads</span></button>
  <button class="nav-btn" data-tab="settings"><span class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg></span><span>System</span></button>
</nav>
<div id="toasts"></div>
</div>
<script>
var S={tab:'home',mode:'audio',url:'',info:null,loading:false,preset:'128k',fmtId:null,fmts:[],task:null,cookiesLoaded:false,plUrl:'',plMode:false,plEntryUrls:[],plEntryTitles:[],subLang:'en',subFmt:'vtt',dlFilter:'all',health:{}};
var polls={};
var _cachedUrls=[];
try{var _su=localStorage.getItem('ytdlp_urls');if(_su)_cachedUrls=JSON.parse(_su);}catch(e){}
function _saveUrls(){try{localStorage.setItem('ytdlp_urls',JSON.stringify(_cachedUrls.slice(0,8)));}catch(e){}}
function _addUrl(u){_cachedUrls=_cachedUrls.filter(function(x){return x!==u;});_cachedUrls.unshift(u);_cachedUrls=_cachedUrls.slice(0,8);_saveUrls();}
var API={
  info:function(url,np){np=np!==false;return fetch('/api/video/info?url='+encodeURIComponent(url)+'&include_raw=false&noplaylist='+np).then(function(r){if(!r.ok)return r.json().then(function(e){throw new Error(e.detail||'Fetch failed')});return r.json();});},
  audio:function(url,preset,playlist){var b={url:url,preset:preset};if(playlist)b.playlist=true;return fetch('/api/audio',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b)}).then(function(r){if(!r.ok)return r.json().then(function(e){throw new Error(e.detail||'Start failed')});return r.json();});},
  video:function(url,fid,playlist){var b={url:url};if(fid)b.format_id=fid;if(playlist)b.playlist=true;return fetch('/api/video',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b)}).then(function(r){if(!r.ok)return r.json().then(function(e){throw new Error(e.detail||'Start failed')});return r.json();});},
  subtitle:function(url,lang,fmt){return fetch('/api/subtitle',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url:url,lang:lang,format:fmt})}).then(function(r){if(!r.ok)return r.json().then(function(e){throw new Error(e.detail||'Start failed')});return r.json();});},
  status:function(type,id){return fetch('/api/'+type+'/'+id+'/status').then(function(r){if(!r.ok)throw new Error('Status failed');return r.json();});},
  tasks:function(){return fetch('/api/tasks').then(function(r){if(!r.ok)throw new Error('Tasks failed');return r.json();});},
  del:function(type,id){return fetch('/api/'+type+'/'+id,{method:'DELETE'}).then(function(r){if(!r.ok)throw new Error('Delete failed');return r.json();});},
  health:function(){return fetch('/api/health').then(function(r){if(!r.ok)throw new Error('Health failed');return r.json();});},
  cookiesStatus:function(){return fetch('/api/cookies').then(function(r){return r.json();});},
  cookiesUpload:function(fd){return fetch('/api/cookies',{method:'POST',body:fd}).then(function(r){if(!r.ok)return r.json().then(function(e){throw new Error(e.detail||'Upload failed')});return r.json();});},
  cookiesDelete:function(){return fetch('/api/cookies',{method:'DELETE'}).then(function(r){return r.json();});}
};
function fmtSize(b){if(!b)return'';var u=['B','KB','MB','GB'];var i=0;while(b>=1024&&i<u.length-1){b/=1024;i++;}return b.toFixed(i?1:0)+u[i];}
function fmtDur(s){if(!s)return'';var m=Math.floor(s/60);var sec=Math.floor(s%60);return m+':'+(sec<10?'0':'')+sec;}
function escHtml(s){var d=document.createElement('div');d.textContent=s;return d.innerHTML;}
function escAttr(s){return s.replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/'/g,'&#39;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
function updateCookieInd(){var el=document.getElementById('cookie-ind');el.className='cookie-ind '+(S.cookiesLoaded?'on':'off');}
function checkCookies(){API.cookiesStatus().then(function(d){S.cookiesLoaded=d.loaded;updateCookieInd();}).catch(function(){S.cookiesLoaded=false;updateCookieInd();});}
function renderPresets(){
  var p=[{id:'48k',label:'Low',sr:'22kHz',ch:'Mono'},{id:'64k',label:'Medium',sr:'22kHz',ch:'Mono'},{id:'128k',label:'HQ',sr:'44kHz',ch:'Stereo'},{id:'320k',label:'Best',sr:'48kHz',ch:'Stereo'}];
  document.getElementById('preset-grid').innerHTML=p.map(function(p){return '<div class="preset-card'+(S.preset===p.id?' selected':'')+'" data-preset="'+p.id+'"><div class="p-check"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg></div><div class="p-bitrate">'+p.id+'</div><div class="p-label">'+p.label+'</div><div class="p-detail">'+p.sr+' &middot; '+p.ch+'</div></div>';}).join('');
  document.querySelectorAll('#preset-grid .preset-card').forEach(function(el){el.addEventListener('click',function(){S.preset=el.dataset.preset;renderPresets();});});
}
function processFormats(formats){
  var v=formats.filter(function(f){return f.vcodec&&f.vcodec!=='none';});var o=v.filter(function(f){return !f.acodec||f.acodec==='none';});var s=o.length>0?o:v;var bH={};
  s.forEach(function(f){var h=parseInt(f.resolution)||0;if(!h)return;if(!bH[h]||(f.tbr||0)>(bH[h].tbr||0))bH[h]=f;});
  return Object.values(bH).sort(function(a,b){return(parseInt(b.resolution)||0)-(parseInt(a.resolution)||0);});
}
function renderFormats(){
  var fmts=S.fmts;var list=document.getElementById('fmt-list');var empty=document.getElementById('fmt-empty');
  if(!fmts.length){list.innerHTML='';empty.style.display='block';return;}
  empty.style.display='none';
  list.innerHTML=fmts.map(function(f){var res=f.resolution||'?';var ext=f.ext||'';var codec=f.vcodec?f.vcodec.split('.')[0].substring(0,6):'';var tbr=f.tbr?Math.round(f.tbr)+'kbps':'';var size=f.filesize?fmtSize(f.filesize):'';return '<div class="fmt-row'+(S.fmtId===f.format_id?' selected':'')+'" data-fid="'+f.format_id+'"><div class="fmt-res">'+res+'p</div><div class="fmt-meta"><span>'+ext.toUpperCase()+(tbr?' &middot; '+tbr:'')+(size?' &middot; '+size:'')+'</span><span class="fmt-codec">'+codec+'</span></div><span class="fmt-badge">'+ext+'</span></div>';}).join('');
  document.querySelectorAll('#fmt-list .fmt-row').forEach(function(el){el.addEventListener('click',function(){S.fmtId=el.dataset.fid;renderFormats();});});
}
function renderPlaylist(info){
  document.getElementById('playlist-view').style.display='block';document.getElementById('preview').style.display='none';
  document.getElementById('pl-thumb').src=info.thumbnail||'';document.getElementById('pl-title').textContent=info.title||'Playlist';
  document.getElementById('pl-uploader').textContent=info.uploader||'';document.getElementById('pl-count').textContent=info.playlist_count+' videos';
  var entries=document.getElementById('pl-entries');
  entries.innerHTML=info.entries.map(function(e,i){return '<div class="pl-entry" data-idx="'+i+'" data-url="'+escAttr(e.url||'')+'"><span class="pl-idx">'+(i+1)+'</span><img class="pl-e-thumb" src="'+(e.thumbnail||'')+'" alt="" onerror="this.style.display=\'none\'"><div class="pl-e-info"><h4>'+escHtml(e.title||'Unknown')+'</h4><span>'+escHtml(e.uploader||e.extractor||'')+'</span></div><span class="pl-e-dur">'+(e.duration?fmtDur(e.duration):'')+'</span></div>';}).join('');
  S.plEntryUrls=info.entries.map(function(e){return e.url||'';});S.plEntryTitles=info.entries.map(function(e){return e.title||'';});
}
function renderDownloads(tasks){
  var list=document.getElementById('dl-list');var empty=document.getElementById('dl-empty');
  var filtered=tasks;var f=S.dlFilter;
  if(f!=='all'){if(f==='completed')filtered=tasks.filter(function(t){return t.status==='completed';});else if(f==='failed')filtered=tasks.filter(function(t){return t.status==='failed';});else filtered=tasks.filter(function(t){return t.type===f;});}
  if(!filtered.length){list.innerHTML='';empty.style.display='block';return;}
  empty.style.display='none';
  list.innerHTML=filtered.map(function(t){
    var isA=t.type==='audio',isV=t.type==='video',isS=t.type==='subtitle',isP=t.is_playlist;
    var icon=isA?'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>':isV?'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2"/></svg>':isS?'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 7v10a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2z"/><line x1="6" y1="12" x2="8" y2="12"/><line x1="10" y1="12" x2="16" y2="12"/></svg>':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h12M9 12h12M9 6h12"/><circle cx="4" cy="6" r="1"/><circle cx="4" cy="12" r="1"/><circle cx="4" cy="18" r="1"/></svg>';
    var iCls=isA?'audio':isV?'video':isS?'subtitle':'playlist';
    var sL={queued:'Queued',downloading:'Downloading',processing:'Processing',completed:'Done',failed:'Failed'}[t.status]||t.status;
    var sub=[t.preset||t.format_id||(t.lang?t.lang+(t.sub_format?'.'+t.sub_format:''):''),t.file_size?fmtSize(t.file_size):'',sL].filter(Boolean);
    if(t.is_playlist)sub.unshift('Playlist');
    var actions='';if(t.status==='completed'){actions+='<button class="dl-btn dl-get" data-type="'+t.type+'" data-id="'+t.task_id+'" data-fname="'+escAttr(t.filename||'')+'"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg></button>';}
    actions+='<button class="dl-btn dl-del" data-type="'+t.type+'" data-id="'+t.task_id+'"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg></button>';
    var prog=(t.status==='downloading'||t.status==='processing')?'<div class="dl-progress"><div class="progress-bar"><div class="progress-fill" style="width:'+t.progress+'%"></div></div></div>':'';
    var eInfo=(t.is_playlist&&t.entries_total)?'<div class="dl-entries">'+(t.entries_done||0)+'/'+t.entries_total+'</div>':'';
    var err=t.error?'<p style="color:var(--red);font-size:10px;margin-top:2px">'+escHtml(t.error.substring(0,70))+'</p>':'';
    return '<div class="dl-item"><div class="dl-icon '+iCls+'">'+icon+'</div><div class="dl-info"><h4>'+escHtml(t.title||t.task_id)+'</h4><p><span class="status-dot '+t.status+'"></span>'+sub.join(' &middot; ')+'</p>'+eInfo+prog+err+'</div><div class="dl-actions">'+actions+'</div></div>';
  }).join('');
  list.querySelectorAll('.dl-get').forEach(function(b){b.addEventListener('click',function(e){e.stopPropagation();var a=document.createElement('a');a.href='/api/'+b.dataset.type+'/'+b.dataset.id+'/download';a.download=b.dataset.fname||'';a.style.display='none';document.body.appendChild(a);a.click();setTimeout(function(){document.body.removeChild(a);},1000);toast('Downloading...','success');});});
  list.querySelectorAll('.dl-del').forEach(function(b){b.addEventListener('click',function(e){e.stopPropagation();API.del(b.dataset.type,b.dataset.id).then(function(){toast('Deleted','info');loadDownloads();}).catch(function(){toast('Delete failed','error');});});});
}
function showUrlHistory(){
  var el=document.getElementById('url-history');if(!_cachedUrls.length||S.loading){el.classList.remove('show');return;}
  el.innerHTML=_cachedUrls.map(function(u){return '<div class="url-h-item" data-url="'+escAttr(u)+'"><span>'+escHtml(u)+'</span><span class="h-del" data-url="'+escAttr(u)+'">&times;</span></div>';}).join('');
  el.classList.add('show');
  el.querySelectorAll('.url-h-item').forEach(function(item){item.addEventListener('click',function(e){if(e.target.classList.contains('h-del')){_cachedUrls=_cachedUrls.filter(function(x){return x!==e.target.dataset.url;});_saveUrls();showUrlHistory();return;}document.getElementById('url-input').value=item.dataset.url;document.getElementById('url-input').dispatchEvent(new Event('input'));el.classList.remove('show');handleFetch();});});
}
function handleFetch(){
  var url=document.getElementById('url-input').value.trim();if(!url)return;
  S.url=url;S.info=null;S.fmts=[];S.fmtId=null;S.task=null;S.loading=true;S.plEntryUrls=[];S.plEntryTitles=[];
  _addUrl(url);updateUI();
  var np=(S.mode!=='playlist');
  API.info(url,np).then(function(info){S.info=info;S.loading=false;if(info._type==='playlist'&&np===false){renderPlaylist(info);S.fmts=[];S.fmtId=null;}else{S.fmts=processFormats(info.formats||[]);S.fmtId=S.fmts.length?S.fmts[0].format_id:null;}updateUI();}).catch(function(e){S.loading=false;updateUI();toast(e.message||'Failed to fetch info','error');});
}
function handleDownload(){
  if(!S.url)return;var btn=document.getElementById('btn-dl');btn.disabled=true;btn.classList.add('pulsing');
  var isPl=(S.mode==='playlist'||(S.info&&S.info._type==='playlist'));var plFlag=(S.mode==='playlist'||isPl);
  var p;
  if(S.mode==='audio'&&!plFlag)p=API.audio(S.url,S.preset,false);
  else if(S.mode==='video'&&!plFlag)p=API.video(S.url,S.fmtId||null,false);
  else if(S.mode==='subtitle'&&!plFlag)p=API.subtitle(S.url,S.subLang,S.subFmt);
  else p=API.audio(S.url,S.preset,true);
  p.then(function(res){S.task={id:res.task_id,type:res.type||S.mode};startPoll(res.task_id,res.type||S.mode);document.getElementById('progress-section').style.display='block';document.getElementById('dl-section').style.display='none';toast('Download started','info');}).catch(function(e){btn.disabled=false;btn.classList.remove('pulsing');toast(e.message||'Failed to start download','error');});
}
function updateUI(){
  var hasInfo=!!S.info;var isPl=hasInfo&&S.info._type==='playlist';
  document.getElementById('home-empty').style.display=(hasInfo||S.loading)?'none':'';
  document.getElementById('loading-skeleton').style.display=S.loading?'block':'none';
  document.getElementById('preview').style.display=(hasInfo&&!isPl)?'block':'none';
  document.getElementById('playlist-view').style.display=(hasInfo&&isPl)?'block':'none';
  document.getElementById('mode-section').style.display=hasInfo?'block':'none';
  document.getElementById('sub-options').style.display=(hasInfo&&S.mode==='subtitle')?'block':'none';
  document.getElementById('pl-info').style.display=(hasInfo&&(S.mode==='playlist'||isPl))?'block':'none';
  if(hasInfo&&!isPl){
    document.getElementById('thumb-img').src=S.info.thumbnail||'';
    document.getElementById('preview-title').textContent=S.info.title||'Unknown';
    document.getElementById('preview-artist').textContent=[S.info.uploader,S.info.duration?fmtDur(S.info.duration):''].filter(Boolean).join(' &middot; ')||'';
    document.getElementById('dur-badge').textContent=S.info.duration?fmtDur(S.info.duration):'';
    document.getElementById('preview-badges').innerHTML=S.info.extractor?'<span class="preview-badge">'+escHtml(S.info.extractor)+'</span>':'';
  }
  document.getElementById('audio-options').style.display=(hasInfo&&S.mode==='audio'&&!isPl)?'block':'none';
  document.getElementById('video-options').style.display=(hasInfo&&S.mode==='video'&&!isPl)?'block':'none';
  document.getElementById('dl-section').style.display=(hasInfo&&!S.task&&!(S.mode==='playlist'&&isPl))?'block':'none';
  document.getElementById('progress-section').style.display=S.task?'block':'none';
  if(hasInfo&&!isPl){renderPresets();renderFormats();}
  var dlBtn=document.getElementById('btn-dl');var dlText=document.getElementById('btn-dl-text');
  if(!S.task){dlBtn.disabled=false;dlBtn.classList.remove('pulsing');}
  if(S.mode==='playlist'||isPl)dlText.textContent='Download Playlist';
  else if(S.mode==='subtitle')dlText.textContent='Download Subtitles';
  else dlText.textContent='Download';
}
function startPoll(id,type){if(polls[id])return;polls[id]=setInterval(function(){API.status(type,id).then(function(s){updateProgress(s);if(s.status==='completed'){stopPoll(id);toast('Complete!','success');document.getElementById('btn-dl').disabled=false;document.getElementById('btn-dl').classList.remove('pulsing');setTimeout(function(){document.getElementById('progress-section').style.display='none';S.task=null;document.getElementById('dl-section').style.display='block';},2000);}else if(s.status==='failed'){stopPoll(id);toast('Failed: '+(s.error||'Unknown'),'error');document.getElementById('btn-dl').disabled=false;document.getElementById('btn-dl').classList.remove('pulsing');document.getElementById('p-fill').classList.add('failed');}}).catch(function(){});},1000);}
function stopPoll(id){if(polls[id]){clearInterval(polls[id]);delete polls[id];}}
function updateProgress(s){var labels={queued:'Queued...',downloading:'Downloading...',processing:'Processing...',completed:'Complete!',failed:'Failed'};document.getElementById('p-status').textContent=labels[s.status]||s.status;document.getElementById('p-pct').textContent=Math.round(s.progress)+'%';document.getElementById('p-fill').style.width=s.progress+'%';if(s.status==='completed')document.getElementById('p-fill').classList.add('complete');}
function loadDownloads(){API.tasks().then(function(tasks){renderDownloads(tasks);tasks.forEach(function(t){if(t.status==='downloading'||t.status==='processing'||t.status==='queued'){if(!polls[t.task_id])startPoll(t.task_id,t.type);}});}).catch(function(){toast('Failed to load downloads','error');});}
function loadHealth(){var grid=document.getElementById('health-grid');var loading=document.getElementById('health-loading');loading.style.display='';grid.innerHTML='';API.health().then(function(h){S.health=h;loading.style.display='none';var cards='';var st=h.status;cards+='<div class="health-card"><div class="health-dot '+(st==='healthy'?'ok':'critical')+'"></div><div class="health-info"><h4>System</h4><p>Status: '+st+' &middot; Uptime: '+fmtDur(h.uptime_seconds)+'</p><p class="health-version">v'+h.version+'</p></div></div>';
var ff=h.checks.ffmpeg;cards+='<div class="health-card"><div class="health-dot '+ff.status+'"></div><div class="health-info"><h4>FFmpeg</h4><p>'+(ff.version||'Not found')+'</p>'+(ff.path?'<p class="health-version">'+ff.path+'</p>':'')+'</div></div>';
var cf=h.checks.cloudflared;cards+='<div class="health-card"><div class="health-dot '+(cf.status==='ok'?'ok':'not_found')+'"></div><div class="health-info"><h4>Cloudflared</h4><p>'+(cf.status==='ok'?cf.version:'Not found')+'</p>'+(cf.path?'<p class="health-version">'+cf.path+'</p>':'')+'</div></div>';
var ds=h.checks.disk_space;var bc='';if(ds.status==='critical')bc=' crit';else if(ds.status==='warning')bc=' warn';cards+='<div class="health-card"><div class="health-dot '+ds.status+'"></div><div class="health-info"><h4>Disk Space</h4><p>'+ds.free_gb+' GB free of '+ds.total_gb+' GB ('+ds.free_percent+'%)</p><div class="health-bar-wrap"><div class="health-bar'+bc+'" style="width:'+ds.free_percent+'%"></div></div></div></div>';
var dd=h.checks.download_dir;cards+='<div class="health-card"><div class="health-dot '+(dd.writable?'ok':'error')+'"></div><div class="health-info"><h4>Download Directory</h4><p>'+(dd.writable?'Writable':'Not writable')+'</p><p class="health-version">'+dd.path+'</p></div></div>';
cards+='<div class="health-card"><div class="health-dot '+(h.tunnel.enabled?'ok':'not_found')+'"></div><div class="health-info"><h4>Tunnel</h4><p>'+(h.tunnel.url||'Not active')+'</p></div></div>';
var ts=h.tasks;cards+='<div class="health-card"><div class="health-dot ok"></div><div class="health-info"><h4>Tasks</h4><p>Total: '+ts.total+' &middot; Active: '+ts.active+' &middot; Queued: '+ts.queued+' &middot; Done: '+ts.completed+' &middot; Failed: '+ts.failed+'</p></div></div>';
grid.innerHTML=cards;document.getElementById('health-footer').innerHTML='<a href="/api/docs">API Documentation</a> &middot; Powered by yt-dlp';updateCookieHealth(h.checks.cookies);}).catch(function(){loading.style.display='none';grid.innerHTML='<div class="empty-state"><h3>Failed to load health data</h3><p>Make sure the server is running</p></div>';});}
function updateCookieHealth(c){var el=document.getElementById('health-cookie-status');if(!c)return;if(c.loaded){el.innerHTML='Loaded &middot; '+fmtSize(c.size)+' &middot; '+c.path;S.cookiesLoaded=true;}else{el.textContent='Not loaded';S.cookiesLoaded=false;}updateCookieInd();}
function switchTab(tab){S.tab=tab;document.querySelectorAll('.page').forEach(function(p){p.classList.remove('active');});document.getElementById('page-'+tab).classList.add('active');document.querySelectorAll('.nav-btn').forEach(function(b){b.classList.toggle('active',b.dataset.tab===tab);});if(tab==='downloads')loadDownloads();if(tab==='settings')loadHealth();}
function switchMode(mode){S.mode=mode;var tabs=document.querySelectorAll('.mode-tab');var idx=0;tabs.forEach(function(t,i){t.classList.toggle('active',t.dataset.mode===mode);if(t.dataset.mode===mode)idx=i;});var ind=document.getElementById('mode-ind');ind.className='mode-ind';if(idx>0)ind.classList.add('a'+(idx+1));S.fmts=[];S.fmtId=null;S.info=null;['preview','playlist-view','audio-options','video-options','sub-options','pl-info','dl-section','progress-section'].forEach(function(id){document.getElementById(id).style.display='none';});document.getElementById('home-empty').style.display='';document.getElementById('loading-skeleton').style.display='none';document.getElementById('mode-section').style.display='none';}
function toast(msg,type){type=type||'info';var icons={success:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="width:16px;height:16px;flex-shrink:0"><polyline points="20 6 9 17 4 12"/></svg>',error:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="width:16px;height:16px;flex-shrink:0"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',info:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="width:16px;height:16px;flex-shrink:0"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>'};var el=document.createElement('div');el.className='toast '+type;el.innerHTML=(icons[type]||icons.info)+'<span>'+escHtml(msg)+'</span><div class="toast-bar"></div>';document.getElementById('toasts').appendChild(el);setTimeout(function(){el.classList.add('out');setTimeout(function(){el.remove();},300);},3000);}
document.getElementById('btn-cookies').addEventListener('click',function(){document.getElementById('cookie-file').click();});
document.getElementById('cookie-file').addEventListener('change',function(){var file=this.files[0];if(!file)return;var fd=new FormData();fd.append('file',file,file.name);API.cookiesUpload(fd).then(function(d){S.cookiesLoaded=true;updateCookieInd();toast(d.message,'success');}).catch(function(e){toast(e.message||'Cookie upload failed','error');});this.value='';});
document.getElementById('health-cookie-upload').addEventListener('click',function(){document.getElementById('cookie-file').click();});
document.getElementById('health-cookie-delete').addEventListener('click',function(){API.cookiesDelete().then(function(d){S.cookiesLoaded=false;updateCookieInd();updateCookieHealth({loaded:false});toast(d.message,'success');}).catch(function(){toast('Delete failed','error');});});
document.getElementById('url-input').addEventListener('input',function(){var v=this.value.trim();document.getElementById('btn-fetch').disabled=!v;document.getElementById('btn-clear').style.display=v?'flex':'none';if(!v)document.getElementById('url-history').classList.remove('show');else showUrlHistory();});
document.getElementById('url-input').addEventListener('focus',function(){if(this.value.trim())showUrlHistory();});
document.getElementById('url-input').addEventListener('blur',function(){setTimeout(function(){document.getElementById('url-history').classList.remove('show');},200);});
document.getElementById('btn-paste').addEventListener('click',function(){navigator.clipboard.readText().then(function(t){document.getElementById('url-input').value=t;document.getElementById('url-input').dispatchEvent(new Event('input'));}).catch(function(){toast('Cannot read clipboard','error');});});
document.getElementById('btn-clear').addEventListener('click',function(){document.getElementById('url-input').value='';document.getElementById('url-input').dispatchEvent(new Event('input'));S.info=null;S.fmts=[];S.fmtId=null;S.task=null;S.url='';updateUI();});
document.getElementById('btn-fetch').addEventListener('click',handleFetch);
document.getElementById('btn-dl').addEventListener('click',handleDownload);
document.querySelectorAll('.mode-tab').forEach(function(t){t.addEventListener('click',function(){switchMode(t.dataset.mode);});});
document.querySelectorAll('.nav-btn').forEach(function(b){b.addEventListener('click',function(){switchTab(b.dataset.tab);});});
document.getElementById('btn-refresh').addEventListener('click',loadDownloads);
document.getElementById('btn-health-refresh').addEventListener('click',loadHealth);
document.getElementById('btn-pl-dl-all').addEventListener('click',function(){if(!S.plEntryUrls.length)return;handleDownload();});
document.getElementById('sub-lang').addEventListener('change',function(){S.subLang=this.value;});
document.getElementById('sub-fmt').addEventListener('change',function(){S.subFmt=this.value;});
document.querySelectorAll('#dl-filters .filter-btn').forEach(function(b){b.addEventListener('click',function(){document.querySelectorAll('#dl-filters .filter-btn').forEach(function(x){x.classList.remove('active');});b.classList.add('active');S.dlFilter=b.dataset.filter;loadDownloads();});});
document.getElementById('url-input').addEventListener('keydown',function(e){if(e.key==='Enter'&&this.value.trim())handleFetch();});
updateUI();checkCookies();
</script>
</body>
</html>"""
