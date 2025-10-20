API_URL = "http://localhost:8000"
document.getElementById("registerForm").addEventListener("submit", async function (event) {
    event.preventDefault();

    let name = document.getElementById("name").value;
    let email = document.getElementById("email").value;
    let password = document.getElementById("password").value;
    let confirmPassword = document.getElementById("confirmPassword").value;

    if (password !== confirmPassword) {
        showMessage("Passwords do not match!", "red");
        return;
    }

    let userData = {
        name: name,
        email: email,
        password: password
    };

    try {
        let response = await fetch(`${API_URL}/auth/register`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(userData)
        });

        let result = await response.json(); // Fix: Properly parse JSON response

        if (result.success === "False") {
            showMessage(result.message, "red"); // Show error in red
        } else {
            showMessage(result.message, "green"); // Show success in green
            setTimeout(() => {
                window.location.href = "/static/authentication/html/login.html"; // Redirect to login page
            }, 2000); // Delay redirect for user to read message
        }
    } catch (error) {
        console.error("Error:", error);
        showMessage("Something went wrong! Please try again.", "red");
    }
});

// Function to show messages in a colored bar
function showMessage(message, color) {
    let messageBox = document.createElement("div");
    messageBox.innerText = message;
    messageBox.style.position = "fixed";
    messageBox.style.top = "10px";
    messageBox.style.left = "50%";
    messageBox.style.transform = "translateX(-50%)";
    messageBox.style.backgroundColor = color;
    messageBox.style.color = "white";
    messageBox.style.padding = "10px 20px";
    messageBox.style.borderRadius = "5px";
    messageBox.style.fontSize = "16px";
    messageBox.style.zIndex = "1000";

    document.body.appendChild(messageBox);

    setTimeout(() => {
        messageBox.remove();
    }, 3000);
}
