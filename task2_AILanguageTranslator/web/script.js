// ==================== INITIALIZATION ====================
let allLanguages = { source: {}, target: {} };
let translationHistory = [];
let currentTheme = localStorage.getItem('theme') || 'light';
let recognition = null;

document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

async function initializeApp() {
    // Set theme
    if (currentTheme === 'dark') {
        document.body.classList.add('dark-mode');
    }

    // Load translations and languages
    await loadLanguages();
    await loadHistory();

    // Setup voice recognition if available
    setupVoiceRecognition();
}

// ==================== THEME MANAGEMENT ====================
function toggleTheme() {
    document.body.classList.toggle('dark-mode');
    currentTheme = document.body.classList.contains('dark-mode') ? 'dark' : 'light';
    localStorage.setItem('theme', currentTheme);
}

// ==================== SECTION NAVIGATION ====================
function showSection(sectionName) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });

    // Remove active from all nav buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected section
    document.getElementById(sectionName).classList.add('active');

    // Mark nav button as active
    event.target.closest('.nav-btn').classList.add('active');

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ==================== LANGUAGE MANAGEMENT ====================
async function loadLanguages() {
    try {
        const response = await fetch('/api/languages');
        if (!response.ok) throw new Error('Failed to load languages');
        
        allLanguages = await response.json();
        
        // Populate source languages
        const sourceSelect = document.getElementById('sourceLanguage');
        sourceSelect.innerHTML = '';
        allLanguages.source.forEach((name) => {
            const option = document.createElement('option');
            option.value = name;
            option.textContent = name;
            sourceSelect.appendChild(option);
        });

        // Populate target languages
        const targetSelect = document.getElementById('targetLanguage');
        targetSelect.innerHTML = '';
        allLanguages.target.forEach((name) => {
            const option = document.createElement('option');
            option.value = name;
            option.textContent = name;
            targetSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading languages:', error);
        showError('Failed to load languages');
    }
}

// ==================== TRANSLATION FUNCTIONS ====================
function handleTranslationInput() {
    const text = document.getElementById('sourceText').value;
    document.getElementById('charCount').textContent = text.length;
    // Just count characters - no auto-translate
}

async function performTranslation() {
    const sourceText = document.getElementById('sourceText').value.trim();
    
    if (!sourceText) {
        showError('Please enter text to translate');
        return;
    }

    const sourceLanguage = document.getElementById('sourceLanguage').value;
    const targetLanguage = document.getElementById('targetLanguage').value;

    console.log('Translation request:', { text: sourceText, source: sourceLanguage, target: targetLanguage });

    showLoading(true);
    hideError();

    try {
        const response = await fetch('/api/translate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: sourceText,
                source: sourceLanguage,
                target: targetLanguage
            })
        });

        console.log('API Response status:', response.status);

        if (!response.ok) {
            const error = await response.json();
            console.error('API Error:', error);
            throw new Error(error.error || 'Translation failed');
        }

        const result = await response.json();
        console.log('Translation result:', result);
        
        document.getElementById('translationResult').value = result.translatedText;
        console.log('Updated div with:', result.translatedText);

        // Add to history
        await loadHistory();
    } catch (error) {
        console.error('Translation error:', error);
        showError(error.message || 'Translation failed. Please try again.');
    } finally {
        showLoading(false);
    }
}

function swapLanguages() {
    const sourceSelect = document.getElementById('sourceLanguage');
    const targetSelect = document.getElementById('targetLanguage');
    
    // Swap values
    const temp = sourceSelect.value;
    sourceSelect.value = targetSelect.value;
    targetSelect.value = temp;

    // Swap texts
    const sourceText = document.getElementById('sourceText');
    const resultText = document.getElementById('translationResult');
    
    if (resultText.value && resultText.value !== 'Your translation will appear here...') {
        const temp = sourceText.value;
        sourceText.value = resultText.value;
        resultText.value = temp;
    }
}

function copyTranslation() {
    const resultText = document.getElementById('translationResult');
    if (resultText.value && resultText.value !== 'Your translation will appear here...') {
        navigator.clipboard.writeText(resultText.value).then(() => {
            showNotification('Copied to clipboard!');
        }).catch(() => {
            showError('Failed to copy');
        });
    }
}

function speakTranslation() {
    const text = document.getElementById('translationResult').value;
    if (!text || text === 'Your translation will appear here...') {
        showError('No translation to speak');
        return;
    }

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    const targetLangName = document.getElementById('targetLanguage').value;

    const nameMap = {
        'afrikaans': 'af', 'albanian': 'sq', 'amharic': 'am', 'arabic': 'ar', 'armenian': 'hy', 'azerbaijani': 'az',
        'basque': 'eu', 'belarusian': 'be', 'bengali': 'bn', 'bosnian': 'bs', 'bulgarian': 'bg', 'catalan': 'ca',
        'cebuano': 'ceb', 'chichewa': 'ny', 'chinese': 'zh', 'corsican': 'co', 'croatian': 'hr', 'czech': 'cs',
        'danish': 'da', 'dutch': 'nl', 'english': 'en', 'esperanto': 'eo', 'estonian': 'et', 'filipino': 'tl',
        'finnish': 'fi', 'french': 'fr', 'frisian': 'fy', 'galician': 'gl', 'georgian': 'ka', 'german': 'de',
        'greek': 'el', 'gujarati': 'gu', 'haitian creole': 'ht', 'hausa': 'ha', 'hawaiian': 'haw', 'hebrew': 'he',
        'hindi': 'hi', 'hmong': 'hmn', 'hungarian': 'hu', 'icelandic': 'is', 'igbo': 'ig', 'indonesian': 'id',
        'irish': 'ga', 'italian': 'it', 'japanese': 'ja', 'javanese': 'jw', 'kannada': 'kn', 'kazakh': 'kk',
        'khmer': 'km', 'korean': 'ko', 'kurdish': 'ku', 'kyrgyz': 'ky', 'lao': 'lo', 'latin': 'la',
        'latvian': 'lv', 'lithuanian': 'lt', 'luxembourgish': 'lb', 'macedonian': 'mk', 'malagasy': 'mg',
        'malay': 'ms', 'malayalam': 'ml', 'maltese': 'mt', 'maori': 'mi', 'marathi': 'mr', 'mongolian': 'mn',
        'myanmar': 'my', 'nepali': 'ne', 'norwegian': 'no', 'odia': 'or', 'pashto': 'ps', 'persian': 'fa',
        'polish': 'pl', 'portuguese': 'pt', 'punjabi': 'pa', 'romanian': 'ro', 'russian': 'ru', 'samoan': 'sm',
        'scots gaelic': 'gd', 'serbian': 'sr', 'sesotho': 'st', 'shona': 'sn', 'sindhi': 'sd', 'sinhala': 'si',
        'slovak': 'sk', 'slovenian': 'sl', 'somali': 'so', 'spanish': 'es', 'sundanese': 'su', 'swahili': 'sw',
        'swedish': 'sv', 'tajik': 'tg', 'tamil': 'ta', 'telugu': 'te', 'thai': 'th', 'turkish': 'tr',
        'ukrainian': 'uk', 'urdu': 'ur', 'uyghur': 'ug', 'uzbek': 'uz', 'vietnamese': 'vi', 'welsh': 'cy',
        'xhosa': 'xh', 'yiddish': 'yi', 'yoruba': 'yo', 'zulu': 'zu'
    };

    const key = targetLangName.toLowerCase();
    if (nameMap[key]) {
        const langCode = nameMap[key];
        const voices = window.speechSynthesis.getVoices();
        const matchedVoice = voices.find(v => v.lang.toLowerCase().startsWith(langCode));
        if (matchedVoice) {
            utterance.voice = matchedVoice;
            utterance.lang = matchedVoice.lang;
        } else {
            utterance.lang = langCode;
        }
    }

    window.speechSynthesis.speak(utterance);
    showNotification('Speaking translation...');
}

function clearTranslator() {
    document.getElementById('sourceText').value = '';
    document.getElementById('translationResult').value = 'Your translation will appear here...';
    document.getElementById('charCount').textContent = '0';
}

function downloadTranslation() {
    const sourceText = document.getElementById('sourceText').value;
    const translatedText = document.getElementById('translationResult').value;
    const sourceLanguage = document.getElementById('sourceLanguage').options[document.getElementById('sourceLanguage').selectedIndex].text;
    const targetLanguage = document.getElementById('targetLanguage').options[document.getElementById('targetLanguage').selectedIndex].text;

    if (!translatedText || translatedText === 'Your translation will appear here...') {
        showError('No translation to download');
        return;
    }

    const content = `AI Translator - Translation Report
============================================

Source Language: ${sourceLanguage}
Target Language: ${targetLanguage}
Date: ${new Date().toLocaleString()}

ORIGINAL TEXT:
${sourceText}

TRANSLATED TEXT:
${translatedText}

============================================
Generated by AI Translator`;

    const blob = new Blob([content], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `translation_${Date.now()}.txt`;
    a.click();
    window.URL.revokeObjectURL(url);

    showNotification('Translation downloaded!');
}

function shareTranslation() {
    const sourceText = document.getElementById('sourceText').value;
    const translatedText = document.getElementById('translationResult').value;

    if (!translatedText || translatedText === 'Your translation will appear here...') {
        showError('No translation to share');
        return;
    }

    const text = `Check out my translation:\n\n"${sourceText}"\n\n→\n\n"${translatedText}"\n\nTranslated with AI Translator`;
    
    if (navigator.share) {
        navigator.share({
            title: 'AI Translator Translation',
            text: text
        });
    } else {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('Share text copied to clipboard!');
        });
    }
}

// ==================== VOICE RECOGNITION ====================
function setupVoiceRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
            document.querySelector('.voice-btn').classList.add('listening');
        };

        recognition.onend = () => {
            document.querySelector('.voice-btn').classList.remove('listening');
        };

        recognition.onresult = (event) => {
            let interimTranscript = '';
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    document.getElementById('sourceText').value += transcript + ' ';
                    handleTranslationInput();
                } else {
                    interimTranscript += transcript;
                }
            }
        };

        recognition.onerror = (event) => {
            showError(`Voice recognition error: ${event.error}`);
        };
    }
}

function startVoiceInput() {
    if (!recognition) {
        showError('Voice recognition not supported in your browser');
        return;
    }

    recognition.start();
}

// ==================== HISTORY MANAGEMENT ====================
async function loadHistory() {
    try {
        const response = await fetch('/api/history');
        if (!response.ok) throw new Error('Failed to load history');
        
        translationHistory = await response.json();
        renderHistory();

        // Update total translations count
        document.getElementById('totalTranslations').textContent = translationHistory.length;
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

function renderHistory(filtered = null) {
    const historyList = document.getElementById('historyList');
    const items = filtered || translationHistory;

    if (items.length === 0) {
        historyList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-inbox"></i>
                <p>No translations yet. Start translating to build your history!</p>
            </div>
        `;
        return;
    }

    historyList.innerHTML = items.map((item, index) => `
        <div class="history-item" style="animation-delay: ${index * 0.1}s;">
            <div class="history-item-header">
                <div class="history-languages">
                    <span class="badge">${item.source_language || 'Auto'}</span>
                    <i class="fas fa-arrow-right"></i>
                    <span class="badge">${item.target_language || 'Unknown'}</span>
                </div>
                <span class="history-date">${new Date(item.created_at).toLocaleDateString()}</span>
            </div>

            <div class="history-text">
                <div class="history-text-label">Original:</div>
                <div class="history-text-content">${escapeHtml(item.source_text)}</div>
            </div>

            <div class="history-text">
                <div class="history-text-label">Translation:</div>
                <div class="history-text-content">${escapeHtml(item.translated_text)}</div>
            </div>

            <div class="history-item-actions">
                <button class="history-btn" onclick="restoreTranslation('${escapeHtml(item.source_text)}', '${escapeHtml(item.translated_text)}')" title="Restore">
                    <i class="fas fa-redo"></i> Use
                </button>
                <button class="history-btn" onclick="copyHistoryItem('${escapeHtml(item.translated_text)}')" title="Copy">
                    <i class="fas fa-copy"></i> Copy
                </button>
                <button class="history-btn" onclick="deleteHistoryItem(${item.id})" title="Delete">
                    <i class="fas fa-trash"></i> Delete
                </button>
            </div>
        </div>
    `).join('');
}

function filterHistory() {
    const searchTerm = document.getElementById('searchHistory').value.toLowerCase();
    const filtered = translationHistory.filter(item => 
        item.source_text.toLowerCase().includes(searchTerm) ||
        item.translated_text.toLowerCase().includes(searchTerm)
    );
    renderHistory(filtered);
}

async function deleteHistoryItem(id) {
    if (!confirm('Are you sure you want to delete this translation?')) return;

    try {
        const response = await fetch(`/api/history/${id}`, { method: 'DELETE' });
        if (!response.ok) throw new Error('Failed to delete');
        
        await loadHistory();
        showNotification('Translation deleted');
    } catch (error) {
        showError('Failed to delete translation');
    }
}

function restoreTranslation(sourceText, translatedText) {
    document.getElementById('sourceText').value = sourceText;
    document.getElementById('translationResult').value = translatedText;
    showSection('translator');
}

function copyHistoryItem(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!');
    }).catch(() => {
        showError('Failed to copy');
    });
}

async function clearHistory() {
    if (!confirm('Are you sure you want to clear all history? This cannot be undone.')) return;

    try {
        const response = await fetch('/api/history', { method: 'DELETE' });
        if (!response.ok) throw new Error('Failed to clear history');
        
        translationHistory = [];
        renderHistory();
        showNotification('History cleared');
    } catch (error) {
        showError('Failed to clear history');
    }
}

// ==================== UI HELPERS ====================
function showLoading(show) {
    const spinner = document.getElementById('loadingSpinner');
    if (show) {
        spinner.style.display = 'flex';
    } else {
        spinner.style.display = 'none';
    }
}

function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}

function hideError() {
    document.getElementById('errorMessage').style.display = 'none';
}

function showNotification(message) {
    // Create notification element
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        z-index: 10000;
        animation: slideInRight 0.3s ease;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideInLeft 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// ==================== KEYBOARD SHORTCUTS ====================
document.addEventListener('keydown', (e) => {
    // Ctrl+Enter to translate
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        if (document.activeElement.id === 'sourceText') {
            performTranslation();
        }
    }
});

// ==================== SMOOTH SCROLL ====================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});
