const form = document.querySelector('#composer');
const input = document.querySelector('#message');
const chat = document.querySelector('#chat');
const sendButton = document.querySelector('#send');
const micButton = document.querySelector('#mic');
const voiceHint = document.querySelector('#voice-hint');
const welcome = document.querySelector('#welcome');
const statusLabel = document.querySelector('#status');
const voiceToggle = document.querySelector('#voice-toggle');
const voiceLanguage = document.querySelector('#voice-language');

let history = [];
let recognition = null;
let listening = false;
let shouldSubmitSpeech = false;
let voiceReplies = false;
let replySpeechLanguage = 'en-US';

function setStatus(value) { statusLabel.textContent = value; }

function detectLanguage(text) {
  if (/[\u0600-\u06FF]/.test(text)) return 'fa-IR';
  const value = ` ${text.toLowerCase()} `;
  if (/[àâçéèêëîïôùûüÿœ]/i.test(text) || /\b(bonjour|merci|salut|avec|pour|vous|nous|je|une|des|les|est|mon|musique|cherche)\b/.test(value)) return 'fr-FR';
  if (/[äöüß]/i.test(text) || /\b(der|die|das|und|ich|nicht|bitte|danke|suche)\b/.test(value)) return 'de-DE';
  if (/[¿¡ñáéíóú]/i.test(text) || /\b(hola|gracias|por|para|busco|una|los|las|que|con)\b/.test(value)) return 'es-ES';
  return 'en-US';
}

function addBubble(text, role, extra = '') {
  const node = document.createElement('div');
  node.className = `bubble ${role} ${extra}`.trim();
  node.textContent = text;
  chat.appendChild(node);
  chat.scrollTop = chat.scrollHeight;
  return node;
}
function speak(text) {
  if (!voiceReplies || !('speechSynthesis' in window)) return;
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = replySpeechLanguage || voiceLanguage.value;
  utterance.rate = 0.96;
  const prefix = utterance.lang.split('-')[0].toLowerCase();
  const voice = window.speechSynthesis.getVoices().find(item => item.lang.toLowerCase().startsWith(prefix));
  if (voice) utterance.voice = voice;
  window.speechSynthesis.speak(utterance);
}
async function submitMessage(rawText) {
  const text = rawText.trim();
  if (!text || sendButton.disabled) return;
  welcome.hidden = true;
  addBubble(text, 'user');
  replySpeechLanguage = detectLanguage(text);
  input.value = '';
  input.style.height = 'auto';
  sendButton.disabled = true;
  micButton.disabled = true;
  setStatus('Thinking…');
  const pending = addBubble('Working on your request…', 'assistant', 'pending');
  history.push({ role: 'user', content: text });
  try {
    const response = await fetch('/api/chat', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: history })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'The service could not be reached.');
    history = Array.isArray(data.messages) ? data.messages : history;
    pending.remove();
    addBubble(data.answer || 'Done.', 'assistant');
    if (data.fallback_used) {
      addBubble(`The primary AI model was temporarily unavailable. NOVA completed this request using the backup model: ${data.model_used}.`, 'assistant', 'model-notice');
      setStatus('Backup model');
    } else {
      setStatus('Ready');
    }
    speak(data.answer || 'Done.');
  } catch (error) {
    pending.remove();
    addBubble(`Error: ${error.message}`, 'assistant', 'error');
    setStatus('Connection error');
  } finally {
    sendButton.disabled = false;
    micButton.disabled = !recognition;
    input.focus();
  }
}

function initSpeech() {
  const SpeechAPI = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechAPI) {
    micButton.disabled = true;
    voiceHint.textContent = 'Speech recognition is not supported in this browser. Try Chrome.';
    return;
  }
  recognition = new SpeechAPI();
  recognition.lang = voiceLanguage.value;
  recognition.continuous = false;
  recognition.interimResults = true;
  recognition.maxAlternatives = 1;

  recognition.onstart = () => {
    listening = true;
    shouldSubmitSpeech = true;
    micButton.classList.add('listening');
    micButton.setAttribute('aria-label', 'Stop voice input');
    voiceHint.textContent = 'Listening… Tap the microphone again to stop.';
    setStatus('Listening');
  };
  recognition.onresult = event => {
    let finalText = '';
    let partialText = '';
    for (let i = event.resultIndex; i < event.results.length; i++) {
      const transcript = event.results[i][0].transcript;
      if (event.results[i].isFinal) finalText += transcript;
      else partialText += transcript;
    }
    if (finalText) {
      input.value = `${input.value} ${finalText}`.trim();
      input.dispatchEvent(new Event('input'));
      voiceHint.textContent = 'Speech recognized. Preparing your request…';
    } else if (partialText) {
      voiceHint.textContent = `Recognizing: ${partialText}`;
    }
  };
  recognition.onerror = event => {
    shouldSubmitSpeech = false;
    const errors = {
      'not-allowed': 'Microphone permission denied. Allow microphone access in your browser.',
      'no-speech': 'No speech detected. Please try again.',
      'network': 'Speech recognition requires an internet connection.',
      'audio-capture': 'No microphone is available.'
    };
    voiceHint.textContent = errors[event.error] || `Microphone error: ${event.error}`;
    setStatus('Ready');
  };
  recognition.onend = () => {
    listening = false;
    micButton.classList.remove('listening');
    micButton.setAttribute('aria-label', 'Start voice input');
    if (shouldSubmitSpeech && input.value.trim()) {
      shouldSubmitSpeech = false;
      voiceHint.textContent = 'Voice request submitted.';
      submitMessage(input.value);
    } else {
      shouldSubmitSpeech = false;
      setStatus('Ready');
    }
  };
}

micButton.addEventListener('click', () => {
  if (!recognition) return;
  if (listening) { recognition.stop(); return; }
  input.value = '';
  recognition.lang = voiceLanguage.value;
  try { recognition.start(); }
  catch { voiceHint.textContent = 'Microphone is busy. Please try again in a moment.'; }
});
voiceLanguage.addEventListener('change', () => {
  if (recognition) recognition.lang = voiceLanguage.value;
  voiceHint.textContent = `Voice input language: ${voiceLanguage.options[voiceLanguage.selectedIndex].text}`;
});
voiceToggle.addEventListener('click', () => {
  voiceReplies = !voiceReplies;
  voiceToggle.classList.toggle('active', voiceReplies);
  if (!voiceReplies && 'speechSynthesis' in window) window.speechSynthesis.cancel();
  else speak('Voice replies are enabled.');
});
form.addEventListener('submit', event => {
  event.preventDefault();
  if (listening) { recognition.stop(); return; }
  submitMessage(input.value);
});
input.addEventListener('input', () => {
  input.style.height = 'auto';
  input.style.height = `${Math.min(input.scrollHeight, 150)}px`;
});
input.addEventListener('keydown', event => {
  if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); form.requestSubmit(); }
});
document.querySelectorAll('[data-prompt]').forEach(button => button.addEventListener('click', () => submitMessage(button.dataset.prompt)));
initSpeech();

// User-selectable file access scope. Full mode follows the current Windows account's permissions.
const settingsToggle = document.querySelector('#settings-toggle');
const settingsPanel = document.querySelector('#settings-panel');
const settingsClose = document.querySelector('#settings-close');
const accessStatus = document.querySelector('#access-status');

async function loadAccessMode() {
  try {
    const response = await fetch('/api/settings/access');
    const data = await response.json();
    const selected = document.querySelector(`input[name="access-mode"][value="${data.mode}"]`);
    if (selected) selected.checked = true;
    accessStatus.textContent = data.mode === 'full'
      ? 'Current mode: Full User Access'
      : 'Current mode: Limited Access (NOVA workspace only)';
  } catch {
    accessStatus.textContent = 'Could not load access settings.';
  }
}
settingsToggle.addEventListener('click', () => {
  settingsPanel.hidden = !settingsPanel.hidden;
  if (!settingsPanel.hidden) loadAccessMode();
});
settingsClose.addEventListener('click', () => { settingsPanel.hidden = true; });
document.querySelectorAll('input[name="access-mode"]').forEach(radio => {
  radio.addEventListener('change', async () => {
    accessStatus.textContent = 'Saving…';
    try {
      const response = await fetch('/api/settings/access', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({mode: radio.value})
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Could not save settings.');
      accessStatus.textContent = data.mode === 'full'
        ? 'Full User Access enabled. NOVA is still limited by the current Windows account permissions.'
        : 'Limited Access enabled.';
    } catch (error) {
      accessStatus.textContent = `Error: ${error.message}`;
    }
  });
});
