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

    // Replace this with your Google Apps Script Web App URL
    var googleAppsScriptUrl = 'https://script.google.com/macros/s/AKfycbyE5l1_Sb9-lAaC2veuTe3-2dxboGsXTUBNCRKOmkir7gxHcqaAtFxauaGHgkmD27VY/exec';

    fetch(googleAppsScriptUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            url: url,
            recipients: recipients,
            email: email,
            password: password
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
