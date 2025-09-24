document.addEventListener('DOMContentLoaded', function () {
    const findingsContainer = document.getElementById('findings-container');
    const addFindingBtn = document.getElementById('add-finding');
    const findingTemplate = document.getElementById('finding-template');
    const partTemplate = document.getElementById('part-template');
    const consumableTemplate = document.getElementById('consumable-template');

    function cloneTemplate(template) {
        return document.importNode(template.content, true);
    }

    function setupFindingEvents(findingEl) {
        findingEl.querySelector('.remove-finding').addEventListener('click', () => {
            findingEl.remove();
        });

        findingEl.querySelector('.add-part').addEventListener('click', () => {
            const container = findingEl.querySelector('.parts-container');
            const partEl = cloneTemplate(partTemplate);
            setupPartEvents(partEl);
            container.appendChild(partEl);
        });

        findingEl.querySelector('.add-consumable').addEventListener('click', () => {
            const container = findingEl.querySelector('.consumables-container');
            const consEl = cloneTemplate(consumableTemplate);
            setupConsumableEvents(consEl);
            container.appendChild(consEl);
        });
    }

    function setupPartEvents(partEl) {
        partEl.querySelector('.remove-part').addEventListener('click', () => {
            partEl.remove();
        });
    }

    function setupConsumableEvents(consumableEl) {
        consumableEl.querySelector('.remove-consumable').addEventListener('click', () => {
            consumableEl.remove();
        });
    }

    addFindingBtn.addEventListener('click', () => {
        const findingEl = cloneTemplate(findingTemplate);
        const findingCard = findingEl.querySelector('.finding-item');
        setupFindingEvents(findingCard);
        findingsContainer.appendChild(findingEl);
    });
});
