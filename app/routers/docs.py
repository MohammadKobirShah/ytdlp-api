"""
Professional modern API documentation page.
Served at /api/docs with dark theme and interactive examples.
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["docs"])


@router.get("/api/docs", response_class=HTMLResponse)
async def api_docs():
    return _HTML


_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#0a0a1a">
<title>YTDLP-API Docs</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>&#x1f4d6;</text></svg>">
<style>
:root{
  --bg:#0a0a1a;--bg2:#111128;--card:#1a1a3e;--card2:#222255;
  --grad:linear-gradient(135deg,#667eea,#764ba2);
  --t1:#fff;--t2:#9999bb;--t3:#555577;
  --border:rgba(255,255,255,.06);--accent:#667eea;--accent2:#8b9cf7;
  --green:#00e676;--red:#ff5252;--blue:#448aff;--yellow:#ffd740;
  --r:14px;--rs:10px;--rx:6px;
}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
  background:var(--bg);color:var(--t1);-webkit-font-smoothing:antialiased;
  line-height:1.6;min-height:100vh}

/* Header */
.doc-header{padding:48px 24px 40px;text-align:center;
  background:linear-gradient(180deg,rgba(102,126,234,.08) 0%,transparent 100%);
  border-bottom:1px solid var(--border)}
.doc-header h1{font-size:32px;font-weight:800;background:var(--grad);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  margin-bottom:8px;letter-spacing:-.5px}
.doc-header p{color:var(--t2);font-size:15px;max-width:480px;margin:0 auto 20px}
.base-url{display:inline-flex;align-items:center;gap:8px;background:var(--card);
  border:1px solid var(--border);border-radius:var(--rs);padding:10px 16px;
  font-family:'SF Mono','Fira Code',monospace;font-size:13px;color:var(--accent2)}
.base-url button{background:none;border:none;color:var(--t2);cursor:pointer;padding:4px;
  border-radius:4px;transition:.2s}
.base-url button:hover{color:var(--t1)}

/* Container */
.container{max-width:780px;margin:0 auto;padding:24px 16px 80px}

/* Section */
.section{margin-bottom:40px}
.section-title{display:flex;align-items:center;gap:10px;font-size:20px;font-weight:700;
  margin-bottom:16px;padding-bottom:10px;border-bottom:1px solid var(--border)}
.section-title .sec-icon{width:28px;height:28px;border-radius:8px;display:flex;
  align-items:center;justify-content:center;font-size:16px}
.sec-icon.audio{background:linear-gradient(135deg,rgba(102,126,234,.2),rgba(118,75,162,.2))}
.sec-icon.video{background:linear-gradient(135deg,rgba(0,230,118,.15),rgba(0,191,165,.15))}
.sec-icon.sys{background:linear-gradient(135deg,rgba(255,215,64,.15),rgba(255,152,0,.15))}

/* Endpoint Card */
.ep-card{background:var(--card);border:1px solid var(--border);border-radius:var(--r);
  margin-bottom:12px;overflow:hidden;transition:.2s}
.ep-card:hover{border-color:rgba(102,126,234,.2)}
.ep-head{display:flex;align-items:center;gap:10px;padding:14px 16px;cursor:pointer;
  user-select:none;transition:.15s}
.ep-head:hover{background:rgba(255,255,255,.02)}
.ep-badge{font-size:11px;font-weight:800;padding:4px 10px;border-radius:4px;
  letter-spacing:.5px;min-width:52px;text-align:center;flex-shrink:0}
.ep-badge.get{background:rgba(0,230,118,.12);color:var(--green)}
.ep-badge.post{background:rgba(68,138,255,.12);color:var(--blue)}
.ep-badge.delete{background:rgba(255,82,82,.12);color:var(--red)}
.ep-path{font-family:'SF Mono','Fira Code',monospace;font-size:14px;font-weight:600}
.ep-desc{color:var(--t2);font-size:13px;margin-left:auto;flex-shrink:0;
  display:none}
@media(min-width:640px){.ep-desc{display:block}}
.ep-arrow{color:var(--t3);transition:.2s;flex-shrink:0;margin-left:8px}
.ep-arrow svg{width:16px;height:16px}
.ep-card.open .ep-arrow{transform:rotate(180deg)}

/* Endpoint Body */
.ep-body{display:none;padding:0 16px 16px;border-top:1px solid var(--border)}
.ep-card.open .ep-body{display:block;animation:fadeIn .2s ease}
.ep-body h4{font-size:13px;font-weight:700;color:var(--t2);margin:14px 0 8px;
  text-transform:uppercase;letter-spacing:.5px}
.ep-body pre{background:var(--bg2);border:1px solid var(--border);border-radius:var(--rx);
  padding:12px 14px;font-family:'SF Mono','Fira Code',monospace;font-size:12px;
  line-height:1.5;overflow-x:auto;color:var(--t2);position:relative}
.ep-body pre .k{color:var(--accent2)}
.ep-body pre .s{color:var(--green)}
.ep-body pre .n{color:var(--yellow)}
.ep-body pre .c{color:var(--t3)}
.ep-copy{position:absolute;top:8px;right:8px;background:var(--card);border:1px solid var(--border);
  color:var(--t2);padding:4px 8px;border-radius:4px;font-size:11px;cursor:pointer;
  font-family:inherit;transition:.2s}
.ep-copy:hover{color:var(--t1);background:var(--card2)}
.ep-copy.copied{color:var(--green);border-color:rgba(0,230,118,.3)}

/* Params Table */
.params{width:100%;border-collapse:collapse;font-size:13px;margin:8px 0}
.params th{text-align:left;color:var(--t3);font-weight:600;padding:6px 8px;
  border-bottom:1px solid var(--border);font-size:11px;text-transform:uppercase;letter-spacing:.5px}
.params td{padding:6px 8px;border-bottom:1px solid var(--border);color:var(--t2)}
.params td:first-child{color:var(--accent2);font-family:'SF Mono','Fira Code',monospace;font-size:12px}
.params .req{color:var(--yellow);font-size:10px;font-weight:700;margin-left:4px}

/* Back Link */
.back-link{display:inline-flex;align-items:center;gap:6px;color:var(--t2);
  text-decoration:none;font-size:13px;padding:8px 0;transition:.2s;margin-bottom:16px}
.back-link:hover{color:var(--t1)}

/* Footer */
.doc-footer{text-align:center;padding:32px 0;font-size:12px;color:var(--t3);
  border-top:1px solid var(--border);margin-top:40px}

/* Animations */
@keyframes fadeIn{from{opacity:0;transform:translateY(-4px)}to{opacity:1;transform:translateY(0)}}

/* Scrollbar */
::-webkit-scrollbar{width:6px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:var(--card2);border-radius:3px}
::-webkit-scrollbar-thumb:hover{background:var(--t3)}
</style>
</head>
<body>

<!-- Header -->
<div class="doc-header">
  <h1>&#x1f3b5; YTDLP-API</h1>
  <p>Free &bull; No API key &bull; No login &bull; No rate-limit<br>Audio transcode + Video merge + Full format dump</p>
  <div class="base-url">
    <span id="base-url-text"></span>
    <button onclick="copyBase()" id="base-copy" title="Copy">&#x1f4cb;</button>
  </div>
</div>

<!-- Content -->
<div class="container">
  <a href="/" class="back-link">&larr; Back to WebUI</a>

  <!-- AUDIO -->
  <div class="section">
    <div class="section-title"><span class="sec-icon audio">&#x1f50a;</span> Audio</div>

    <div class="ep-card" data-ep="audio-post">
      <div class="ep-head" onclick="toggle(this)">
        <span class="ep-badge post">POST</span>
        <span class="ep-path">/api/audio</span>
        <span class="ep-desc">Queue audio download</span>
        <span class="ep-arrow"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg></span>
      </div>
      <div class="ep-body">
        <h4>Request Body</h4>
        <table class="params">
          <tr><th>Field</th><th>Type</th><th>Default</th><th>Description</th></tr>
          <tr><td>url<span class="req">REQ</span></td><td>string</td><td>&mdash;</td><td>Video/audio URL</td></tr>
          <tr><td>preset</td><td>string</td><td>"128k"</td><td>48k | 64k | 128k | 320k</td></tr>
          <tr><td>playlist</td><td>bool</td><td>false</td><td>Download playlist/channel as zip</td></tr>
        </table>
        <h4>Example Request</h4>
        <pre><button class="ep-copy" onclick="copyCmd(this)">Copy</button><span class="c"># Audio @ 128k MP3</span>
curl -X POST <span class="s">{{BASE}}</span>/api/audio \\
  -H <span class="s">"Content-Type: application/json"</span> \\
  -d <span class="s">'{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "preset": "128k"}'</span></pre>
        <h4>Response</h4>
        <pre>{
  <span class="k">"task_id"</span>: <span class="s">"a1b2c3d4e5f6"</span>,
  <span class="k">"status"</span>: <span class="s">"queued"</span>,
  <span class="k">"preset"</span>: <span class="s">"128k"</span>,
  <span class="k">"message"</span>: <span class="s">"Queued. Poll /api/audio/{task_id}/status for progress."</span>
}</pre>
      </div>
    </div>

    <div class="ep-card" data-ep="audio-status">
      <div class="ep-head" onclick="toggle(this)">
        <span class="ep-badge get">GET</span>
        <span class="ep-path">/api/audio/{task_id}/status</span>
        <span class="ep-desc">Poll task progress</span>
        <span class="ep-arrow"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg></span>
      </div>
      <div class="ep-body">
        <h4>Response</h4>
        <pre>{
  <span class="k">"task_id"</span>: <span class="s">"a1b2c3d4e5f6"</span>,
  <span class="k">"type"</span>: <span class="s">"audio"</span>,
  <span class="k">"status"</span>: <span class="s">"completed"</span>,
  <span class="k">"progress"</span>: <span class="n">100</span>,
  <span class="k">"preset"</span>: <span class="s">"128k"</span>,
  <span class="k">"title"</span>: <span class="s">"Rick Astley - Never Gonna Give You Up"</span>,
  <span class="k">"artist"</span>: <span class="s">"Rick Astley"</span>,
  <span class="k">"duration"</span>: <span class="n">212</span>,
  <span class="k">"file_size"</span>: <span class="n">3392000</span>,
  <span class="k">"filename"</span>: <span class="s">"Rick Astley - Never Gonna Give You Up [128k].mp3"</span>,
  <span class="k">"download_url"</span>: <span class="s">"https://xxx.trycloudflare.com/api/audio/a1b2c3d4e5f6/download"</span>,
  <span class="k">"error"</span>: <span class="k">null</span>
}</pre>
      </div>
    </div>

    <div class="ep-card" data-ep="audio-download">
      <div class="ep-head" onclick="toggle(this)">
        <span class="ep-badge get">GET</span>
        <span class="ep-path">/api/audio/{task_id}/download</span>
        <span class="ep-desc">Download the MP3 file</span>
        <span class="ep-arrow"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg></span>
      </div>
      <div class="ep-body">
        <h4>Response</h4>
        <pre><span class="c">Content-Type: audio/mpeg
Content-Disposition: attachment; filename*=UTF-8''...</span>

<span class="c">Binary MP3 file with embedded metadata + thumbnail</span></pre>
      </div>
    </div>

    <div class="ep-card" data-ep="audio-delete">
      <div class="ep-head" onclick="toggle(this)">
        <span class="ep-badge delete">DEL</span>
        <span class="ep-path">/api/audio/{task_id}</span>
        <span class="ep-desc">Remove task + file</span>
        <span class="ep-arrow"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg></span>
      </div>
      <div class="ep-body">
        <h4>Response</h4>
        <pre>{ <span class="k">"deleted"</span>: <span class="s">"a1b2c3d4e5f6"</span> }</pre>
      </div>
    </div>
  </div>

  <!-- VIDEO -->
  <div class="section">
    <div class="section-title"><span class="sec-icon video">&#x1f3ac;</span> Video</div>

    <div class="ep-card" data-ep="video-info">
      <div class="ep-head" onclick="toggle(this)">
        <span class="ep-badge get">GET</span>
        <span class="ep-path">/api/video/info</span>
        <span class="ep-desc">Full format dump</span>
        <span class="ep-arrow"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg></span>
      </div>
      <div class="ep-body">
        <h4>Query Parameters</h4>
        <table class="params">
          <tr><th>Param</th><th>Type</th><th>Default</th><th>Description</th></tr>
          <tr><td>url<span class="req">REQ</span></td><td>string</td><td>&mdash;</td><td>Video/playlist URL</td></tr>
          <tr><td>include_raw</td><td>bool</td><td>false</td><td>Include full yt-dlp info dict</td></tr>
          <tr><td>noplaylist</td><td>bool</td><td>true</td><td>Set to false to list playlist entries</td></tr>
        </table>
        <h4>Playlist Response</h4>
        <pre>{
  <span class="k">"_type"</span>: <span class="s">"playlist"</span>,
  <span class="k">"title"</span>: <span class="s">"Playlist Title"</span>,
  <span class="k">"playlist_count"</span>: <span class="n">10</span>,
  <span class="k">"entries"</span>: [
    { <span class="k">"id"</span>: <span class="s">"..."</span>, <span class="k">"title"</span>: <span class="s">"Video 1"</span>, <span class="k">"duration"</span>: <span class="n">120</span>, <span class="k">"url"</span>: <span class="s">"..."</span> }
  ]
}</pre>
        <h4>Example</h4>
        <pre><button class="ep-copy" onclick="copyCmd(this)">Copy</button>curl <span class="s">{{BASE}}</span>/api/video/info?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ</pre>
        <h4>Response</h4>
        <pre>{
  <span class="k">"title"</span>: <span class="s">"Rick Astley - Never Gonna Give You Up"</span>,
  <span class="k">"duration"</span>: <span class="n">212</span>,
  <span class="k">"thumbnail"</span>: <span class="s">"https://i.ytimg.com/vi/.../maxresdefault.jpg"</span>,
  <span class="k">"artist"</span>: <span class="s">"Rick Astley"</span>,
  <span class="k">"formats"</span>: [
    {
      <span class="k">"format_id"</span>: <span class="s">"137"</span>,
      <span class="k">"ext"</span>: <span class="s">"mp4"</span>,
      <span class="k">"resolution"</span>: <span class="s">"1080"</span>,
      <span class="k">"vcodec"</span>: <span class="s">"avc1"</span>,
      <span class="k">"acodec"</span>: <span class="s">"none"</span>,
      <span class="k">"tbr"</span>: <span class="n">2400</span>
    },
    ...
  ]
}</pre>
      </div>
    </div>

    <div class="ep-card" data-ep="video-post">
      <div class="ep-head" onclick="toggle(this)">
        <span class="ep-badge post">POST</span>
        <span class="ep-path">/api/video</span>
        <span class="ep-desc">Queue video merge download</span>
        <span class="ep-arrow"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg></span>
      </div>
      <div class="ep-body">
        <h4>Request Body</h4>
        <table class="params">
          <tr><th>Field</th><th>Type</th><th>Default</th><th>Description</th></tr>
          <tr><td>url<span class="req">REQ</span></td><td>string</td><td>&mdash;</td><td>Video URL</td></tr>
          <tr><td>format_id</td><td>string</td><td>null</td><td>e.g. "137+251" or blank for best</td></tr>
          <tr><td>playlist</td><td>bool</td><td>false</td><td>Download playlist/channel as zip</td></tr>
        </table>
        <h4>Example</h4>
        <pre><button class="ep-copy" onclick="copyCmd(this)">Copy</button><span class="c"># Best quality (auto-merge)</span>
curl -X POST <span class="s">{{BASE}}</span>/api/video \\
  -H <span class="s">"Content-Type: application/json"</span> \\
  -d <span class="s">'{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'</span>

<span class="c"># Specific format (1080p video + best audio)</span>
curl -X POST <span class="s">{{BASE}}</span>/api/video \\
  -H <span class="s">"Content-Type: application/json"</span> \\
  -d <span class="s">'{"url": "...", "format_id": "137+251"}'</span></pre>
        <h4>Response</h4>
        <pre>{
  <span class="k">"task_id"</span>: <span class="s">"f6e5d4c3b2a1"</span>,
  <span class="k">"status"</span>: <span class="s">"queued"</span>,
  <span class="k">"message"</span>: <span class="s">"Queued. Poll /api/video/{task_id}/status for progress."</span>
}</pre>
      </div>
    </div>

    <div class="ep-card" data-ep="video-status">
      <div class="ep-head" onclick="toggle(this)">
        <span class="ep-badge get">GET</span>
        <span class="ep-path">/api/video/{task_id}/status</span>
        <span class="ep-desc">Poll task progress</span>
        <span class="ep-arrow"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg></span>
      </div>
      <div class="ep-body">
        <h4>Response</h4>
        <pre>{
  <span class="k">"task_id"</span>: <span class="s">"f6e5d4c3b2a1"</span>,
  <span class="k">"type"</span>: <span class="s">"video"</span>,
  <span class="k">"status"</span>: <span class="s">"completed"</span>,
  <span class="k">"progress"</span>: <span class="n">100</span>,
  <span class="k">"format_id"</span>: <span class="s">"137+251"</span>,
  <span class="k">"title"</span>: <span class="s">"Rick Astley - Never Gonna Give You Up"</span>,
  <span class="k">"file_size"</span>: <span class="n">245000000</span>,
  <span class="k">"filename"</span>: <span class="s">"Rick Astley - Never Gonna Give You Up.mp4"</span>,
  <span class="k">"download_url"</span>: <span class="s">"https://xxx.trycloudflare.com/api/video/f6e5d4c3b2a1/download"</span>
}</pre>
      </div>
    </div>

    <div class="ep-card" data-ep="video-download">
      <div class="ep-head" onclick="toggle(this)">
        <span class="ep-badge get">GET</span>
        <span class="ep-path">/api/video/{task_id}/download</span>
        <span class="ep-desc">Download merged video</span>
        <span class="ep-arrow"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg></span>
      </div>
      <div class="ep-body">
        <h4>Response</h4>
        <pre><span class="c">Content-Type: video/mp4
Content-Disposition: attachment; filename*=UTF-8''...</span>

<span class="c">Binary MP4/WebM file (no transcode, stream copy)</span></pre>
      </div>
    </div>

    <div class="ep-card" data-ep="video-delete">
      <div class="ep-head" onclick="toggle(this)">
        <span class="ep-badge delete">DEL</span>
        <span class="ep-path">/api/video/{task_id}</span>
        <span class="ep-desc">Remove task + file</span>
        <span class="ep-arrow"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg></span>
      </div>
      <div class="ep-body">
        <h4>Response</h4>
        <pre>{ <span class="k">"deleted"</span>: <span class="s">"f6e5d4c3b2a1"</span> }</pre>
      </div>
    </div>
  </div>

  <!-- SUBTITLE -->
  <div class="section">
    <div class="section-title"><span class="sec-icon audio">&#x1f4c4;</span> Subtitles</div>

    <div class="ep-card" data-ep="sub-post">
      <div class="ep-head" onclick="toggle(this)">
        <span class="ep-badge post">POST</span>
        <span class="ep-path">/api/subtitle</span>
        <span class="ep-desc">Queue subtitle download</span>
        <span class="ep-arrow"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg></span>
      </div>
      <div class="ep-body">
        <h4>Request Body</h4>
        <table class="params">
          <tr><th>Field</th><th>Type</th><th>Default</th><th>Description</th></tr>
          <tr><td>url<span class="req">REQ</span></td><td>string</td><td>&mdash;</td><td>Video URL</td></tr>
          <tr><td>lang</td><td>string</td><td>"en"</td><td>ISO language code</td></tr>
          <tr><td>format</td><td>string</td><td>"vtt"</td><td>vtt | srt | ass | lrc</td></tr>
        </table>
        <h4>Example</h4>
        <pre><button class="ep-copy" onclick="copyCmd(this)">Copy</button>curl -X POST <span class="s">{{BASE}}</span>/api/subtitle \
  -H <span class="s">"Content-Type: application/json"</span> \
  -d <span class="s">'{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "lang": "en", "format": "vtt"}'</span></pre>
        <h4>Response</h4>
        <pre>{
  <span class="k">"task_id"</span>: <span class="s">"s1b2c3d4e5f6"</span>,
  <span class="k">"status"</span>: <span class="s">"queued"</span>,
  <span class="k">"lang"</span>: <span class="s">"en"</span>,
  <span class="k">"format"</span>: <span class="s">"vtt"</span>,
  <span class="k">"message"</span>: <span class="s">"Queued. Poll /api/subtitle/{task_id}/status for progress."</span>
}</pre>
      </div>
    </div>

    <div class="ep-card" data-ep="sub-status">
      <div class="ep-head" onclick="toggle(this)">
        <span class="ep-badge get">GET</span>
        <span class="ep-path">/api/subtitle/{task_id}/status</span>
        <span class="ep-desc">Poll subtitle task</span>
        <span class="ep-arrow"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg></span>
      </div>
      <div class="ep-body">
        <h4>Response</h4>
        <pre>{
  <span class="k">"task_id"</span>: <span class="s">"s1b2c3d4e5f6"</span>,
  <span class="k">"type"</span>: <span class="s">"subtitle"</span>,
  <span class="k">"status"</span>: <span class="s">"completed"</span>,
  <span class="k">"lang"</span>: <span class="s">"en"</span>,
  <span class="k">"sub_format"</span>: <span class="s">"vtt"</span>,
  <span class="k">"filename"</span>: <span class="s">"Rick Astley - Never Gonna Give You Up.en.vtt"</span>,
  <span class="k">"download_url"</span>: <span class="s">"https://xxx.trycloudflare.com/api/subtitle/s1b2c3d4e5f6/download"</span>
}</pre>
      </div>
    </div>

    <div class="ep-card" data-ep="sub-download">
      <div class="ep-head" onclick="toggle(this)">
        <span class="ep-badge get">GET</span>
        <span class="ep-path">/api/subtitle/{task_id}/download</span>
        <span class="ep-desc">Download subtitle file</span>
        <span class="ep-arrow"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg></span>
      </div>
      <div class="ep-body">
        <h4>Response</h4>
        <pre><span class="c">Content-Type: text/vtt
Content-Disposition: attachment</span>

<span class="c">WebVTT subtitle file with captions</span></pre>
      </div>
    </div>

    <div class="ep-card" data-ep="sub-delete">
      <div class="ep-head" onclick="toggle(this)">
        <span class="ep-badge delete">DEL</span>
        <span class="ep-path">/api/subtitle/{task_id}</span>
        <span class="ep-desc">Remove task + file</span>
        <span class="ep-arrow"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg></span>
      </div>
      <div class="ep-body">
        <h4>Response</h4>
        <pre>{ <span class="k">"deleted"</span>: <span class="s">"s1b2c3d4e5f6"</span> }</pre>
      </div>
    </div>
  </div>

  <!-- SYSTEM -->
  <div class="section">
    <div class="section-title"><span class="sec-icon sys">&#x2699;&#xfe0f;</span> System</div>

    <div class="ep-card" data-ep="sys-health">
      <div class="ep-head" onclick="toggle(this)">
        <span class="ep-badge get">GET</span>
        <span class="ep-path">/api/health</span>
        <span class="ep-desc">Dependency health checks</span>
        <span class="ep-arrow"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg></span>
      </div>
      <div class="ep-body">
        <h4>Response</h4>
        <pre>{
  <span class="k">"status"</span>: <span class="s">"healthy"</span>,
  <span class="k">"version"</span>: <span class="s">"1.0.0"</span>,
  <span class="k">"uptime_seconds"</span>: <span class="n">1234</span>,
  <span class="k">"checks"</span>: {
    <span class="k">"ffmpeg"</span>: { <span class="k">"status"</span>: <span class="s">"ok"</span>, <span class="k">"version"</span>: <span class="s">"6.1.1"</span>, <span class="k">"path"</span>: <span class="s">"/usr/bin/ffmpeg"</span> },
    <span class="k">"cloudflared"</span>: { <span class="k">"status"</span>: <span class="s">"ok"</span>, <span class="k">"version"</span>: <span class="s">"..."</span>, <span class="k">"path"</span>: <span class="s">"..."</span> },
    <span class="k">"disk_space"</span>: { <span class="k">"status"</span>: <span class="s">"ok"</span>, <span class="k">"free_gb"</span>: <span class="n">55</span>, <span class="k">"free_percent"</span>: <span class="n">55</span> },
    <span class="k">"download_dir"</span>: { <span class="k">"status"</span>: <span class="s">"ok"</span>, <span class="k">"writable"</span>: <span class="k">true</span> },
    <span class="k">"cookies"</span>: { <span class="k">"loaded"</span>: <span class="k">true</span>, <span class="k">"size"</span>: <span class="n">123</span> }
  },
  <span class="k">"tasks"</span>: { <span class="k">"total"</span>: <span class="n">0</span>, <span class="k">"active"</span>: <span class="n">0</span> }
}</pre>
      </div>
    </div>

    <div class="ep-card" data-ep="sys-status">
      <div class="ep-head" onclick="toggle(this)">
        <span class="ep-badge get">GET</span>
        <span class="ep-path">/api/status</span>
        <span class="ep-desc">System info + tunnel URL</span>
        <span class="ep-arrow"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg></span>
      </div>
      <div class="ep-body">
        <h4>Response</h4>
        <pre>{
  <span class="k">"status"</span>: <span class="s">"running"</span>,
  <span class="k">"tunnel_url"</span>: <span class="s">"https://xxx.trycloudflare.com"</span>,
  <span class="k">"local_url"</span>: <span class="s">"http://localhost:8000"</span>,
  <span class="k">"presets"</span>: [<span class="s">"48k"</span>, <span class="s">"64k"</span>, <span class="s">"128k"</span>, <span class="s">"320k"</span>],
  <span class="k">"tasks"</span>: {
    <span class="k">"total"</span>: <span class="n">5</span>,
    <span class="k">"queued"</span>: <span class="n">1</span>,
    <span class="k">"active"</span>: <span class="n">2</span>,
    <span class="k">"completed"</span>: <span class="n">1</span>,
    <span class="k">"failed"</span>: <span class="n">1</span>
  }
}</pre>
      </div>
    </div>

    <div class="ep-card" data-ep="sys-tasks">
      <div class="ep-head" onclick="toggle(this)">
        <span class="ep-badge get">GET</span>
        <span class="ep-path">/api/tasks</span>
        <span class="ep-desc">List all tasks</span>
        <span class="ep-arrow"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg></span>
      </div>
      <div class="ep-body">
        <h4>Query Parameters</h4>
        <table class="params">
          <tr><th>Param</th><th>Type</th><th>Default</th></tr>
          <tr><td>limit</td><td>int</td><td>50</td></tr>
        </table>
        <h4>Response</h4>
        <pre>[
  {
    <span class="k">"task_id"</span>: <span class="s">"a1b2c3d4e5f6"</span>,
    <span class="k">"type"</span>: <span class="s">"audio"</span>,
    <span class="k">"status"</span>: <span class="s">"completed"</span>,
    <span class="k">"progress"</span>: <span class="n">100</span>,
    <span class="k">"title"</span>: <span class="s">"Song Title"</span>,
    <span class="k">"preset"</span>: <span class="s">"128k"</span>,
    <span class="k">"filename"</span>: <span class="s">"Song Title [128k].mp3"</span>,
    <span class="k">"file_size"</span>: <span class="n">3392000</span>
  }
]</pre>
      </div>
    </div>

    <div class="ep-card" data-ep="sys-presets">
      <div class="ep-head" onclick="toggle(this)">
        <span class="ep-badge get">GET</span>
        <span class="ep-path">/api/presets</span>
        <span class="ep-desc">Audio preset details</span>
        <span class="ep-arrow"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg></span>
      </div>
      <div class="ep-body">
        <h4>Response</h4>
        <pre>{
  <span class="k">"audio_presets"</span>: {
    <span class="k">"48k"</span>:  { <span class="k">"bitrate"</span>:<span class="s">"48k"</span>,  <span class="k">"sample_rate"</span>:<span class="n">22050</span>, <span class="k">"channels"</span>:<span class="n">1</span> },
    <span class="k">"64k"</span>:  { <span class="k">"bitrate"</span>:<span class="s">"64k"</span>,  <span class="k">"sample_rate"</span>:<span class="n">22050</span>, <span class="k">"channels"</span>:<span class="n">1</span> },
    <span class="k">"128k"</span>: { <span class="k">"bitrate"</span>:<span class="s">"128k"</span>, <span class="k">"sample_rate"</span>:<span class="n">44100</span>, <span class="k">"channels"</span>:<span class="n">2</span> },
    <span class="k">"320k"</span>: { <span class="k">"bitrate"</span>:<span class="s">"320k"</span>, <span class="k">"sample_rate"</span>:<span class="n">48000</span>, <span class="k">"channels"</span>:<span class="n">2</span> }
  }
}</pre>
      </div>
    </div>
  </div>

  <!-- Status Flow -->
  <div class="section">
    <div class="section-title">&#x1f4ca; Task Status Flow</div>
    <div style="background:var(--card);border:1px solid var(--border);border-radius:var(--r);padding:20px;text-align:center">
      <div style="display:flex;align-items:center;justify-content:center;gap:8px;flex-wrap:wrap;font-size:14px">
        <span style="background:rgba(85,85,119,.2);color:var(--t3);padding:6px 14px;border-radius:20px;font-weight:600">queued</span>
        <span style="color:var(--t3)">&rarr;</span>
        <span style="background:rgba(68,138,255,.12);color:var(--blue);padding:6px 14px;border-radius:20px;font-weight:600">downloading</span>
        <span style="color:var(--t3)">&rarr;</span>
        <span style="background:rgba(255,215,64,.12);color:var(--yellow);padding:6px 14px;border-radius:20px;font-weight:600">processing</span>
        <span style="color:var(--t3)">&rarr;</span>
        <span style="background:rgba(0,230,118,.12);color:var(--green);padding:6px 14px;border-radius:20px;font-weight:600">completed</span>
      </div>
      <div style="margin-top:10px;font-size:13px;color:var(--t3)">
        Any stage may transition to <span style="color:var(--red);font-weight:600">failed</span> on error
      </div>
    </div>
  </div>

  <div class="doc-footer">
    YTDLP-API v1.0.0 &bull; Powered by yt-dlp + FFmpeg + Cloudflared
  </div>
</div>

<script>
// Base URL
var base = window.location.origin;
document.getElementById('base-url-text').textContent = base;

// Replace all {{BASE}} in pre blocks
document.querySelectorAll('pre').forEach(function(pre) {
  pre.innerHTML = pre.innerHTML.replace(/\\{\\{BASE\\}\\}/g, base);
});

// Toggle endpoint cards
function toggle(head){
  var card = head.closest('.ep-card');
  card.classList.toggle('open');
}

// Copy base URL
function copyBase(){
  navigator.clipboard.writeText(base).then(function(){
    var btn = document.getElementById('base-copy');
    btn.textContent = '\\u2705';
    setTimeout(function(){ btn.textContent = '\\ud83d\\udccb'; }, 1500);
  });
}

// Copy curl command
function copyCmd(btn){
  var pre = btn.closest('pre');
  var text = pre.textContent.replace('Copy','').trim();
  navigator.clipboard.writeText(text).then(function(){
    btn.textContent = '\\u2705 Copied';
    btn.classList.add('copied');
    setTimeout(function(){ btn.textContent = 'Copy'; btn.classList.remove('copied'); }, 1500);
  });
}
</script>
</body>
</html>"""
