/**
 * FarmShield AI - Professional Startup JS
 * Features: Transitions, Interactive Map, Autofill, Geolocation, Live Stats
 */

document.addEventListener('DOMContentLoaded', function() {
    initLiveStats();
    initSidebar();
    initTransitions();
    initFormInteractions();
    initLanguageToggle();
    initThemeToggle();
});

// ─── Live Clock & Weather ───────────────────────────────────
function initLiveStats() {
    const timeEl = document.getElementById('liveTime');
    if (timeEl) {
        setInterval(() => {
            const now = new Date();
            timeEl.textContent = now.toLocaleTimeString('en-IN', {
                hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true
            });
        }, 1000);
    }

    // Topbar Weather (Simulated or API)
    const tempEl = document.getElementById('topbarTemp');
    if (tempEl) {
        fetch('/api/weather?lat=20.5937&lon=78.9629')
            .then(res => res.json())
            .then(data => {
                tempEl.textContent = `${data.temperature}°C`;
            })
            .catch(() => {});
    }
}

// ─── Sidebar Logic ──────────────────────────────────────────
function initSidebar() {
    const toggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    if (toggle && sidebar) {
        toggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });
    }
    
    // Auto-close on mobile when link clicked
    document.querySelectorAll('.nav-link-side').forEach(link => {
        link.addEventListener('click', () => {
            if (window.innerWidth < 992 && sidebar) {
                sidebar.classList.remove('open');
            }
        });
    });
}

// ─── Page Transitions (Truck Animation) ─────────────────────
function initTransitions() {
    const overlay = document.getElementById('truck-overlay');
    
    // Show on link click
    document.querySelectorAll('a').forEach(link => {
        const href = link.getAttribute('href');
        if (href && href !== '#' && !href.startsWith('javascript') && !link.target && !href.includes('logout')) {
            link.addEventListener('click', (e) => {
                if (e.metaKey || e.ctrlKey) return;
                e.preventDefault();
                if (overlay) overlay.classList.add('show');
                setTimeout(() => {
                    window.location.href = href;
                }, 800);
            });
        }
    });

    // Handle form submissions
    const mainForm = document.getElementById('predictForm');
    if (mainForm) {
        mainForm.addEventListener('submit', () => {
            if (overlay) overlay.classList.add('show');
        });
    }
}

// ─── Form Interactions (Autofill, Geo, Preview) ─────────────
function initFormInteractions() {
    // Image Preview
    const fileInput = document.getElementById('foodImage');
    const previewImg = document.querySelector('#imagePreview img');
    const previewWrap = document.getElementById('imagePreview');
    if (fileInput && previewImg) {
        fileInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = e => {
                    previewImg.src = e.target.result;
                    previewWrap.classList.remove('d-none');
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Drag and Drop Zone
    const dropZone = document.getElementById('dropZone');
    if (dropZone) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(evt => {
            dropZone.addEventListener(evt, e => {
                e.preventDefault();
                e.stopPropagation();
            });
        });
        dropZone.addEventListener('dragover', () => dropZone.classList.add('dragover'));
        dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
        dropZone.addEventListener('drop', (e) => {
            dropZone.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length && fileInput) {
                fileInput.files = files;
                fileInput.dispatchEvent(new Event('change'));
            }
        });
    }
}

// ─── Toast Utility ──────────────────────────────────────────
function showToast(message, category = 'info') {
    const container = document.querySelector('.toast-container');
    if (!container) return;
    
    const id = 'toast-' + Date.now();
    const html = `
        <div id="${id}" class="toast show toast-startup" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header border-0 bg-transparent">
                <i class="fas fa-info-circle me-2 text-primary"></i>
                <strong class="me-auto text-capitalize">${category}</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">${message}</div>
        </div>
    `;
    container.insertAdjacentHTML('beforeend', html);
    setTimeout(() => {
        const el = document.getElementById(id);
        if (el) el.remove();
    }, 4000);
}

// Ensure fromjson works if needed in frontend (though usually handled by Jinja)
function parseJson(str) {
    try { return JSON.parse(str); } catch(e) { return {}; }
}

function initLanguageToggle() {
    const langButton = document.getElementById('langToggle');
    if (!langButton) return;

    const labels = {
        en: {
            nav_dashboard: 'Dashboard',
            nav_predict: 'AI Predictor',
            nav_analytics: 'Analytics',
            nav_map: 'Live Map',
            nav_about: 'About',
            nav_support: 'Support',
            toggle_theme: 'Dark'
        },
        ta: {
            nav_dashboard: 'டாஷ்போர்டு',
            nav_predict: 'ஏ.ஐ முன்னறிதல்',
            nav_analytics: 'புள்ளிவிவரங்கள்',
            nav_map: 'நேரடி வரைபடம்',
            nav_about: 'பற்றி',
            nav_support: 'ஆதரவு',
            toggle_theme: 'இருண்ட'
        }
    };

    let currentLang = localStorage.getItem('agro_lang') || 'en';
    applyLanguage(currentLang, labels);
    langButton.textContent = currentLang === 'en' ? 'TA' : 'EN';

    langButton.addEventListener('click', () => {
        currentLang = currentLang === 'en' ? 'ta' : 'en';
        localStorage.setItem('agro_lang', currentLang);
        langButton.textContent = currentLang === 'en' ? 'TA' : 'EN';
        applyLanguage(currentLang, labels);
    });
}

function applyLanguage(lang, labels) {
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.dataset.i18n;
        if (labels[lang] && labels[lang][key]) {
            el.textContent = labels[lang][key];
        }
    });
}

function initThemeToggle() {
    const themeButton = document.getElementById('themeToggle');
    if (!themeButton) return;

    let theme = localStorage.getItem('agro_theme') || 'light';
    setTheme(theme, themeButton);

    themeButton.addEventListener('click', () => {
        theme = theme === 'light' ? 'dark' : 'light';
        setTheme(theme, themeButton);
    });
}

function setTheme(theme, button) {
    document.body.classList.toggle('dark-mode', theme === 'dark');
    localStorage.setItem('agro_theme', theme);
    if (button) {
        button.textContent = theme === 'dark' ? 'Light' : 'Dark';
    }
}

// PERF: Removed dead AJAX code for shelf-life/timeline/storage/delay (now server-rendered)

