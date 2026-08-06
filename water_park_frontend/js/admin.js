// Must be logged in AND be an admin to view this page
requireAdmin();

async function loadDashboard() {
    let ticketBookings = [];
    let foodOrders = [];
    let stayBookings = [];

    try {
        [ticketBookings, foodOrders, stayBookings] = await Promise.all([
            apiFetch("/bookings/"),
            apiFetch("/food/orders"),
            apiFetch("/stay/bookings"),
        ]);
    } catch (err) {
        alert("Could not load dashboard data: " + err.message);
        return;
    }

    document.getElementById("ticketCount").innerHTML = ticketBookings.length;
    document.getElementById("foodCount").innerHTML = foodOrders.length;
    document.getElementById("stayCount").innerHTML = stayBookings.length;

    let revenue = 0;

    // ---- Ticket bookings ----
    const ticketTable = document.getElementById("ticketTable");
    ticketBookings.forEach(function (booking) {
        if (booking.status === "cancelled") return;
        revenue += booking.total_amount;
        ticketTable.innerHTML += `
        <tr>
            <td>${booking.booking_code}</td>
            <td>${booking.customer_name || ""}</td>
            <td>${booking.visit_date}</td>
            <td>₹${booking.total_amount}</td>
        </tr>
        `;
    });

    // ---- Food orders ----
    const foodTable = document.getElementById("foodTable");
    foodOrders.forEach(function (order) {
        if (order.status === "cancelled") return;
        revenue += order.total_amount;
        const orderDate = new Date(order.created_at).toLocaleString();
        foodTable.innerHTML += `
        <tr>
            <td>${order.order_code}</td>
            <td>${orderDate}</td>
            <td>₹${order.total_amount}</td>
        </tr>
        `;
    });

    // ---- Stay bookings ----
    const stayTable = document.getElementById("stayTable");
    stayBookings.forEach(function (stay) {
        if (stay.status === "cancelled") return;
        revenue += stay.total_amount;
        stayTable.innerHTML += `
        <tr>
            <td>${stay.booking_code}</td>
            <td>${stay.customer_name}</td>
            <td>Room #${stay.room_id}</td>
            <td>₹${stay.total_amount.toFixed(2)}</td>
        </tr>
        `;
    });

    document.getElementById("totalRevenue").innerHTML = "₹" + revenue.toFixed(2);
}

document.getElementById("logoutBtn").addEventListener("click", function () {
    logout();
});

loadDashboard();
