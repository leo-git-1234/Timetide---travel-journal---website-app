/**
 * Dynamic Translation System for Timetide
 * Uses Google Translate to translate ALL content on the page in real-time
 */

class DynamicTranslator {
    constructor() {
        this.currentLanguage = localStorage.getItem('userLanguage') || 'en';
        this.originalContent = new Map();
        this.isTranslating = false;
    }

    /**
     * Translate text using Google Translate API
     */
    async translateText(text, targetLang) {
        if (!text || text.trim() === '') return text;
        if (targetLang === 'en') return text;

        try {
            // Using Google Translate API endpoint
            const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=${targetLang}&dt=t&q=${encodeURIComponent(text)}`;
            
            const response = await fetch(url);
            const data = await response.json();
            
            if (data && data[0] && data[0][0] && data[0][0][0]) {
                return data[0][0][0];
            }
            
            return text;
        } catch (error) {
            console.error('Translation error:', error);
            return text;
        }
    }

    /**
     * Translate multiple texts in batch
     */
    async translateBatch(texts, targetLang) {
        if (targetLang === 'en') return texts;
        
        const promises = texts.map(text => this.translateText(text, targetLang));
        return await Promise.all(promises);
    }

    /**
     * Save original content before translation
     */
    saveOriginalContent(element, content) {
        const key = this.getElementKey(element);
        if (!this.originalContent.has(key)) {
            this.originalContent.set(key, content);
        }
    }

    /**
     * Get unique key for an element
     */
    getElementKey(element) {
        if (element.id) return element.id;
        
        let path = [];
        let current = element;
        while (current && current !== document.body) {
            let selector = current.tagName.toLowerCase();
            if (current.className) {
                selector += '.' + current.className.split(' ').join('.');
            }
            path.unshift(selector);
            current = current.parentElement;
        }
        return path.join(' > ');
    }

    /**
     * Get original content
     */
    getOriginalContent(element) {
        const key = this.getElementKey(element);
        return this.originalContent.get(key);
    }

    /**
     * Translate all text nodes in the page
     */
    async translatePage(targetLang) {
        if (this.isTranslating) return;
        this.isTranslating = true;

        try {
            // If switching back to English, restore original content
            if (targetLang === 'en') {
                this.restoreOriginalContent();
                this.isTranslating = false;
                return;
            }

            // Get all text nodes
            const textNodes = this.getAllTextNodes(document.body);
            const textsToTranslate = [];
            const nodesToUpdate = [];

            textNodes.forEach(node => {
                const text = node.textContent.trim();
                if (text && text.length > 0 && !this.isExcluded(node.parentElement)) {
                    // Save original content
                    this.saveOriginalContent(node.parentElement, node.textContent);
                    textsToTranslate.push(text);
                    nodesToUpdate.push(node);
                }
            });

            // Translate in batches of 50
            const batchSize = 50;
            for (let i = 0; i < textsToTranslate.length; i += batchSize) {
                const batch = textsToTranslate.slice(i, i + batchSize);
                const nodes = nodesToUpdate.slice(i, i + batchSize);
                
                const translations = await this.translateBatch(batch, targetLang);
                
                // Update the nodes
                translations.forEach((translation, index) => {
                    if (nodes[index]) {
                        nodes[index].textContent = translation;
                    }
                });

                // Small delay to avoid rate limiting
                if (i + batchSize < textsToTranslate.length) {
                    await new Promise(resolve => setTimeout(resolve, 100));
                }
            }

            // Translate placeholders
            await this.translatePlaceholders(targetLang);

            // Translate input values
            await this.translateInputValues(targetLang);

        } catch (error) {
            console.error('Page translation error:', error);
        } finally {
            this.isTranslating = false;
        }
    }

    /**
     * Get all text nodes recursively
     */
    getAllTextNodes(element) {
        const textNodes = [];
        const walk = document.createTreeWalker(
            element,
            NodeFilter.SHOW_TEXT,
            {
                acceptNode: function(node) {
                    // Skip script, style, and empty text nodes
                    if (node.parentElement.tagName === 'SCRIPT' ||
                        node.parentElement.tagName === 'STYLE' ||
                        !node.textContent.trim()) {
                        return NodeFilter.FILTER_REJECT;
                    }
                    return NodeFilter.FILTER_ACCEPT;
                }
            }
        );

        let node;
        while (node = walk.nextNode()) {
            textNodes.push(node);
        }

        return textNodes;
    }

    /**
     * Check if element should be excluded from translation
     */
    isExcluded(element) {
        if (!element) return true;
        
        // Exclude certain tags
        const excludedTags = ['SCRIPT', 'STYLE', 'CODE', 'PRE'];
        if (excludedTags.includes(element.tagName)) return true;

        // Exclude elements with data-no-translate attribute
        if (element.hasAttribute('data-no-translate')) return true;

        return false;
    }

    /**
     * Translate placeholder attributes
     */
    async translatePlaceholders(targetLang) {
        const elements = document.querySelectorAll('[placeholder]');
        
        for (const element of elements) {
            const originalPlaceholder = element.getAttribute('data-original-placeholder') || element.placeholder;
            
            if (!element.hasAttribute('data-original-placeholder')) {
                element.setAttribute('data-original-placeholder', originalPlaceholder);
            }

            if (targetLang === 'en') {
                element.placeholder = originalPlaceholder;
            } else {
                const translated = await this.translateText(originalPlaceholder, targetLang);
                element.placeholder = translated;
            }
        }
    }

    /**
     * Translate input values
     */
    async translateInputValues(targetLang) {
        const elements = document.querySelectorAll('input[type="button"], input[type="submit"], button');
        
        for (const element of elements) {
            if (element.hasAttribute('data-no-translate')) continue;
            
            const originalValue = element.getAttribute('data-original-value') || element.value || element.textContent;
            
            if (!element.hasAttribute('data-original-value')) {
                element.setAttribute('data-original-value', originalValue);
            }

            if (targetLang === 'en') {
                if (element.value) element.value = originalValue;
            } else {
                const translated = await this.translateText(originalValue, targetLang);
                if (element.value) element.value = translated;
            }
        }
    }

    /**
     * Restore original content
     */
    restoreOriginalContent() {
        this.originalContent.forEach((content, key) => {
            const element = this.findElementByKey(key);
            if (element) {
                element.textContent = content;
            }
        });

        // Restore placeholders
        document.querySelectorAll('[data-original-placeholder]').forEach(element => {
            element.placeholder = element.getAttribute('data-original-placeholder');
        });

        // Restore button values
        document.querySelectorAll('[data-original-value]').forEach(element => {
            const original = element.getAttribute('data-original-value');
            if (element.value) element.value = original;
        });
    }

    /**
     * Find element by key (simplified version)
     */
    findElementByKey(key) {
        return document.getElementById(key) || document.querySelector(key);
    }

    /**
     * Change language and translate entire page
     */
    async changeLanguage(langCode) {
        this.currentLanguage = langCode;
        localStorage.setItem('userLanguage', langCode);
        document.documentElement.lang = langCode;
        
        // Show loading indicator
        this.showLoadingIndicator();
        
        // Translate the page
        await this.translatePage(langCode);
        
        // Hide loading indicator
        this.hideLoadingIndicator();
        
        // Emit event
        window.dispatchEvent(new CustomEvent('languageChanged', { detail: { language: langCode } }));
    }

    /**
     * Show loading indicator
     */
    showLoadingIndicator() {
        let indicator = document.getElementById('translation-loading');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'translation-loading';
            indicator.style.cssText = `
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 20px 40px;
                border-radius: 10px;
                z-index: 100000;
                font-size: 16px;
            `;
            indicator.textContent = 'Translating...';
            document.body.appendChild(indicator);
        }
        indicator.style.display = 'block';
    }

    /**
     * Hide loading indicator
     */
    hideLoadingIndicator() {
        const indicator = document.getElementById('translation-loading');
        if (indicator) {
            indicator.style.display = 'none';
        }
    }

    /**
     * Initialize on page load
     */
    async init() {
        if (this.currentLanguage !== 'en') {
            await this.translatePage(this.currentLanguage);
        }
    }
}

// Create global instance
window.translator = new DynamicTranslator();

// Auto-initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => window.translator.init());
} else {
    window.translator.init();
}
