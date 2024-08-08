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
        }),
        mode: 'cors' // Ensures CORS is handled properly
    }).then(response => response.text()) // Use .text() to handle the response
    .then(text => {
        if (text === 'Success') {
            showAlert('successAlert');
            document.getElementById('submitForm').reset();
        } else {
            console.error('Error:', text);
            showAlert('errorAlert');
        }
    }).catch(error => {
        console.error('Error:', error);
        showAlert('errorAlert');
    });
});
