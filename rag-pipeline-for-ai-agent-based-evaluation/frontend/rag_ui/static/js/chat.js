/* ============================================================
   Chat page — all interactive behaviour
   ============================================================ */

// ── Utilities ─────────────────────────────────────────────────
function toast(msg, type = 'info') {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.className = `toast toast-${type} show`;
  clearTimeout(el._t);
  el._t = setTimeout(() => { el.className = 'toast'; }, 3500);
}

function getCsrf() {
  // Read from the hidden input Django renders via {% csrf_token %}
  const el = document.querySelector('[name=csrfmiddlewaretoken]');
  return el ? el.value : '';
}

// ── Chat messages ──────────────────────────────────────────────
const chatMessages = document.getElementById('chat-messages');
const chatEmpty    = document.getElementById('chat-empty');

function hideEmpty() {
  if (chatEmpty) { chatEmpty.style.display = 'none'; }
}

function appendMessage(role, text, sources = []) {
  hideEmpty();

  const wrap = document.createElement('div');
  wrap.className = `message message--${role}`;

  const roleEl = document.createElement('div');
  roleEl.className = 'message-role';
  roleEl.textContent = role === 'user' ? 'You' : 'Assistant';

  const bubble = document.createElement('div');
  bubble.className = 'message-bubble';
  bubble.textContent = text;

  wrap.appendChild(roleEl);
  wrap.appendChild(bubble);

  if (sources.length) {
    const srcWrap = document.createElement('div');
    srcWrap.className = 'message-sources';
    sources.forEach(s => {
      const tag = document.createElement('span');
      tag.className = 'source-tag';
      tag.textContent = s;
      srcWrap.appendChild(tag);
    });
    wrap.appendChild(srcWrap);
  }

  chatMessages.appendChild(wrap);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return wrap;
}

function appendThinking() {
  hideEmpty();
  const wrap = document.createElement('div');
  wrap.className = 'message message--assistant';

  const roleEl = document.createElement('div');
  roleEl.className = 'message-role';
  roleEl.textContent = 'Assistant';

  const bubble = document.createElement('div');
  bubble.className = 'message-bubble thinking';
  bubble.innerHTML = `
    <span class="thinking-dot"></span>
    <span class="thinking-dot"></span>
    <span class="thinking-dot"></span>`;

  wrap.appendChild(roleEl);
  wrap.appendChild(bubble);
  chatMessages.appendChild(wrap);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return wrap;
}

// ── Chat form ──────────────────────────────────────────────────
const chatForm  = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');

// Auto-grow textarea up to max-height (set via CSS)
chatInput.addEventListener('input', () => {
  chatInput.style.height = 'auto';
  chatInput.style.height = Math.min(chatInput.scrollHeight, 160) + 'px';
});

// Enter = submit, Shift+Enter = newline
chatInput.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    chatForm.dispatchEvent(new Event('submit', { bubbles: true }));
  }
});

chatForm.addEventListener('submit', async e => {
  e.preventDefault();
  const query = chatInput.value.trim();
  if (!query) return;

  chatInput.value = '';
  chatInput.style.height = 'auto';

  appendMessage('user', query);
  const thinking = appendThinking();

  try {
    const res = await fetch('/api/query/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrf(),
      },
      body: JSON.stringify({ query, top_k: 5 }),
    });

    thinking.remove();
    const data = await res.json();

    if (!res.ok) {
      appendMessage('assistant', '⚠️ ' + (data.detail || 'Unknown error'));
      return;
    }

    appendMessage('assistant', data.answer, data.sources || []);
  } catch (err) {
    thinking.remove();
    appendMessage('assistant', '⚠️ Could not reach the backend. Is it running?');
  }
});

// ── File upload ────────────────────────────────────────────────
const uploadZone = document.getElementById('upload-zone');
const fileInput  = document.getElementById('file-input');
const btnUpload  = document.getElementById('btn-upload');

let selectedFiles = [];

uploadZone.addEventListener('dragover', e => {
  e.preventDefault();
  uploadZone.classList.add('drag-over');
});
uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('drag-over'));
uploadZone.addEventListener('drop', e => {
  e.preventDefault();
  uploadZone.classList.remove('drag-over');
  selectedFiles = Array.from(e.dataTransfer.files);
  updateUploadLabel();
});

fileInput.addEventListener('change', () => {
  selectedFiles = Array.from(fileInput.files);
  updateUploadLabel();
});

function updateUploadLabel() {
  const textEl = uploadZone.querySelector('.upload-text');
  if (selectedFiles.length) {
    textEl.textContent = selectedFiles.map(f => f.name).join(', ');
    btnUpload.disabled = false;
  } else {
    textEl.textContent = 'Drop files or click to browse';
    btnUpload.disabled = true;
  }
}

btnUpload.addEventListener('click', async () => {
  if (!selectedFiles.length) return;

  const origText     = btnUpload.textContent;
  btnUpload.disabled = true;
  btnUpload.textContent = 'Uploading…';

  const form = new FormData();
  selectedFiles.forEach(f => form.append('files', f));

  try {
    const res = await fetch('/api/index/files/', {
      method: 'POST',
      headers: { 'X-CSRFToken': getCsrf() },
      body: form,
    });
    const data = await res.json();
    if (res.ok) {
      toast('✅ ' + data.message, 'success');
      selectedFiles = [];
      fileInput.value = '';
      updateUploadLabel();
    } else {
      toast('❌ ' + (data.detail || 'Upload failed'), 'error');
    }
  } catch {
    toast('❌ Upload failed — backend unreachable', 'error');
  } finally {
    btnUpload.disabled = false;
    btnUpload.textContent = origText;
  }
});

// ── Sample data ────────────────────────────────────────────────
document.getElementById('btn-sample').addEventListener('click', async function () {
  const origText    = this.textContent;
  this.disabled     = true;
  this.textContent  = 'Indexing…';
  toast('Indexing sample documents…', 'info');

  try {
    const res  = await fetch('/api/index/sample/', {
      method: 'POST',
      headers: { 'X-CSRFToken': getCsrf() },
    });
    const data = await res.json();
    toast(res.ok ? '✅ ' + data.message : '❌ ' + (data.detail || 'Failed'),
          res.ok ? 'success' : 'error');
  } catch {
    toast('❌ Backend unreachable', 'error');
  } finally {
    this.disabled    = false;
    this.textContent = origText;
  }
});

// ── Reset ──────────────────────────────────────────────────────
document.getElementById('btn-reset').addEventListener('click', async function () {
  if (!confirm('Reset the database? All indexed documents will be deleted.')) return;

  const origText    = this.textContent;
  this.disabled     = true;
  this.textContent  = 'Resetting…';

  try {
    const res  = await fetch('/api/reset/', {
      method: 'POST',
      headers: { 'X-CSRFToken': getCsrf() },
    });
    const data = await res.json();
    toast(res.ok ? '🗑️ ' + data.message : '❌ ' + (data.detail || 'Reset failed'),
          res.ok ? 'info' : 'error');
  } catch {
    toast('❌ Backend unreachable', 'error');
  } finally {
    this.disabled    = false;
    this.textContent = origText;
  }
});
