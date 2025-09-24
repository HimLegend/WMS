document.addEventListener("DOMContentLoaded", () => {
    // Utility: Add a new input row to a container with optional initial value
    function addInputRow(containerId, value = "") {
        const container = document.getElementById(containerId);
        if (!container) return;

        const inputGroup = document.createElement("div");
        inputGroup.className = "input-group mb-2";

        const input = document.createElement("input");
        input.type = "text";
        input.className = "form-control";
        input.value = value;
        input.placeholder = containerId === "job-notes-container" ? "Enter note..." : "";

        // Set input name based on container ID
        switch (containerId) {
            case "required_jobs_list": input.name = "required_jobs[]"; break;
            case "customer_comments_list": input.name = "customer_comments[]"; break;
            case "workshop_comments_list": input.name = "workshop_comments[]"; break;
            case "job-notes-container": input.name = "job_notes[]"; break;
            default: input.name = ""; break;
        }

        // Add (+) button to add new input row
        const addBtn = document.createElement("button");
        addBtn.type = "button";
        addBtn.className = "btn btn-outline-secondary";
        addBtn.innerHTML = '<i class="fas fa-plus"></i>';
        addBtn.addEventListener("click", (e) => {
            e.preventDefault();
            addInputRow(containerId);
        });

        // Remove (−) button to remove this input row
        const removeBtn = document.createElement("button");
        removeBtn.type = "button";
        removeBtn.className = "btn btn-outline-danger ms-1";
        removeBtn.innerHTML = '<i class="fas fa-minus"></i>';
        removeBtn.addEventListener("click", (e) => {
            e.preventDefault();
            inputGroup.remove();
        });

        inputGroup.appendChild(input);
        if (containerId !== "job-notes-container") {
            inputGroup.appendChild(addBtn);
        }
        inputGroup.appendChild(removeBtn);
        container.appendChild(inputGroup);
    }

    // Prefill inputs from multiline string (split by newline)
    function prefillInputList(containerId, rawText) {
        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = ""; // Clear existing

        if (!rawText || rawText.trim() === "") {
            addInputRow(containerId);
            return;
        }

        const lines = rawText.split(/\r?\n/).filter(line => line.trim() !== "");
        lines.forEach(line => addInputRow(containerId, line));
    }

    // Event delegation for remove buttons inside specified containers
    const containers = ['required_jobs_list', 'customer_comments_list', 'workshop_comments_list', 'job-notes-container'];
    containers.forEach(containerId => {
        const container = document.getElementById(containerId);
        if (!container) return;

        container.addEventListener('click', (e) => {
            if (e.target.closest('.btn-outline-danger') || e.target.closest('.remove-note')) {
                const inputGroup = e.target.closest('.input-group');
                if (inputGroup) {
                    inputGroup.remove();
                    // If container becomes empty, add a blank input row (except job-notes-container)
                    if (container.children.length === 0 && containerId !== "job-notes-container") {
                        addInputRow(containerId);
                    }
                }
            }
        });
    });

    // Prefill the comment/job sections from hidden inputs' values
    prefillInputList("required_jobs_list", document.getElementById("id_required_jobs")?.value);
    prefillInputList("customer_comments_list", document.getElementById("id_customer_comments")?.value);
    prefillInputList("workshop_comments_list", document.getElementById("id_workshop_comments")?.value);

    // Initialize add note buttons
    const addNoteButtons = document.querySelectorAll('[onclick*="addInputRow"]');
    addNoteButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            const containerId = button.getAttribute('onclick').match(/'([^']+)'/)[1];
            addInputRow(containerId);
        });
    });
    
    // Initialize remove note buttons
    document.addEventListener('click', (e) => {
        if (e.target.closest('.btn-outline-danger') || e.target.closest('.remove-note')) {
            e.preventDefault();
            const inputGroup = e.target.closest('.input-group');
            if (inputGroup) {
                const container = inputGroup.parentElement;
                inputGroup.remove();
                
                // If no more items in container and it's not job-notes, add a blank one
                if (container.children.length === 0 && !container.id.includes('job-notes')) {
                    addInputRow(container.id);
                }
            }
        }
    });

    // On form submit, gather all inputs back into hidden fields (except job-notes which you handle separately)
    const form = document.querySelector("form");
    if (form) {
        form.addEventListener("submit", () => {
            function gatherInputValues(containerId) {
                const container = document.getElementById(containerId);
                if (!container) return "";
                const inputs = container.querySelectorAll("input[type='text']");
                const values = [];
                inputs.forEach(input => {
                    const val = input.value.trim();
                    if (val !== "") values.push(val);
                });
                return values.join("\n");
            }

            const requiredJobsValue = gatherInputValues("required_jobs_list");
            const customerCommentsValue = gatherInputValues("customer_comments_list");
            const workshopCommentsValue = gatherInputValues("workshop_comments_list");
            const jobNotesValue = gatherInputValues("job-notes-container");

            const hiddenRequiredJobs = document.getElementById("id_required_jobs");
            const hiddenCustomerComments = document.getElementById("id_customer_comments");
            const hiddenWorkshopComments = document.getElementById("id_workshop_comments");
            const hiddenJobNotes = document.getElementById("id_job_notes");

            if (hiddenRequiredJobs) hiddenRequiredJobs.value = requiredJobsValue;
            if (hiddenCustomerComments) hiddenCustomerComments.value = customerCommentsValue;
            if (hiddenWorkshopComments) hiddenWorkshopComments.value = workshopCommentsValue;
            if (hiddenJobNotes) hiddenJobNotes.value = jobNotesValue;
        });
    }
});
