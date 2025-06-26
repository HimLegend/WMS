document.addEventListener('DOMContentLoaded', function() {
    // Status update buttons
    document.querySelectorAll('.status-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            const jobcardId = this.dataset.id;
            const newStatus = this.dataset.status;
            
            fetch(`/api/jobcards/${jobcardId}/status/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({status: newStatus})
            })
            .then(response => response.json())
            .then(data => {
                if(data.success) {
                    location.reload();
                }
            });
        });
    });

    // DateTime picker initialization
    if(document.getElementById('id_estimated_completion')) {
        flatpickr('#id_estimated_completion', {
            enableTime: true,
            dateFormat: "Y-m-d H:i",
        });
    }
});

function getCookie(name) {
    // Cookie retrieval function
}