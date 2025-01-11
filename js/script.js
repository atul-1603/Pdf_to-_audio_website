document.addEventListener("DOMContentLoaded", function() {
    const loginForm = document.getElementById("loginForm");
    const signupForm = document.getElementById("signupForm");
    
    // Replace with your actual backend URL (for local development, use http://localhost:5000)
    const backendUrl = "http://127.0.0.1:5000"; // Replace with your backend URL

    // Handle Login Form Submit
    if (loginForm) {
        loginForm.addEventListener("submit", function(e) {
            e.preventDefault();

            const username = document.getElementById("loginUsername").value;
            const password = document.getElementById("loginPassword").value;

            const data = {
                username: username,
                password: password
            };

            // Send POST request to the backend
            fetch(`${backendUrl}/login`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = "dashboard.html"; // Redirect to dashboard or homepage
                } else {
                    alert("Login failed. Please check your credentials.");
                }
            })
            .catch(error => {
                console.error("Error:", error);
                alert("An error occurred. Please try again later.");
            });
        });
    }

    // Handle Signup Form Submit
    if (signupForm) {
        signupForm.addEventListener("submit", function(e) {
            e.preventDefault();

            const username = document.getElementById("signupUsername").value;
            const password = document.getElementById("signupPassword").value;
            // const email = document.getElementById("signupEmail").value;

            const data = {
                username: username,
                password: password,
                // email: email
            };

            console.log(data)

            // Send POST request to the backend
            fetch(`${backendUrl}/register`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert("Registration successful! You can now login.");
                    window.location.href = "login.html"; // Redirect to login page
                } else {
                    alert("Registration failed. Please try again.");
                }
            })
            .catch(error => {
                console.error("Error:", error);
                alert("An error occurred. Please try again later.");
            });
        });
    }
    
    // Handle PDF File Upload (if applicable)
    const uploadForm = document.getElementById("uploadForm");
    if (uploadForm) {
        uploadForm.addEventListener("submit", function(e) {
            e.preventDefault();
            const formData = new FormData(uploadForm);
            const pdfFile = document.getElementById("pdfFile").files[0];
            formData.append("pdfFile", pdfFile);

            // Send POST request for PDF upload
            fetch(`${backendUrl}/upload`, {
                method: "POST",
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert("PDF uploaded successfully!");
                    // Optionally, update the UI with the file data
                } else {
                    alert("PDF upload failed. Please try again.");
                }
            })
            .catch(error => {
                console.error("Error:", error);
                alert("An error occurred. Please try again later.");
            });
        });
    }
});
