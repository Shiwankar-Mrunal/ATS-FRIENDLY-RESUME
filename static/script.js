async function uploadResume() {
    const fileInput = document.getElementById('resumeFile');
    const jobDesc = document.getElementById('jobDescription').value;
    const resultDiv = document.getElementById('result');

    if (fileInput.files.length === 0 || jobDesc.trim() === "") {
        alert("Please upload resume and paste job description");
        return;
    }

    resultDiv.innerHTML = `<p>Scanning...</p>`;

    const formData = new FormData();
    formData.append("resume", fileInput.files[0]);
    formData.append("job_description", jobDesc);

    try {
        const response = await fetch("http://127.0.0.1:5000/scan", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error);
        }

        displayResult(data);

    } catch (error) {
        console.error(error);
        resultDiv.innerHTML = `<p style="color:red;">Error scanning resume</p>`;
    }
}

function displayResult(data) {
    const resultDiv = document.getElementById('result');

    resultDiv.innerHTML = `
        <div class="result-card">
            <h3>ATS Match Score</h3>
            <p><strong>${data.ats_score}%</strong></p>
        </div>

        <div class="result-card">
            <h3>NLP Similarity Score</h3>
            <p>${data.similarity_score}%</p>
        </div>

        <div class="result-card">
            <h3>Keyword Match</h3>
            <p>${data.keyword_score}%</p>
        </div>
    `;
}
