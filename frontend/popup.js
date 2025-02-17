document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('redactionForm');
    const fileInput = document.getElementById('pdfFile');
    const redactBtn = document.getElementById('redactBtn');

    fileInput.addEventListener('change', function() {
        redactBtn.disabled = !this.files.length;
    });

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const formData = new FormData();
        const file = fileInput.files[0];
        formData.append('file', file);

        // Add selected filters
        const filters = Array.from(document.querySelectorAll('input[name="filters"]:checked'))
            .map(input => input.value);
        filters.forEach(filter => formData.append('filters', filter));

        redactBtn.disabled = true;
        redactBtn.textContent = 'Processing...';

        try {
            const response = await fetch('http://localhost:7678/redact', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Server returned ${response.status}`);
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);

            // Download the redacted file
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'redacted_document.pdf';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);

            redactBtn.textContent = 'Redaction Complete!';
            setTimeout(() => {
                redactBtn.textContent = 'Redact Document';
                redactBtn.disabled = false;
            }, 2000);

        } catch (error) {
            console.error('Error:', error);
            redactBtn.textContent = `Error - ${error.message}`; // Display error message
            redactBtn.disabled = false;
        }
    });
});