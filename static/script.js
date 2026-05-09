async function doRegister() {

    const name = document.getElementById("reg-name").value;
    const email = document.getElementById("reg-email").value;
    const password = document.getElementById("reg-password").value;

    const errorDiv = document.getElementById("reg-error");

    errorDiv.innerText = "";

    try {

        const response = await fetch("http://127.0.0.1:8000/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                name: name,
                email: email,
                password: password
            })
        });

        const data = await response.json();

        console.log("REGISTER RESPONSE:", data);
        console.log({
               name: name,
               email: email,
               password : password,
               type: typeof password
        });

        if (!response.ok) {

            errorDiv.innerText = data.detail || "Registration failed";
            return;
        }

        alert("✅ Registration successful!");

    } catch (error) {

        console.error("REGISTER ERROR:", error);

        errorDiv.innerText = "Server connection failed";

    }
}