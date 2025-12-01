(function() {
    'use strict';

    console.log('Taiga Custom Fields Display - Loaded');

    let customFieldsConfig = {
        showInList: true,
        showInKanban: true,
        maxFieldsToShow: 3
    };

    function injectCustomFieldsStyles() {
        if (document.getElementById('custom-fields-styles')) {
            return;
        }

        const style = document.createElement('style');
        style.id = 'custom-fields-styles';
        style.textContent = `
            .custom-fields-display {
                margin-top: 6px;
                padding: 6px 8px;
                background: #f9f9f9;
                border-radius: 3px;
                font-size: 11px;
                line-height: 1.4;
                border-left: 2px solid #e0e0e0;
            }

            .custom-field-item {
                display: inline-block;
                margin-right: 12px;
                margin-bottom: 3px;
                color: #666;
            }

            .custom-field-item strong {
                color: #333;
                font-weight: 600;
                margin-right: 4px;
            }

            .custom-field-value {
                color: #555;
            }

            .kanban-card .custom-fields-display {
                margin-top: 8px;
                font-size: 10px;
            }

            .custom-fields-display:empty {
                display: none;
            }
        `;
        document.head.appendChild(style);
        console.log('✓ Custom fields styles injected');
    }

    function extractCustomFields(element) {
        const customFieldsData = {};

        try {
            const dataElement = element.querySelector('[data-custom-fields]');
            if (dataElement) {
                const data = JSON.parse(dataElement.getAttribute('data-custom-fields'));
                return data;
            }
        } catch (e) {
            console.debug('No custom fields data found');
        }

        return customFieldsData;
    }

    function createCustomFieldsDisplay(customFields) {
        if (!customFields || Object.keys(customFields).length === 0) {
            return null;
        }

        const container = document.createElement('div');
        container.className = 'custom-fields-display';

        let fieldCount = 0;
        const maxFields = customFieldsConfig.maxFieldsToShow;

        for (const [key, value] of Object.entries(customFields)) {
            if (fieldCount >= maxFields) break;
            if (!value) continue;

            const fieldItem = document.createElement('span');
            fieldItem.className = 'custom-field-item';

            const fieldName = document.createElement('strong');
            fieldName.textContent = key + ':';

            const fieldValue = document.createElement('span');
            fieldValue.className = 'custom-field-value';
            fieldValue.textContent = value;

            fieldItem.appendChild(fieldName);
            fieldItem.appendChild(fieldValue);
            container.appendChild(fieldItem);

            fieldCount++;
        }

        return fieldCount > 0 ? container : null;
    }

    function processCard(card) {
        if (card.hasAttribute('data-custom-fields-processed')) {
            return;
        }

        const customFields = extractCustomFields(card);
        const displayElement = createCustomFieldsDisplay(customFields);

        if (displayElement) {
            const insertPoint = card.querySelector('.card-title, .task-name, .us-title') || card;
            if (insertPoint.parentNode) {
                insertPoint.parentNode.insertBefore(displayElement, insertPoint.nextSibling);
            } else {
                card.appendChild(displayElement);
            }
        }

        card.setAttribute('data-custom-fields-processed', 'true');
    }

    function processAllCards() {
        const selectors = [
            '.task-card',
            '.us-item',
            '.kanban-card',
            '.backlog-item',
            '.issue-row'
        ];

        let processedCount = 0;

        selectors.forEach(selector => {
            const cards = document.querySelectorAll(selector + ':not([data-custom-fields-processed])');
            cards.forEach(card => {
                processCard(card);
                processedCount++;
            });
        });

        if (processedCount > 0) {
            console.log(`✓ Processed ${processedCount} cards with custom fields`);
        }
    }

    function observeDOMChanges() {
        const observer = new MutationObserver((mutations) => {
            let shouldProcess = false;

            mutations.forEach((mutation) => {
                if (mutation.addedNodes.length > 0) {
                    shouldProcess = true;
                }
            });

            if (shouldProcess) {
                setTimeout(processAllCards, 100);
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });

        console.log('✓ DOM observer started');
    }

    function initialize() {
        console.log('Initializing custom fields display...');

        injectCustomFieldsStyles();

        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                processAllCards();
                observeDOMChanges();
            });
        } else {
            processAllCards();
            observeDOMChanges();
        }

        setInterval(processAllCards, 2000);

        console.log('✓ Custom fields display initialized');
    }

    initialize();

})();
