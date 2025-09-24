function recalculateTotals() {
    const rows = document.querySelectorAll('tbody tr.item-form-row:not(#empty-form-template):not([style*="display: none"])');
    let subtotal = 0;
    const discountPercent = parseFloat(window.discountPercentage || 0);
    const vatPercent = parseFloat(window.vatPercentage || 0);

    rows.forEach(row => {
        const qtyInput = row.querySelector('[name$="-quantity"]');
        const priceInput = row.querySelector('[name$="-unit_price"]');
        const lineTotalSpan = row.querySelector('.item-total');

        const quantity = parseFloat(qtyInput?.value || 0);
        const unitPrice = parseFloat(priceInput?.value || 0);
        const lineTotal = quantity * unitPrice;

        if (lineTotalSpan) {
            lineTotalSpan.textContent = 'AED ' + lineTotal.toFixed(2);
        }

        subtotal += lineTotal;
    });

    const discountAmount = subtotal * (discountPercent / 100);
    const vatAmount = (subtotal - discountAmount) * (vatPercent / 100);
    const grandTotal = subtotal - discountAmount + vatAmount;

    const subtotalDisplay = document.getElementById('subtotal-display');
    const discountDisplay = document.getElementById('discount-display');
    const vatDisplay = document.getElementById('vat-display');
    const grandTotalDisplay = document.getElementById('grand-total-display');

    if (subtotalDisplay) subtotalDisplay.textContent = 'AED ' + subtotal.toFixed(2);
    if (discountDisplay) discountDisplay.textContent = '-AED ' + discountAmount.toFixed(2);
    if (vatDisplay) vatDisplay.textContent = 'AED ' + vatAmount.toFixed(2);
    if (grandTotalDisplay) grandTotalDisplay.textContent = 'AED ' + grandTotal.toFixed(2);
}

document.addEventListener('DOMContentLoaded', () => {
    // Quantity increment/decrement buttons
    document.querySelectorAll('.quantity-controls').forEach(control => {
        const input = control.querySelector('input.quantity');
        const btnUp = control.querySelector('.quantity-up');
        const btnDown = control.querySelector('.quantity-down');

        btnUp?.addEventListener('click', () => {
            if (!input) return;
            let val = parseInt(input.value) || 1;
            val++;
            input.value = val;
            input.dispatchEvent(new Event('input'));  // trigger recalculation
        });

        btnDown?.addEventListener('click', () => {
            if (!input) return;
            let val = parseInt(input.value) || 1;
            if (val > 1) val--;
            input.value = val;
            input.dispatchEvent(new Event('input'));  // trigger recalculation
        });
    });

    // Initialize discount and VAT from inputs
    const includeVatCheckbox = document.querySelector('[name="include_vat"]');
    const discountInput = document.querySelector('[name="discount_percentage"]');

    window.discountPercentage = parseFloat(discountInput?.value || 0);
    window.vatPercentage = includeVatCheckbox?.checked ? 5 : 0;

    // Add listeners for recalculation on quantity and unit price inputs
    document.querySelectorAll('[name$="-quantity"], [name$="-unit_price"]').forEach(input => {
        input.addEventListener('input', recalculateTotals);
    });

    // Listen for VAT checkbox toggle
    if (includeVatCheckbox) {
        includeVatCheckbox.addEventListener('change', () => {
            window.vatPercentage = includeVatCheckbox.checked ? 5 : 0;
            recalculateTotals();
        });
    }

    // Listen for discount percentage input changes
    if (discountInput) {
        discountInput.addEventListener('input', () => {
            const val = parseFloat(discountInput.value);
            window.discountPercentage = isNaN(val) ? 0 : val;
            recalculateTotals();
        });
    }

    // Add Item button and formset management
    const addItemBtn = document.getElementById('add-item-btn');
    const itemsContainer = document.getElementById('items-container');
    const totalFormsInput = document.querySelector('input[name$="-TOTAL_FORMS"]');

    addItemBtn.addEventListener('click', () => {
        const totalForms = parseInt(totalFormsInput.value, 10);
        const emptyRow = document.getElementById('empty-form-template');

        const newRow = emptyRow.cloneNode(true);
        newRow.classList.remove('d-none');
        newRow.removeAttribute('id');

        newRow.innerHTML = newRow.innerHTML.replace(/__prefix__/g, totalForms);

        const numberCell = newRow.querySelector('td.text-center');
        if (numberCell) {
            numberCell.textContent = totalForms + 1;
        }

        newRow.querySelectorAll('input, select, textarea').forEach(input => {
            if (input.type === 'checkbox' || input.type === 'radio') {
                input.checked = false;
            } else {
                input.value = '';
            }
        });

        itemsContainer.appendChild(newRow);
        totalFormsInput.value = totalForms + 1;

        newRow.querySelectorAll('[name$="-quantity"], [name$="-unit_price"]').forEach(input => {
            input.addEventListener('input', recalculateTotals);
        });

        const removeBtn = newRow.querySelector('.remove-item');
        if (removeBtn) {
            removeBtn.addEventListener('click', removeRow);
        }

        recalculateTotals();
    });

    // Remove row function
    function removeRow(event) {
        const btn = event.currentTarget;
        const row = btn.closest('tr.item-form-row');
        if (!row) return;

        const deleteInput = row.querySelector('input[type="checkbox"][name$="-DELETE"]');
        if (deleteInput) {
            deleteInput.checked = true;
            row.style.display = 'none';
        } else {
            row.remove();
        }

        recalculateTotals();
        updateRowNumbers();
    }

    // Add remove listeners on existing rows
    document.querySelectorAll('.remove-item').forEach(btn => {
        btn.addEventListener('click', removeRow);
    });

    // Update row numbers after changes
    function updateRowNumbers() {
        const rows = itemsContainer.querySelectorAll('tr.item-form-row:not(#empty-form-template):not([style*="display: none"])');
        rows.forEach((row, index) => {
            const numberCell = row.querySelector('td.text-center');
            if (numberCell) {
                numberCell.textContent = index + 1;
            }
        });
    }

    // Initial calculation
    recalculateTotals();
});
