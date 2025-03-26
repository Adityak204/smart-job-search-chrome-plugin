document.getElementById('searchBtn').addEventListener('click', async () => {
    const companies = document.getElementById('companies').value;
    const position = document.getElementById('position').value;
    const country = document.getElementById('country').value || 'United States';
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '<p>Searching... Please wait.</p>';

    try {
        const response = await fetch('http://127.0.0.1:8000/search_jobs/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                companies,
                position,
                country
            }),
            credentials: 'include' // Important for CORS with credentials
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        displayResults(data.job_urls);
    } catch (error) {
        resultsDiv.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
        console.error('Error:', error);
    }
});

function displayResults(jobData) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';

    if (!jobData || Object.keys(jobData).length === 0) {
        resultsDiv.innerHTML = '<p>No job openings found.</p>';
        return;
    }

    Object.entries(jobData).forEach(([company, platforms]) => {
        const companyDiv = document.createElement('div');
        companyDiv.style.marginBottom = '20px';
        companyDiv.innerHTML = `<h3>${company}</h3>`;

        Object.entries(platforms).forEach(([platform, urls]) => {
            if (urls && urls.length > 0) {
                const platformDiv = document.createElement('div');
                platformDiv.innerHTML = `<strong>${platform}:</strong>`;

                const list = document.createElement('ul');
                urls.forEach(url => {
                    const item = document.createElement('li');
                    const link = document.createElement('a');
                    link.href = url;
                    link.textContent = url.length > 50 ? url.substring(0, 50) + '...' : url;
                    link.target = '_blank';
                    link.rel = 'noopener noreferrer';
                    item.appendChild(link);
                    list.appendChild(item);
                });

                platformDiv.appendChild(list);
                companyDiv.appendChild(platformDiv);
            }
        });

        resultsDiv.appendChild(companyDiv);
    });
}