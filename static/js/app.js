// =====================================
// K Wallet Frontend
// app.js - Part 1 (Authentication)
// =====================================

// -----------------------------
// Notification
// -----------------------------

function showNotification(message, type = "success") {

    const box = document.getElementById("notification");

    if (!box) return;

    box.innerHTML = `
        <div class="alert alert-${type}">
            ${message}
        </div>
    `;

    setTimeout(() => {
        box.innerHTML = "";
    }, 3000);
}


// -----------------------------
// Register
// -----------------------------

async function registerUser() {

    const username = document.getElementById("username").value.trim();
    const pin = document.getElementById("pin").value.trim();

    if (!username || !pin) {

        showNotification(
            "Please fill in all fields",
            "danger"
        );

        return;
    }

    try {

        const response = await fetch("/register", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                username,
                pin
            })

        });

        const data = await response.json();

        if (response.ok) {

            showNotification(
                `Account Created! Your account number is ${data.account}`
            );

            setTimeout(() => {

                window.location.href = "/login-page";

            }, 2500);

        } else {

            showNotification(
                data.error,
                "danger"
            );

        }

    }

    catch (err) {

        console.error(err);

        showNotification(
            "Server error",
            "danger"
        );

    }

}



// -----------------------------
// Login
// -----------------------------

async function loginUser() {

    const account = document
        .getElementById("loginAccount")
        .value
        .trim();

    const pin = document
        .getElementById("loginPin")
        .value
        .trim();

    if (!account || !pin) {

        showNotification(
            "Enter account and PIN",
            "danger"
        );

        return;

    }

    try {

        const response = await fetch("/login", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                account,
                pin
            })

        });

        const data = await response.json();

        if (response.ok) {

            localStorage.setItem(
                "username",
                data.username
            );

            localStorage.setItem(
                "balance",
                data.balance
            );

            localStorage.setItem(
                "account",
                account
            );

            showNotification(
                "Login Successful"
            );

            setTimeout(() => {

                window.location.href =
                    "/dashboard";

            }, 1000);

        }

        else {

            showNotification(
                data.error,
                "danger"
            );

        }

    }

    catch (err) {

        console.error(err);

        showNotification(
            "Server error",
            "danger"
        );

    }

}



// -----------------------------
// Logout
// -----------------------------

function logoutUser() {

    window.location.href = "/logout";

}



// -----------------------------
// Admin Login
// -----------------------------

async function adminLogin() {

    const username = document
        .getElementById("adminUsername")
        .value
        .trim();

    const password = document
        .getElementById("adminPassword")
        .value
        .trim();

    if (!username || !password) {

        showNotification(
            "Enter username and password",
            "danger"
        );

        return;

    }

    try {

        const response = await fetch("/admin-login", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                username,
                password

            })

        });

        const data = await response.json();

        if (response.ok) {

            showNotification(
                "Admin Login Successful"
            );

            setTimeout(() => {

                window.location.href =
                    "/admin";

            }, 1000);

        }

        else {

            showNotification(
                data.error,
                "danger"
            );

        }

    }

    catch (err) {

        console.error(err);

        showNotification(
            "Server error",
            "danger"
        );

    }

}


// =====================================
// Dashboard
// app.js - Part 2
// =====================================


// -----------------------------
// Load Dashboard
// -----------------------------

async function loadDashboard() {

    if (!document.getElementById("balance")) {

        return;

    }

    document.getElementById("welcome").innerText =
        localStorage.getItem("username") || "Welcome";

    document.getElementById("account").innerText =
        localStorage.getItem("account") || "";

    document.getElementById("balance").innerText =
        localStorage.getItem("balance") || "0";

    loadTransactions();

}



// -----------------------------
// Send Money
// -----------------------------

async function sendMoney() {

    const receiver =
        document.getElementById("receiver").value.trim();

    const amount =
        document.getElementById("amount").value.trim();

    if (!receiver || !amount) {

        showNotification(
            "Enter receiver and amount",
            "danger"
        );

        return;

    }

    try {

        const response = await fetch("/send", {

            method: "POST",

            headers: {

                "Content-Type":
                "application/json"

            },

            body: JSON.stringify({

                receiver,
                amount

            })

        });

        const data = await response.json();

        if (response.ok) {

            showNotification(data.message);

            document.getElementById("receiver").value = "";
            document.getElementById("amount").value = "";

            loadTransactions();

        }

        else {

            showNotification(
                data.error,
                "danger"
            );

        }

    }

    catch (err) {

        console.error(err);

        showNotification(
            "Server error",
            "danger"
        );

    }

}



// -----------------------------
// Transactions
// -----------------------------

async function loadTransactions() {

    const history =
        document.getElementById("history");

    if (!history) {

        return;

    }

    try {

        const response =
            await fetch("/history");

        const data =
            await response.json();

        history.innerHTML = "";

        if (data.length === 0) {

            history.innerHTML =

                "<p>No transactions yet.</p>";

            return;

        }

        data.forEach(tx => {

            history.innerHTML += `

                <div class="card p-3 mb-2">

                    <strong>

                        ${tx.type}

                    </strong>

                    <br>

                    KSh ${tx.amount}

                    <br>

                    ${tx.account}

                    <br>

                    <small>

                        ${tx.date}

                    </small>

                </div>

            `;

        });

    }

    catch (err) {

        console.error(err);

    }

}



// -----------------------------
// Upload Profile Photo
// -----------------------------

async function uploadPhoto() {

    const input =
        document.getElementById("photoInput");

    if (!input || input.files.length === 0) {

        showNotification(
            "Choose a photo first",
            "danger"
        );

        return;

    }

    const form =
        new FormData();

    form.append(
        "photo",
        input.files[0]
    );

    try {

        const response =
            await fetch("/upload-photo", {

                method: "POST",

                body: form

            });

        const data =
            await response.json();

        if (response.ok) {

            showNotification(
                "Photo Updated"
            );

            document
                .getElementById("profile-photo")
                .src = data.photo;

        }

        else {

            showNotification(
                data.error,
                "danger"
            );

        }

    }

    catch (err) {

        console.error(err);

    }

}



// -----------------------------
// Auto Load Dashboard
// -----------------------------

document.addEventListener(

    "DOMContentLoaded",

    function () {

        loadDashboard();

    }

);


// =====================================
// K Wallet
// app.js - Part 3 (Admin Dashboard)
// =====================================


// -----------------------------
// Load Admin Dashboard
// -----------------------------

async function loadAdminDashboard() {

    if (!document.getElementById("users")) {

        return;

    }

    try {

        // --------------------
        // Statistics
        // --------------------

        const stats = await fetch("/admin/stats")
            .then(r => r.json());

        document.getElementById("users").innerText =
            stats.users;

        document.getElementById("transactions").innerText =
            stats.transactions;

        document.getElementById("money").innerText =
            stats.money;


        // --------------------
        // Users
        // --------------------

        const users = await fetch("/admin/users")
            .then(r => r.json());

        let usersHTML = "";

        users.forEach(user => {

            usersHTML += `
                <tr>
                    <td>${user.username}</td>
                    <td>${user.account}</td>
                    <td>KSh ${user.balance}</td>
                </tr>
            `;

        });

        document.getElementById("usersTable").innerHTML =
            usersHTML;


        // --------------------
        // Transactions
        // --------------------

        const tx = await fetch("/admin/transactions")
            .then(r => r.json());

        let txHTML = "";

        tx.forEach(item => {

            txHTML += `
                <tr>
                    <td>${item.from}</td>
                    <td>${item.to}</td>
                    <td>KSh ${item.amount}</td>
                    <td>${item.date}</td>
                </tr>
            `;

        });

        document.getElementById("transactionsTable").innerHTML =
            txHTML;


        // --------------------
        // Line Chart
        // --------------------

        const chart =
            await fetch("/admin/chart")
            .then(r => r.json());

        const lineCanvas =
            document.getElementById("lineChart");

        if (lineCanvas) {

            new Chart(lineCanvas, {

                type: "line",

                data: {

                    labels: chart.labels,

                    datasets: [{

                        label: "Transactions",

                        data: chart.values,

                        borderWidth: 3,

                        tension: 0.4,

                        fill: false

                    }]

                }

            });

        }


        // --------------------
        // Pie Chart
        // ----------------------------

        const pie =
            await fetch("/admin/pie")
            .then(r => r.json());

        const pieCanvas =
            document.getElementById("pieChart");

        if (pieCanvas) {

            new Chart(pieCanvas, {

                type: "pie",

                data: {

                    labels: [

                        "Money Sent",

                        "Wallet Balances"

                    ],

                    datasets: [{

                        data: [

                            pie.sent,

                            pie.wallets

                        ]

                    }]

                }

            });

        }

    }

    catch (err) {

        console.error(err);

        showNotification(

            "Failed to load admin dashboard",

            "danger"

        );

    }

}



// -----------------------------
// Auto Load Admin Dashboard
// -----------------------------

document.addEventListener(

    "DOMContentLoaded",

    function () {

        loadAdminDashboard();

    }

);
