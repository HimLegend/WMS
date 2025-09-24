document.addEventListener('DOMContentLoaded', function () {
    const findingsContainer = document.getElementById('findings-container');
    const addFindingBtn = document.getElementById('add-finding');
    const form = document.getElementById('inspection-form');
    let findingCount = 0;

    // Add a new finding
    addFindingBtn.addEventListener('click', function () {
        const template = document.getElementById('finding-template');
        const clone = template.content.cloneNode(true);
        const findingElement = clone.querySelector('.finding-item');

        // Update finding field names
        findingElement.querySelectorAll('input, select, textarea').forEach(input => {
            input.name = input.name.replace('findings[]', `findings[${findingCount}]`);
            if (input.name.includes('description') || input.name.includes('severity')) {
                input.required = true;
            }
        });

        // Initialize part and consumable counters for this finding
        let partCount = 0;
        let consumableCount = 0;

        // Add part button functionality
        const addPartBtn = findingElement.querySelector('.add-part');
        if (addPartBtn) {
            addPartBtn.addEventListener('click', function () {
                addPart(findingElement, findingCount, partCount);
                partCount++;
            });
        }

        // Add consumable button functionality
        const addConsumableBtn = findingElement.querySelector('.add-consumable');
        if (addConsumableBtn) {
            addConsumableBtn.addEventListener('click', function () {
                addConsumable(findingElement, findingCount, consumableCount);
                consumableCount++;
            });
        }

        // Add remove button functionality
        const removeBtn = findingElement.querySelector('.remove-finding');
        if (removeBtn) {
            removeBtn.addEventListener('click', function () {
                findingElement.remove();
            });
        }

        findingsContainer.appendChild(findingElement);
        findingCount++;
    });

    // Add a new part to a finding
    function addPart(findingElement, findingIndex, partIndex) {
        const partsContainer = findingElement.querySelector('.parts-container');
        const template = document.getElementById('part-template');
        const clone = template.content.cloneNode(true);
        const partElement = clone.querySelector('.part-item');

        // Update part field names
        partElement.querySelectorAll('input, select').forEach(input => {
            const fieldName = input.name.match(/\[([^\]]*)\]/)[1];
            input.name = `findings[${findingIndex}][parts][${partIndex}][${fieldName}]`;
            if (fieldName === 'description') {
                input.required = true;
            }
        });

        // Add remove button functionality
        const removeBtn = partElement.querySelector('.remove-part');
        if (removeBtn) {
            removeBtn.addEventListener('click', function () {
                partElement.remove();
            });
        }

        partsContainer.appendChild(partElement);
    }

    // Add a new consumable to a finding
    function addConsumable(findingElement, findingIndex, consumableIndex) {
        const consumablesContainer = findingElement.querySelector('.consumables-container');
        const template = document.getElementById('consumable-template');
        const clone = template.content.cloneNode(true);
        const consumableElement = clone.querySelector('.consumable-item');

        // Update consumable field names
        consumableElement.querySelectorAll('input, select').forEach(input => {
            const fieldName = input.name.match(/\[([^\]]*)\]/)[1];
            input.name = `findings[${findingIndex}][consumables][${consumableIndex}][${fieldName}]`;
            if (fieldName === 'name') {
                input.required = true;
            }
        });

        // Add remove button functionality
        const removeBtn = consumableElement.querySelector('.remove-consumable');
        if (removeBtn) {
            removeBtn.addEventListener('click', function () {
                consumableElement.remove();
            });
        }

        consumablesContainer.appendChild(consumableElement);
    }

    // Add the first finding by default
    addFindingBtn.click();
});