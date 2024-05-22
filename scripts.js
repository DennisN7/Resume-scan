/* scripts.js */
document.getElementById('resumeForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    
    const fileInput = document.getElementById('resumeFile');
    const formData = new FormData();
    formData.append('resume', fileInput.files[0]);

    const response = await fetch('/scan-resume', {
        method: 'POST',
        body: formData
    });

    const result = await response.json();

    document.getElementById('jobMatch').textContent = `Best Fitted Job: ${result.jobMatch}`;
    document.getElementById('resumeQuality').textContent = `Resume Quality: ${result.resumeQuality}%`;

    document.getElementById('results').style.display = 'block';
});
