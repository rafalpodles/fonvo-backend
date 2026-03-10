// Fonvo Admin — AI Configuration
// ================================

// API base is relative — admin UI is served from the same backend
const API_BASE = '/api/v1';

// Auth state
let authToken = localStorage.getItem('fonvo_admin_token');

// State
let prompts = [];
let models = [];
let selectedPromptKey = null;
let dirtyPrompts = new Set();
let dirtyModels = new Set();
let currentTab = 'prompts';

// Model presets for quick selection in admin UI
const MODEL_PRESETS = {
  tts: [
    { provider: 'elevenlabs', model_id: 'eleven_flash_v2_5', display_name: 'ElevenLabs Flash v2.5', note: '<75ms latency, 32 langs' },
    { provider: 'elevenlabs', model_id: 'eleven_v3', display_name: 'ElevenLabs v3', note: 'Best quality, 70+ langs' },
    { provider: 'elevenlabs', model_id: 'eleven_turbo_v2_5', display_name: 'ElevenLabs Turbo v2.5', note: 'Balanced latency/quality' },
    { provider: 'openai', model_id: 'tts-1', display_name: 'OpenAI TTS-1', note: 'Low latency, lower quality' },
    { provider: 'openai', model_id: 'tts-1-hd', display_name: 'OpenAI TTS-1 HD', note: 'Best OpenAI quality' },
    { provider: 'openai', model_id: 'gpt-4o-mini-tts', display_name: 'OpenAI GPT-4o Mini TTS', note: 'Tone/emotion control' },
  ],
  tts_streaming: [
    { provider: 'elevenlabs', model_id: 'eleven_flash_v2_5', display_name: 'ElevenLabs Flash v2.5', note: 'WebSocket streaming' },
    { provider: 'elevenlabs', model_id: 'eleven_v3', display_name: 'ElevenLabs v3', note: 'Best quality streaming' },
    { provider: 'elevenlabs', model_id: 'eleven_turbo_v2_5', display_name: 'ElevenLabs Turbo v2.5', note: 'Balanced streaming' },
  ],
  stt: [
    { provider: 'openai', model_id: 'gpt-4o-mini-transcribe', display_name: 'OpenAI GPT-4o Mini Transcribe', note: '~320ms, good accuracy' },
    { provider: 'openai', model_id: 'gpt-4o-transcribe', display_name: 'OpenAI GPT-4o Transcribe', note: 'Best OpenAI accuracy' },
    { provider: 'openai', model_id: 'whisper-1', display_name: 'OpenAI Whisper', note: 'Legacy, 99 langs' },
    { provider: 'elevenlabs', model_id: 'scribe_v2', display_name: 'ElevenLabs Scribe v2', note: '150ms, fastest STT' },
  ],
  chat: [
    { provider: 'openai', model_id: 'gpt-4o', display_name: 'GPT-4o', note: 'Default chat model' },
    { provider: 'openai', model_id: 'gpt-4o-mini', display_name: 'GPT-4o Mini', note: 'Faster, cheaper' },
    { provider: 'openrouter', model_id: 'google/gemini-2.5-flash', display_name: 'Gemini 2.5 Flash', note: 'Via OpenRouter' },
    { provider: 'openrouter', model_id: 'google/gemini-2.5-pro', display_name: 'Gemini 2.5 Pro', note: 'Via OpenRouter' },
    { provider: 'openrouter', model_id: 'anthropic/claude-sonnet-4.6', display_name: 'Claude Sonnet 4.6', note: 'Via OpenRouter' },
  ],
};

// Category definitions for prompt grouping
const PROMPT_CATEGORIES = [
  { prefix: 'conversation.', label: 'Conversation' },
  { prefix: 'analysis.', label: 'Analysis' },
  { prefix: 'vocabulary.', label: 'Vocabulary' },
  { prefix: 'suggestions.', label: 'Suggestions' },
];

function categorizePrompt(key) {
  for (const cat of PROMPT_CATEGORIES) {
    if (key.startsWith(cat.prefix)) return cat.label;
  }
  return 'Other';
}

// ============================================================
// Auth
// ============================================================

async function handleLogin(event) {
  event.preventDefault();
  const btn = document.getElementById('loginBtn');
  const errEl = document.getElementById('loginError');
  btn.disabled = true;
  btn.textContent = 'Logging in...';
  errEl.classList.add('hidden');

  try {
    const res = await fetch(`${API_BASE}/admin/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: document.getElementById('loginUsername').value,
        password: document.getElementById('loginPassword').value,
      }),
    });

    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || 'Invalid credentials');
    }

    const data = await res.json();
    authToken = data.token;
    localStorage.setItem('fonvo_admin_token', authToken);
    showMainApp();
  } catch (err) {
    errEl.textContent = err.message;
    errEl.classList.remove('hidden');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Log in';
  }
}

function handleLogout() {
  authToken = null;
  localStorage.removeItem('fonvo_admin_token');
  document.getElementById('mainApp').classList.add('hidden');
  document.getElementById('loginScreen').classList.remove('hidden');
  document.getElementById('loginPassword').value = '';
}

function showMainApp() {
  document.getElementById('loginScreen').classList.add('hidden');
  document.getElementById('mainApp').classList.remove('hidden');
  init();
}

// ============================================================
// API (with auth headers)
// ============================================================

function authHeaders() {
  const headers = { 'Content-Type': 'application/json' };
  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }
  return headers;
}

async function apiGet(path) {
  const res = await fetch(`${API_BASE}${path}`, { headers: authHeaders() });
  if (res.status === 401) {
    handleLogout();
    showToast('Session expired — please log in again', 'error');
    throw new Error('Unauthorized');
  }
  if (!res.ok) throw new Error(`GET ${path} failed: ${res.status}`);
  return res.json();
}

async function apiPut(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'PUT',
    headers: authHeaders(),
    body: JSON.stringify(body),
  });
  if (res.status === 401) {
    handleLogout();
    showToast('Session expired — please log in again', 'error');
    throw new Error('Unauthorized');
  }
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`PUT ${path} failed: ${res.status} — ${text}`);
  }
  return res.json();
}

// ============================================================
// Data loading
// ============================================================

async function loadPrompts() {
  try {
    prompts = await apiGet('/config/prompts');
    prompts.sort((a, b) => a.key.localeCompare(b.key));
    renderPromptList();
    setConnectionStatus(true);
  } catch (err) {
    if (err.message === 'Unauthorized') return;
    console.error('Failed to load prompts:', err);
    setConnectionStatus(false);
    showToast('Failed to load prompts', 'error');
  }
}

async function loadModels() {
  try {
    models = await apiGet('/config/models');
    models.sort((a, b) => a.key.localeCompare(b.key));
    renderModelList();
    setConnectionStatus(true);
  } catch (err) {
    if (err.message === 'Unauthorized') return;
    console.error('Failed to load models:', err);
    setConnectionStatus(false);
    showToast('Failed to load models', 'error');
  }
}

// ============================================================
// Tab switching
// ============================================================

function switchTab(tab) {
  currentTab = tab;
  document.getElementById('promptsTab').classList.toggle('hidden', tab !== 'prompts');
  document.getElementById('modelsTab').classList.toggle('hidden', tab !== 'models');

  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.remove('active');
    btn.classList.remove('border-brand-500', 'text-brand-700');
    btn.classList.add('border-transparent', 'text-gray-500');
  });

  const activeBtn = document.getElementById(tab === 'prompts' ? 'tabPrompts' : 'tabModels');
  activeBtn.classList.add('active');
  activeBtn.classList.remove('border-transparent', 'text-gray-500');
  activeBtn.classList.add('border-brand-500', 'text-brand-700');
}

// ============================================================
// Prompt list rendering
// ============================================================

function renderPromptList() {
  const container = document.getElementById('promptList');
  const searchTerm = document.getElementById('promptSearch').value.toLowerCase();

  const filtered = prompts.filter(p => p.key.toLowerCase().includes(searchTerm));

  // Group by category
  const grouped = {};
  for (const p of filtered) {
    const cat = categorizePrompt(p.key);
    if (!grouped[cat]) grouped[cat] = [];
    grouped[cat].push(p);
  }

  // Render order
  const order = ['Conversation', 'Analysis', 'Vocabulary', 'Suggestions', 'Other'];
  let html = '';

  for (const cat of order) {
    const items = grouped[cat];
    if (!items || items.length === 0) continue;

    html += `<div class="prompt-category">${cat}</div>`;
    for (const p of items) {
      const isActive = p.key === selectedPromptKey;
      const isDirty = dirtyPrompts.has(p.key);
      const shortKey = p.key.includes('.') ? p.key.split('.').slice(1).join('.') : p.key;
      html += `<div class="prompt-item${isActive ? ' active' : ''}${isDirty ? ' dirty' : ''}" onclick="selectPrompt('${p.key}')" title="${p.key}">${shortKey}</div>`;
    }
  }

  if (!html) {
    html = '<div class="px-3 py-4 text-center text-sidebar-muted text-sm">No prompts found</div>';
  }

  container.innerHTML = html;
}

function filterPrompts() {
  renderPromptList();
}

// ============================================================
// Prompt editor
// ============================================================

function selectPrompt(key) {
  selectedPromptKey = key;
  const prompt = prompts.find(p => p.key === key);
  if (!prompt) return;

  document.getElementById('promptEmpty').classList.add('hidden');
  document.getElementById('promptForm').classList.remove('hidden');

  document.getElementById('promptKey').textContent = prompt.key;
  document.getElementById('promptDescription').value = prompt.description || '';
  document.getElementById('promptText').value = prompt.prompt_text || '';

  const meta = [];
  if (prompt.version) meta.push(`v${prompt.version}`);
  if (prompt.updated_at) meta.push(`Updated: ${formatDate(prompt.updated_at)}`);
  document.getElementById('promptMeta').textContent = meta.join(' · ');

  renderPlaceholders(prompt.placeholders || []);
  updatePreview();
  updateUnsavedIndicator();
  renderPromptList();
}

function renderPlaceholders(placeholders) {
  const container = document.getElementById('promptPlaceholders');
  container.innerHTML = placeholders.map(ph =>
    `<span class="placeholder-tag">{${ph}}<button onclick="removePlaceholder('${ph}')">&times;</button></span>`
  ).join('');
}

function getEditedPlaceholders() {
  const tags = document.querySelectorAll('#promptPlaceholders .placeholder-tag');
  return Array.from(tags).map(tag => {
    const text = tag.childNodes[0].textContent.trim();
    return text.replace(/^\{/, '').replace(/\}$/, '');
  });
}

function addPlaceholder() {
  const input = document.getElementById('newPlaceholder');
  const val = input.value.trim().replace(/[{}]/g, '');
  if (!val) return;

  const current = getEditedPlaceholders();
  if (current.includes(val)) {
    input.value = '';
    return;
  }

  current.push(val);
  renderPlaceholders(current);
  input.value = '';
  markPromptDirty();
}

function removePlaceholder(name) {
  const current = getEditedPlaceholders().filter(p => p !== name);
  renderPlaceholders(current);
  markPromptDirty();
}

function markPromptDirty() {
  if (selectedPromptKey) {
    dirtyPrompts.add(selectedPromptKey);
    updateUnsavedIndicator();
    renderPromptList();
  }
}

function updateUnsavedIndicator() {
  const el = document.getElementById('promptUnsaved');
  if (selectedPromptKey && dirtyPrompts.has(selectedPromptKey)) {
    el.classList.remove('hidden');
  } else {
    el.classList.add('hidden');
  }
}

function updatePreview() {
  const text = document.getElementById('promptText').value;
  const preview = document.getElementById('promptPreview');
  // Escape HTML then highlight placeholders
  const escaped = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
  const highlighted = escaped.replace(
    /\{(\w+)\}/g,
    '<span class="placeholder-highlight">{$1}</span>'
  );
  preview.innerHTML = highlighted;
}

async function saveCurrentPrompt() {
  if (!selectedPromptKey) return;

  const btn = document.getElementById('promptSaveBtn');
  btn.disabled = true;
  btn.textContent = 'Saving...';

  try {
    const body = {
      prompt_text: document.getElementById('promptText').value,
      description: document.getElementById('promptDescription').value,
      placeholders: getEditedPlaceholders(),
    };

    const updated = await apiPut(`/config/prompts/${selectedPromptKey}`, body);

    // Update local state
    const idx = prompts.findIndex(p => p.key === selectedPromptKey);
    if (idx >= 0 && updated) {
      prompts[idx] = { ...prompts[idx], ...updated };
    }

    dirtyPrompts.delete(selectedPromptKey);
    updateUnsavedIndicator();
    renderPromptList();

    // Refresh meta
    if (updated && updated.version) {
      const meta = [];
      meta.push(`v${updated.version}`);
      if (updated.updated_at) meta.push(`Updated: ${formatDate(updated.updated_at)}`);
      document.getElementById('promptMeta').textContent = meta.join(' · ');
    }

    showToast('Prompt saved successfully', 'success');
  } catch (err) {
    console.error('Save failed:', err);
    showToast(`Save failed: ${err.message}`, 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Save';
  }
}

// ============================================================
// Models
// ============================================================

function renderModelList() {
  const container = document.getElementById('modelList');

  if (models.length === 0) {
    container.innerHTML = '<div class="text-center text-gray-400 py-12">No models configured</div>';
    return;
  }

  container.innerHTML = models.map(m => {
    const presets = MODEL_PRESETS[m.key] || [];
    const presetDropdown = presets.length > 0 ? `
      <div class="mb-4">
        <label class="block text-xs font-medium text-gray-500 mb-1">Quick Select</label>
        <select onchange="applyPreset('${m.key}', this.value)" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:border-brand-500 focus:ring-1 focus:ring-brand-500 focus:outline-none bg-white">
          <option value="">— Choose a preset —</option>
          ${presets.map((p, i) => `<option value="${i}" ${p.model_id === m.model_id ? 'selected' : ''}>${p.display_name} — ${p.note}</option>`).join('')}
        </select>
      </div>
    ` : '';

    const extraJson = m.extra_config && Object.keys(m.extra_config).length > 0
      ? JSON.stringify(m.extra_config, null, 2)
      : '{}';

    return `
    <div class="model-card${dirtyModels.has(m.key) ? ' dirty' : ''}" id="model-${m.key}">
      <div class="flex items-start justify-between mb-4">
        <div>
          <h3 class="font-mono font-semibold text-lg text-gray-800">${escapeHtml(m.key)}</h3>
          ${m.updated_at ? `<p class="text-xs text-gray-400 mt-0.5">Updated: ${formatDate(m.updated_at)}</p>` : ''}
        </div>
        <div class="flex items-center gap-2">
          <span class="model-unsaved text-xs text-brand-600 font-medium ${dirtyModels.has(m.key) ? '' : 'hidden'}">Unsaved</span>
          <button onclick="saveModel('${m.key}')" class="model-save-btn px-4 py-1.5 bg-brand-500 text-white text-sm font-medium rounded-lg hover:bg-brand-600 disabled:opacity-50 transition-colors">Save</button>
        </div>
      </div>
      ${presetDropdown}
      <div class="grid grid-cols-3 gap-4">
        <div>
          <label class="block text-xs font-medium text-gray-500 mb-1">Provider</label>
          <input type="text" value="${escapeAttr(m.provider || '')}" class="model-provider w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:border-brand-500 focus:ring-1 focus:ring-brand-500 focus:outline-none" oninput="markModelDirty('${m.key}')">
        </div>
        <div>
          <label class="block text-xs font-medium text-gray-500 mb-1">Model ID</label>
          <input type="text" value="${escapeAttr(m.model_id || '')}" class="model-model-id w-full border border-gray-300 rounded-lg px-3 py-2 text-sm font-mono focus:border-brand-500 focus:ring-1 focus:ring-brand-500 focus:outline-none" oninput="markModelDirty('${m.key}')">
        </div>
        <div>
          <label class="block text-xs font-medium text-gray-500 mb-1">Display Name</label>
          <input type="text" value="${escapeAttr(m.display_name || '')}" class="model-display-name w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:border-brand-500 focus:ring-1 focus:ring-brand-500 focus:outline-none" oninput="markModelDirty('${m.key}')">
        </div>
      </div>
      <div class="mt-3">
        <label class="block text-xs font-medium text-gray-500 mb-1">Extra Config (JSON)</label>
        <textarea class="model-extra-config w-full border border-gray-300 rounded-lg px-3 py-2 text-sm font-mono focus:border-brand-500 focus:ring-1 focus:ring-brand-500 focus:outline-none resize-none" rows="2" oninput="markModelDirty('${m.key}')">${escapeHtml(extraJson)}</textarea>
      </div>
    </div>
  `}).join('');
}

function applyPreset(modelKey, presetIndex) {
  if (presetIndex === '') return;
  const presets = MODEL_PRESETS[modelKey];
  if (!presets) return;
  const preset = presets[parseInt(presetIndex)];
  if (!preset) return;

  const card = document.getElementById(`model-${modelKey}`);
  if (!card) return;

  card.querySelector('.model-provider').value = preset.provider;
  card.querySelector('.model-model-id').value = preset.model_id;
  card.querySelector('.model-display-name').value = preset.display_name;
  markModelDirty(modelKey);
}

function markModelDirty(key) {
  dirtyModels.add(key);
  const card = document.getElementById(`model-${key}`);
  if (card) {
    card.classList.add('dirty');
    card.querySelector('.model-unsaved').classList.remove('hidden');
  }
}

async function saveModel(key) {
  const card = document.getElementById(`model-${key}`);
  if (!card) return;

  const btn = card.querySelector('.model-save-btn');
  btn.disabled = true;
  btn.textContent = 'Saving...';

  try {
    let extraConfig = {};
    try {
      extraConfig = JSON.parse(card.querySelector('.model-extra-config').value || '{}');
    } catch {
      throw new Error('Invalid JSON in extra config');
    }

    const body = {
      provider: card.querySelector('.model-provider').value.trim(),
      model_id: card.querySelector('.model-model-id').value.trim(),
      display_name: card.querySelector('.model-display-name').value.trim(),
      extra_config: extraConfig,
    };

    const updated = await apiPut(`/config/models/${key}`, body);

    // Update local state
    const idx = models.findIndex(m => m.key === key);
    if (idx >= 0 && updated) {
      models[idx] = { ...models[idx], ...updated };
    }

    dirtyModels.delete(key);
    card.classList.remove('dirty');
    card.querySelector('.model-unsaved').classList.add('hidden');

    showToast(`Model "${key}" saved`, 'success');
  } catch (err) {
    console.error('Save failed:', err);
    showToast(`Save failed: ${err.message}`, 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Save';
  }
}

// ============================================================
// UI helpers
// ============================================================

function setConnectionStatus(ok) {
  const el = document.getElementById('connectionStatus');
  if (ok) {
    el.textContent = 'Connected';
    el.className = 'text-xs px-2 py-1 rounded-full bg-green-900/30 text-green-400';
  } else {
    el.textContent = 'Connection error';
    el.className = 'text-xs px-2 py-1 rounded-full bg-red-900/30 text-red-400';
  }
}

let toastTimer = null;
function showToast(message, type = 'success') {
  const toast = document.getElementById('toast');
  const inner = toast.querySelector('div');

  inner.textContent = message;
  if (type === 'success') {
    inner.className = 'px-4 py-3 rounded-lg shadow-lg text-sm font-medium flex items-center gap-2 bg-green-600 text-white';
  } else {
    inner.className = 'px-4 py-3 rounded-lg shadow-lg text-sm font-medium flex items-center gap-2 bg-red-600 text-white';
  }

  toast.classList.remove('hidden', 'hide');
  toast.classList.add('show');

  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toast.classList.remove('show');
    toast.classList.add('hide');
    setTimeout(() => toast.classList.add('hidden'), 200);
  }, 3000);
}

function formatDate(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleDateString('en-GB', {
    day: 'numeric', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

function escapeAttr(str) {
  return str.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// ============================================================
// Keyboard shortcuts
// ============================================================

document.addEventListener('keydown', (e) => {
  // Cmd+S / Ctrl+S to save
  if ((e.metaKey || e.ctrlKey) && e.key === 's') {
    e.preventDefault();
    if (currentTab === 'prompts' && selectedPromptKey) {
      saveCurrentPrompt();
    }
  }
});

// ============================================================
// Init
// ============================================================

async function init() {
  await Promise.all([loadPrompts(), loadModels()]);
}

// Check for existing token on page load
if (authToken) {
  showMainApp();
} else {
  document.getElementById('loginScreen').classList.remove('hidden');
}
