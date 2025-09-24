document.addEventListener('DOMContentLoaded', function () {
    const commentSections = ['requiredJobs', 'customerComments', 'workshopComments'];

    commentSections.forEach(section => {
        const container = document.getElementById(`${section}Container`);
        const addBtn = document.getElementById(`add${capitalize(section)}`);

        addBtn.addEventListener('click', () => {
            const newEntry = createEntry(section, '');
            container.appendChild(newEntry);
            updateTextareaNames(section);
        });

        // Load existing values (if any)
        const existingData = container.getAttribute('data-existing') || '';
        const lines = existingData.trim().split('\n').filter(line => line.trim() !== '');
        lines.forEach(line => {
            const entry = createEntry(section, line);
            container.appendChild(entry);
        });
    });

    function createEntry(section, value) {
        const wrapper = document.createElement('div');
        wrapper.className = 'input-group mb-2';

        const span = document.createElement('span');
        span.className = 'input-group-text';
        span.textContent = `${getNumber(section) + 1}.`;

        const textarea = document.createElement('textarea');
        textarea.className = 'form-control';
        textarea.rows = 1;
        textarea.value = value;

        const removeBtnWrapper = document.createElement('div');
        removeBtnWrapper.className = 'input-group-append';

        const removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.className = 'btn btn-danger';
        removeBtn.innerHTML = '<i class="fas fa-minus"></i>';
        removeBtn.addEventListener('click', () => {
            wrapper.remove();
            updateTextareaNames(section);
            updateNumbers(section);
        });

        removeBtnWrapper.appendChild(removeBtn);

        wrapper.appendChild(span);
        wrapper.appendChild(textarea);
        wrapper.appendChild(removeBtnWrapper);

        return wrapper;
    }

    function updateTextareaNames(section) {
        const container = document.getElementById(`${section}Container`);
        const textareas = container.querySelectorAll('textarea');
        textareas.forEach((textarea, idx) => {
            textarea.name = `${section}_list`;
        });
    }

    function updateNumbers(section) {
        const container = document.getElementById(`${section}Container`);
        const spans = container.querySelectorAll('.input-group-text');
        spans.forEach((span, idx) => {
            span.textContent = `${idx + 1}.`;
        });
    }

    function getNumber(section) {
        const container = document.getElementById(`${section}Container`);
        return container.querySelectorAll('.input-group').length;
    }

    function capitalize(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
});
