document.getElementById('searchBtn').addEventListener('click', async () => {
    const companies = document.getElementById('companies').value;
    const position = document.getElementById('position').value;
    const country = document.getElementById('country').value || 'United States';
    const resultsDiv = document.getElementById('results');

    try {
        // Use local development URL
        const response = await fetch('http://127.0.0.1:8000/search_jobs/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                companies,
                position,
                country
            })
        });

        const data = await response.json();

        // Clear previous results
        resultsDiv.innerHTML = '';

        // Display job URLs
        Object.entries(data.job_urls).forEach(([company, jobData]) => {
            const companyDiv = document.createElement('div');
            companyDiv.innerHTML = `<strong>${company} Job Openings:</strong>`;
            resultsDiv.appendChild(companyDiv);

            // LinkedIn Jobs
            if (jobData.LinkedIn && jobData.LinkedIn.length > 0) {
                const linkedinDiv = document.createElement('div');
                linkedinDiv.innerHTML = 'LinkedIn Jobs:';
                jobData.LinkedIn.forEach(url => {
                    const linkElement = document.createElement('a');
                    linkElement.href = url;
                    linkElement.textContent = url;
                    linkElement.target = '_blank';
                    linkedinDiv.appendChild(linkElement);
                    linkedinDiv.appendChild(document.createElement('br'));
                });
                resultsDiv.appendChild(linkedinDiv);
            }

            // Glassdoor Jobs
            if (jobData.Glassdoor && jobData.Glassdoor.length > 0) {
                const glassdoorDiv = document.createElement('div');
                glassdoorDiv.innerHTML = 'Glassdoor Jobs:';
                jobData.Glassdoor.forEach(url => {
                    const linkElement = document.createElement('a');
                    linkElement.href = url;
                    linkElement.textContent = url;
                    linkElement.target = '_blank';
                    glassdoorDiv.appendChild(linkElement);
                    glassdoorDiv.appendChild(document.createElement('br'));
                });
                resultsDiv.appendChild(glassdoorDiv);
            }

            // Add separator
            resultsDiv.appendChild(document.createElement('hr'));
        });
    } catch (error) {
        resultsDiv.textContent = `Error: ${error.message}`;
    }
});