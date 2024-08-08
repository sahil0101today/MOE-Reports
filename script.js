document.getElementById('submitForm').addEventListener('submit', function(e) {
    e.preventDefault();

    var url = document.getElementById('url').value;
    var recipients = document.getElementById('recipients').value;
    var email = sessionStorage.getItem('email');
    var password = sessionStorage.getItem('password');

    // Replace this with your Google Apps Script Web App URL
    var googleAppsScriptUrl = 'https://script.google.com/macros/s/AKfycbyE5l1_Sb9-lAaC2veuTe3-2dxboGsXTUBNCRKOmkir7gxHcqaAtFxauaGHgkmD27VY/exec';

    // Prepare form data
    var formData = new FormData();
    formData.append('url', url);
    formData.append('recipients', recipients);
    formData.append('email', email);
    formData.append('password', password);

    // Send data to Google Apps Script
    fetch(googleAppsScriptUrl, {
        method: 'POST',
        body: formData,
        mode: 'cors' // Ensure CORS is handled properly
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.message || 'Error');
            });
        }
        return response.json(); // Expect JSON response from server
    })
    .then(data => {
        if (data.redirectUrl) {
            // Show success alert
            showAlert('successAlert');
            document.getElementById('submitForm').reset();
        } else {
            // Show error alert
            showAlert('errorAlert');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('errorAlert');
    });
});
