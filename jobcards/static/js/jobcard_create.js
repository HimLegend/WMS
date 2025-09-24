document.addEventListener("DOMContentLoaded", () => {
    // Set default date and time
    const now = new Date();
    const dateInput = document.getElementById("id_date");
    const timeInput = document.getElementById("id_time");
    
    if (dateInput) dateInput.value = now.toISOString().split('T')[0];
    if (timeInput) timeInput.value = now.toTimeString().slice(0, 5);

    // Initialize job notes button
    const addNoteBtn = document.getElementById("add-note");
    if (addNoteBtn) {
        addNoteBtn.addEventListener("click", () => {
            addInputRow("job-notes-container");
        });
    }

    // Setup form submission handler
    const form = document.querySelector("form");
    if (form) {
        form.addEventListener("submit", handleFormSubmit);
    }
});

// Add a new input row to a container with optional initial value
function addInputRow(containerId, value = "") {
    const container = document.getElementById(containerId);
    if (!container) return;

    const inputGroup = document.createElement("div");
    inputGroup.className = "input-group mb-2";

    const input = document.createElement("input");
    input.type = "text";
    input.className = "form-control";
    input.value = value;

    // Set input name based on container ID
    switch (containerId) {
        case "required_jobs_list": input.name = "required_jobs[]"; break;
        case "customer_comments_list": input.name = "customer_comments[]"; break;
        case "workshop_comments_list": input.name = "workshop_comments[]"; break;
        case "job-notes-container": input.name = "job_notes[]"; break;
        default: input.name = ""; break;
    }

    // Add (+) button to add new input row (except for job notes)
    if (containerId !== "job-notes-container") {
        const addBtn = document.createElement("button");
        addBtn.type = "button";
        addBtn.className = "btn btn-outline-secondary";
        addBtn.textContent = "+";
        addBtn.addEventListener("click", () => addInputRow(containerId));
        inputGroup.appendChild(addBtn);
    }

    // Remove (−) button to remove this input row
    const removeBtn = document.createElement("button");
    removeBtn.type = "button";
    removeBtn.className = "btn btn-outline-danger ms-1";
    removeBtn.textContent = "−";
    removeBtn.addEventListener("click", () => inputGroup.remove());
    
    inputGroup.appendChild(input);
    inputGroup.appendChild(removeBtn);
    container.appendChild(inputGroup);
}

// Handle form submission
function handleFormSubmit(e) {
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

    // Gather values from all input groups
    const requiredJobsValue = gatherInputValues("required_jobs_list");
    const customerCommentsValue = gatherInputValues("customer_comments_list");
    const workshopCommentsValue = gatherInputValues("workshop_comments_list");
    const jobNotesValue = gatherInputValues("job-notes-container");

    // Update hidden fields if they exist
    const hiddenRequiredJobs = document.getElementById("id_required_jobs");
    const hiddenCustomerComments = document.getElementById("id_customer_comments");
    const hiddenWorkshopComments = document.getElementById("id_workshop_comments");
    const hiddenJobNotes = document.getElementById("id_job_notes");

    if (hiddenRequiredJobs) hiddenRequiredJobs.value = requiredJobsValue;
    if (hiddenCustomerComments) hiddenCustomerComments.value = customerCommentsValue;
    if (hiddenWorkshopComments) hiddenWorkshopComments.value = workshopCommentsValue;
    if (hiddenJobNotes) hiddenJobNotes.value = jobNotesValue;
}
