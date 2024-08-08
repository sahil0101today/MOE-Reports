function showAlert(alertId) {
    var alertElement = document.getElementById(alertId);
    alertElement.style.display = 'block';
    setTimeout(function() {
        alertElement.style.display = 'none';
    }, 3000);
}

document.getElementById('submitForm').addEventListener('submit', function(e) {
    e.preventDefault();

    var url = document.getElementById('url').value;
    var recipients = document.getElementById('recipients').value;
    var email = sessionStorage.getItem('email');
    var password = sessionStorage.getItem('password');

    // Replace this with your GitHub repository details
    var githubRepo = 'sahil0101today/MOE-Reports';
    var githubToken = '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';

    // Create a GitHub API URL to trigger the workflow dispatch
    var apiUrl = `https://api.github.com/repos/${githubRepo}/actions/workflows/MOE_reports.yml/dispatches`;

    fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Authorization': `token ${githubToken}`,
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            ref: 'main', // The branch you want to run the workflow on
            inputs: {
                url: url,
                recipients: recipients,
                email: email,
                password: password
            }
        })
    }).then(response => {
        if(response.ok) {
            showAlert('successAlert');
            document.getElementById('submitForm').reset();
        } else {
            response.json().then(data => {
                console.error('Error:', data);
                showAlert('errorAlert');
            });
        }
    }).catch(error => {
        console.error('Error:', error);
        showAlert('errorAlert');
    });
});
