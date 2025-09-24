document.addEventListener('DOMContentLoaded', function() {
    // Initialize formset management
    const addButtons = document.querySelectorAll('.add-item-btn');
    
    // Add event listeners to all add buttons
    addButtons.forEach(button => {
        if (button) {
            button.addEventListener('click', function() {
                const itemType = this.dataset.itemType;
                if (itemType) {
                    addNewItemRow(itemType);
                    updateRowNumbers(itemType);
                    updateTotals();
                }
            });
        }
    });

    // Add new item row
    function addNewItemRow(itemType) {
        const container = document.getElementById(`${itemType}s-container`);
        const emptyRow = document.getElementById(`empty-${itemType}s-template`).cloneNode(true);
        
        // Make the row visible
        emptyRow.classList.remove('d-none');
        
        // Update the form indices
        const totalForms = document.getElementById(`id_${itemType}s-TOTAL_FORMS`);
        const formIdx = parseInt(totalForms.value);
        
        emptyRow.innerHTML = emptyRow.innerHTML.replace(/__prefix__/g, formIdx);
        
        // Add delete button functionality
        const deleteBtn = emptyRow.querySelector('.delete-item-btn');
        if (deleteBtn) {
            deleteBtn.addEventListener('click', function() {
                this.closest('tr').remove();
                updateRowNumbers(itemType);
                updateTotals();
            });
        }
        
        // Add input event listeners for calculations
        const quantityInput = emptyRow.querySelector('input[id$="-quantity"]');
        const priceInput = emptyRow.querySelector('input[id$="-unit_price"]');
        const totalCell = emptyRow.querySelector('.item-total');
        
        if (quantityInput && priceInput && totalCell) {
            const updateRowTotal = () => {
                const quantity = parseFloat(quantityInput.value) || 0;
                const price = parseFloat(priceInput.value) || 0;
                const total = (quantity * price).toFixed(2);
                totalCell.textContent = `AED ${total}`;
                updateTotals();
            };
            
            quantityInput.addEventListener('input', updateRowTotal);
            priceInput.addEventListener('input', updateRowTotal);
        }
        
        container.appendChild(emptyRow);
        totalForms.value = formIdx + 1;
    }

    // Update row numbers
    function updateRowNumbers(itemType) {
        const rows = document.querySelectorAll(`#${itemType}s-container .item-form-row:not(.d-none)`);
        rows.forEach((row, index) => {
            const numberCell = row.querySelector('td:first-child');
            if (numberCell) {
                numberCell.textContent = index + 1;
            }
        });
    }

    // Update totals
    function updateTotals() {
        let subtotal = 0;
        
        // Calculate subtotal from all items
        document.querySelectorAll('.item-form-row:not(.d-none)').forEach(row => {
            const quantity = parseFloat(row.querySelector('input[id$="-quantity"]')?.value) || 0;
            const price = parseFloat(row.querySelector('input[id$="-unit_price"]')?.value) || 0;
            subtotal += quantity * price;
        });
        
        // Get discount percentage
        const discountInput = document.querySelector('input[name$="-discount_percentage"], #id_discount_percentage');
        const discountPercentage = parseFloat(discountInput ? discountInput.value : 0) || 0;
        const discount = (subtotal * discountPercentage) / 100;
        
        // Get VAT percentage (assuming 5% as default)
        const vatPercentage = 5; // You can make this dynamic if needed
        const vat = ((subtotal - discount) * vatPercentage) / 100;
        
        // Calculate total
        const total = subtotal - discount + vat;
        
        // Update display
        document.getElementById('subtotal-display').textContent = `AED ${subtotal.toFixed(2)}`;
        document.getElementById('discount-display').textContent = `-AED ${discount.toFixed(2)}`;
        document.getElementById('vat-display').textContent = `AED ${vat.toFixed(2)}`;
        document.getElementById('total-display').textContent = `AED ${total.toFixed(2)}`;
    }

    // Add event listeners for discount percentage changes
    const discountInput = document.querySelector('input[name$="-discount_percentage"], #id_discount_percentage');
    if (discountInput) {
        discountInput.addEventListener('input', updateTotals);
    }

    // Initialize delete buttons for existing items
    const deleteButtons = document.querySelectorAll('.delete-item-btn');
    if (deleteButtons.length > 0) {
        deleteButtons.forEach(btn => {
            if (btn) {
                btn.addEventListener('click', function() {
                    const row = this.closest('tr');
                    if (!row) return;
                    
                    const itemInput = row.querySelector('input[data-item-type]');
                    const itemType = itemInput ? itemInput.dataset.itemType : null;
                    
                    // If this is a new row (not saved to DB), just remove it
                    if (row.id && row.id.startsWith('empty-')) {
                        row.remove();
                    } else {
                        // For existing items, hide the row and mark for deletion
                        row.style.display = 'none';
                        const deleteInput = row.querySelector('input[id$="-DELETE"]');
                        if (deleteInput) {
                            deleteInput.checked = true;
                        }
                    }
                    
                    if (itemType) {
                        updateRowNumbers(itemType);
                    }
                    updateTotals();
                });
            }
        });
    }

    // Initialize totals on page load
    updateTotals();
});
