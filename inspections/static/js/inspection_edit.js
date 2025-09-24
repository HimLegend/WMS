document.addEventListener('DOMContentLoaded', () => {
    const findingsContainer = document.getElementById('findings-container');
    const addFindingBtn = document.getElementById('add-finding');

    // Helper: Update all form element names and ids to reflect correct indexes
    function updateIndexes() {
        const findings = findingsContainer.querySelectorAll('.finding-item');
        findings.forEach((findingEl, fIndex) => {
            // Update finding inputs
            findingEl.querySelectorAll('input, select, textarea').forEach(el => {
                if (el.name) {
                    el.name = el.name.replace(/\findings-\d+-/, `findings-${fIndex}-`);
                }
                if (el.id) {
                    el.id = el.id.replace(/\findings-\d+-/, `findings-${fIndex}-`);
                }
            });
            // Update hidden id and DELETE inputs similarly
            const idInput = findingEl.querySelector('input[type=hidden][name$="-id"]');
            if (idInput) {
                idInput.name = `findings-${fIndex}-id`;
                idInput.id = `id_findings-${fIndex}-id`;
            }
            const deleteInput = findingEl.querySelector('input[type=checkbox][name$="-DELETE"]');
            if (deleteInput) {
                deleteInput.name = `findings-${fIndex}-DELETE`;
                deleteInput.id = `id_findings-${fIndex}-DELETE`;
            }

            // Update Parts nested formset
            const partsContainer = findingEl.querySelector('.parts-container');
            if (partsContainer) {
                const parts = partsContainer.querySelectorAll('.part-item');
                parts.forEach((partEl, pIndex) => {
                    partEl.querySelectorAll('input, select').forEach(el => {
                        if (el.name) {
                            el.name = el.name.replace(/parts-\d+-/, `parts-${fIndex}-${pIndex}-`);
                        }
                        if (el.id) {
                            el.id = el.id.replace(/parts-\d+-/, `id_parts-${fIndex}-${pIndex}-`);
                        }
                    });
                    // Hidden id and DELETE for parts
                    const partIdInput = partEl.querySelector('input[type=hidden][name$="-id"]');
                    if (partIdInput) {
                        partIdInput.name = `parts-${fIndex}-${pIndex}-id`;
                        partIdInput.id = `id_parts-${fIndex}-${pIndex}-id`;
                    }
                    const partDeleteInput = partEl.querySelector('input[type=checkbox][name$="-DELETE"]');
                    if (partDeleteInput) {
                        partDeleteInput.name = `parts-${fIndex}-${pIndex}-DELETE`;
                        partDeleteInput.id = `id_parts-${fIndex}-${pIndex}-DELETE`;
                    }
                });
                // Update management form TOTAL_FORMS for parts of this finding
                const partManagement = findingEl.querySelector('input[name$="TOTAL_FORMS"][name^="parts-"]');
                if (partManagement) {
                    partManagement.value = parts.length;
                    partManagement.name = `parts-${fIndex}-TOTAL_FORMS`;
                    partManagement.id = `id_parts-${fIndex}-TOTAL_FORMS`;
                }
            }

            // Update Consumables nested formset
            const consumablesContainer = findingEl.querySelector('.consumables-container');
            if (consumablesContainer) {
                const consumables = consumablesContainer.querySelectorAll('.consumable-item');
                consumables.forEach((consEl, cIndex) => {
                    consEl.querySelectorAll('input, select').forEach(el => {
                        if (el.name) {
                            el.name = el.name.replace(/consumables-\d+-/, `consumables-${fIndex}-${cIndex}-`);
                        }
                        if (el.id) {
                            el.id = el.id.replace(/consumables-\d+-/, `id_consumables-${fIndex}-${cIndex}-`);
                        }
                    });
                    // Hidden id and DELETE for consumables
                    const consIdInput = consEl.querySelector('input[type=hidden][name$="-id"]');
                    if (consIdInput) {
                        consIdInput.name = `consumables-${fIndex}-${cIndex}-id`;
                        consIdInput.id = `id_consumables-${fIndex}-${cIndex}-id`;
                    }
                    const consDeleteInput = consEl.querySelector('input[type=checkbox][name$="-DELETE"]');
                    if (consDeleteInput) {
                        consDeleteInput.name = `consumables-${fIndex}-${cIndex}-DELETE`;
                        consDeleteInput.id = `id_consumables-${fIndex}-${cIndex}-DELETE`;
                    }
                });
                // Update management form TOTAL_FORMS for consumables of this finding
                const consManagement = findingEl.querySelector('input[name$="TOTAL_FORMS"][name^="consumables-"]');
                if (consManagement) {
                    consManagement.value = consumables.length;
                    consManagement.name = `consumables-${fIndex}-TOTAL_FORMS`;
                    consManagement.id = `id_consumables-${fIndex}-TOTAL_FORMS`;
                }
            }
        });

        // Update TOTAL_FORMS for findings
        const totalFindingForms = document.querySelector('input[name="findings-TOTAL_FORMS"]');
        if (totalFindingForms) {
            totalFindingForms.value = findings.length;
        }
    }

    // Add Finding
    addFindingBtn.addEventListener('click', () => {
        // Clone the first finding form or create from template if you have one
        const firstFinding = findingsContainer.querySelector('.finding-item');
        if (!firstFinding) return;

        const clone = firstFinding.cloneNode(true);

        // Clear inputs in cloned finding
        clone.querySelectorAll('input, textarea').forEach(el => {
            if (el.type === 'hidden' && /-id$/.test(el.name)) {
                el.value = '';
            } else if (el.type === 'checkbox' && /-DELETE$/.test(el.name)) {
                el.checked = false;
            } else if (el.tagName === 'TEXTAREA' || el.tagName === 'INPUT' || el.tagName === 'SELECT') {
                if (el.type === 'number') {
                    el.value = '1.0';
                } else if (el.tagName === 'SELECT') {
                    el.selectedIndex = 1; // e.g. Medium severity by default
                } else {
                    el.value = '';
                }
            }
        });

        // Remove all parts and consumables from cloned finding to start clean
        const partsContainer = clone.querySelector('.parts-container');
        if (partsContainer) partsContainer.innerHTML = '';
        const consumablesContainer = clone.querySelector('.consumables-container');
        if (consumablesContainer) consumablesContainer.innerHTML = '';

        // Append clone
        findingsContainer.appendChild(clone);

        updateIndexes();
    });

    // Delegate click event for dynamic remove buttons on findings, parts, consumables
    findingsContainer.addEventListener('click', e => {
        if (e.target.classList.contains('remove-finding')) {
            e.target.closest('.finding-item').remove();
            updateIndexes();
        }
        if (e.target.classList.contains('remove-part')) {
            e.target.closest('.part-item').remove();
            updateIndexes();
        }
        if (e.target.classList.contains('remove-consumable')) {
            e.target.closest('.consumable-item').remove();
            updateIndexes();
        }
    });

    // Delegate click for add part button inside findings container
    findingsContainer.addEventListener('click', e => {
        if (e.target.classList.contains('add-part')) {
            const findingEl = e.target.closest('.finding-item');
            const partsContainer = findingEl.querySelector('.parts-container');
            if (!partsContainer) return;

            // Create new part row with empty inputs
            const newPart = document.createElement('div');
            newPart.classList.add('row', 'mb-2', 'part-item');
            newPart.innerHTML = `
          <input type="hidden" name="" value="" />
          <div class="col">
            <input type="text" name="" placeholder="Part number" class="form-control" />
          </div>
          <div class="col">
            <input type="text" name="" placeholder="Part description" class="form-control" required />
          </div>
          <div class="col-2">
            <input type="number" name="" value="1" min="1" class="form-control" />
          </div>
          <div class="col">
            <select name="" class="form-select">
              <option value="required">Required</option>
              <option value="ordered">Ordered</option>
              <option value="in_stock">In Stock</option>
              <option value="installed">Installed</option>
            </select>
          </div>
          <div class="col-auto">
            <button type="button" class="btn btn-sm btn-danger remove-part">✕</button>
          </div>
        `;
            partsContainer.appendChild(newPart);
            updateIndexes();
        }
    });

    // Delegate click for add consumable button inside findings container
    findingsContainer.addEventListener('click', e => {
        if (e.target.classList.contains('add-consumable')) {
            const findingEl = e.target.closest('.finding-item');
            const consumablesContainer = findingEl.querySelector('.consumables-container');
            if (!consumablesContainer) return;

            const newConsumable = document.createElement('div');
            newConsumable.classList.add('row', 'mb-2', 'consumable-item');
            newConsumable.innerHTML = `
          <input type="hidden" name="" value="" />
          <div class="col">
            <input type="text" name="" placeholder="Consumable name" class="form-control" required />
          </div>
          <div class="col-2">
            <input type="number" step="0.1" name="" value="1" class="form-control" />
          </div>
          <div class="col-2">
            <select name="" class="form-select">
              <option value="pcs">pcs</option>
              <option value="l">L</option>
              <option value="ml">ml</option>
              <option value="kg">kg</option>
              <option value="g">g</option>
              <option value="m">m</option>
              <option value="cm">cm</option>
            </select>
          </div>
          <div class="col-auto">
            <button type="button" class="btn btn-sm btn-danger remove-consumable">✕</button>
          </div>
        `;
            consumablesContainer.appendChild(newConsumable);
            updateIndexes();
        }
    });

    // Initial index update on page load
    updateIndexes();
});
