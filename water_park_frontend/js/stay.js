// Must be logged in to book a stay
requireLogin();

let selectedRoom = "";
let roomPrice = 0;
let roomsByName = {}; // "Standard Room" -> {id, price_per_night}

// Fetch real room IDs from the backend so we know what to submit.
// The room cards in stay.html already have the name+price hardcoded;
// we just need the matching database ID for each one.
async function loadRooms() {
    try {
        const rooms = await apiFetch("/stay/rooms");
        rooms.forEach(room => {
            roomsByName[room.name] = room;
        });
    } catch (err) {
        console.error("Could not load rooms:", err);
        alert("Could not load room list from the server. Is the backend running?");
    }
}

function selectRoom(room, price) {
    selectedRoom = room;
    roomPrice = price;

    document.getElementById("roomType").value = room;
    document.getElementById("roomPrice").value = "₹" + price;

    calculateTotal();
}

function calculateTotal() {
    if (selectedRoom === "") return;

    let checkin = new Date(document.getElementById("checkin").value);
    let checkout = new Date(document.getElementById("checkout").value);
    let rooms = Number(document.getElementById("rooms").value);
    if (rooms < 1) rooms = 1;

    let nights = 0;
    if (!isNaN(checkin) && !isNaN(checkout)) {
        let diff = checkout - checkin;
        nights = Math.ceil(diff / (1000 * 60 * 60 * 24));
        if (nights < 1) nights = 1;
    }

    let subtotal = roomPrice * rooms * nights;
    let gst = subtotal * 0.18;
    let total = subtotal + gst;

    document.getElementById("summaryRoom").innerHTML = selectedRoom;
    document.getElementById("summaryPrice").innerHTML = "₹" + roomPrice;
    document.getElementById("summaryRooms").innerHTML = rooms;
    document.getElementById("totalNights").innerHTML = nights;
    document.getElementById("gstAmount").innerHTML = "₹" + gst.toFixed(2);
    document.getElementById("grandTotal").innerHTML = "<strong>₹" + total.toFixed(2) + "</strong>";
}

document.getElementById("checkin").addEventListener("change", calculateTotal);
document.getElementById("checkout").addEventListener("change", calculateTotal);
document.getElementById("rooms").addEventListener("input", calculateTotal);

document.getElementById("stayForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    if (selectedRoom === "") {
        alert("Please select a room.");
        return;
    }

    const room = roomsByName[selectedRoom];
    if (!room) {
        alert("Room list is still loading, please try again in a moment.");
        return;
    }

    const payload = {
        room_id: room.id,
        customer_name: document.getElementById("customerName").value,
        mobile: document.getElementById("mobile").value,
        checkin_date: document.getElementById("checkin").value,
        checkout_date: document.getElementById("checkout").value,
        guests: Number(document.getElementById("guests").value),
        rooms_count: Number(document.getElementById("rooms").value),
    };

    try {
        const booking = await apiFetch("/stay/bookings", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        alert(
            "🏨 Stay Booking Successful!\n\n" +
            "Booking ID: " + booking.booking_code +
            "\nRoom: " + selectedRoom +
            "\nTotal: ₹" + booking.total_amount
        );

        document.getElementById("stayForm").reset();
        selectedRoom = "";
        roomPrice = 0;

        document.getElementById("summaryRoom").innerHTML = "Not Selected";
        document.getElementById("summaryPrice").innerHTML = "₹0";
        document.getElementById("summaryRooms").innerHTML = "1";
        document.getElementById("totalNights").innerHTML = "0";
        document.getElementById("gstAmount").innerHTML = "₹0";
        document.getElementById("grandTotal").innerHTML = "<strong>₹0</strong>";
    } catch (err) {
        alert("❌ Stay booking failed: " + err.message);
    }
});

loadRooms();
