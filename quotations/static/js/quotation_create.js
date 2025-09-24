document.addEventListener('DOMContentLoaded', function () {
    const itemsContainer = document.getElementById('items-container');
    const totalFormsInput = document.querySelector('[name$="-TOTAL_FORMS"]');
    const vatCheckbox = document.querySelector('input[name="include_vat"]');
    const discountInput = document.querySelector('input[name="discount_percentage"]');
    const addItemBtn = document.getElementById('add-item-btn');
    const emptyFormRow = document.getElementById('empty-form-template');

    function calculateRowTotal(row) {
        const unitPrice = parseFloat(row.querySelector('.unit-price')?.value || 0);
        const quantity = parseInt(row.querySelector('.quantity')?.value || 1);
        const total = unitPrice * quantity;
        row.querySelector('.item-total').textContent = total.toFixed(2);
        return total;
    }

    function calculateAllTotals() {
        let subtotal = 0;
        document.querySelectorAll('.item-form-row').forEach(row => {
            if (!row.classList.contains('d-none')) {
                subtotal += calculateRowTotal(row);
            }
        });

        const discountPct = parseFloat(discountInput?.value || 0);
        const discount = subtotal * (discountPct / 100);
        const vat = vatCheckbox?.checked ? (subtotal - discount) * 0.05 : 0;
        const grandTotal = subtotal - discount + vat;

        document.getElementById('subtotal-display').textContent = `AED ${subtotal.toFixed(2)}`;
        document.getElementById('discount-display').textContent = `-AED ${discount.toFixed(2)}`;
        document.getElementById('vat-display').textContent = `AED ${vat.toFixed(2)}`;
        document.getElementById('total-display').textContent = `AED ${grandTotal.toFixed(2)}`;
    }

    function setupRowEvents(row) {
        row.querySelectorAll('.unit-price, .quantity').forEach(input => {
            input.addEventListener('input', calculateAllTotals);
        });

        row.querySelector('.quantity-up')?.addEventListener('click', () => {
            const input = row.querySelector('.quantity');
            input.value = parseInt(input.value || 1) + 1;
            calculateAllTotals();
        });

        row.querySelector('.quantity-down')?.addEventListener('click', () => {
            const input = row.querySelector('.quantity');
            input.value = Math.max(1, parseInt(input.value || 1) - 1);
            calculateAllTotals();
        });

        row.querySelector('.remove-item')?.addEventListener('click', () => {
            row.style.display = 'none';
            const deleteInput = row.querySelector('input[type="checkbox"]');
            if (deleteInput) deleteInput.checked = true;
            calculateAllTotals();
        });
    }

    document.querySelectorAll('.item-form-row').forEach(row => {
        if (!row.id.includes('empty-form-template')) {
            setupRowEvents(row);
        }
    });

    addItemBtn.addEventListener('click', () => {
        const formIdx = parseInt(totalFormsInput.value);
        const newRow = emptyFormRow.cloneNode(true);
        newRow.classList.remove('d-none');
        newRow.removeAttribute('id');

        newRow.innerHTML = newRow.innerHTML.replace(/__prefix__/g, formIdx);

        // Update all name and id attributes
        newRow.querySelectorAll('[name], [id], [for]').forEach(el => {
            if (el.name) el.name = el.name.replace(/__prefix__/g, formIdx);
            if (el.id) el.id = el.id.replace(/__prefix__/g, formIdx);
            if (el.getAttribute('for')) el.setAttribute('for', el.getAttribute('for').replace(/__prefix__/g, formIdx));
        });

        itemsContainer.appendChild(newRow);
        totalFormsInput.value = formIdx + 1;
        setupRowEvents(newRow);
        calculateAllTotals();
    });

    vatCheckbox?.addEventListener('change', calculateAllTotals);
    discountInput?.addEventListener('input', calculateAllTotals);
    calculateAllTotals();
});
