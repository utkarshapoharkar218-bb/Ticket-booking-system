// Must be logged in to book a ticket
requireLogin();

let ADULT_PRICE = 800;
let CHILD_PRICE = 500;
let ADULT_TICKET_ID = null;
let CHILD_TICKET_ID = null;

const bookingForm = document.getElementById("bookingForm");
const adult = document.getElementById("adult");
const child = document.getElementById("child");
const food = document.getElementById("food");
const stay = document.getElementById("stay");
const rooms = document.getElementById("rooms");

const adultTotal = document.getElementById("adultTotal");
const childTotal = document.getElementById("childTotal");
const foodTotal = document.getElementById("foodTotal");
const stayTotal = document.getElementById("stayTotal");
const grandTotal = document.getElementById("grandTotal");

// Load real ticket type IDs + prices from the backend so we book against
// whatever the admin has actually configured (in case prices change later).
async function loadTicketTypes() {
    try {
        const types = await apiFetch("/ticket-types/");
        const adultType = types.find(t => t.name.toLowerCase() === "adult");
        const childType = types.find(t => t.name.toLowerCase() === "child");

        if (adultType) {
            ADULT_TICKET_ID = adultType.id;
            ADULT_PRICE = adultType.price;
        }
        if (childType) {
            CHILD_TICKET_ID = childType.id;
            CHILD_PRICE = childType.price;
        }

        calculateTotal();
    } catch (err) {
        console.error("Could not load ticket types:", err);
    }
}

function calculateTotal() {
    let adultCost = Number(adult.value) * ADULT_PRICE;
    let childCost = Number(child.value) * CHILD_PRICE;
    let foodCost = Number(food.value);
    let stayCost = Number(stay.value) * Number(rooms.value);
    let total = adultCost + childCost + foodCost + stayCost;

    adultTotal.innerHTML = "₹" + adultCost;
    childTotal.innerHTML = "₹" + childCost;
    foodTotal.innerHTML = "₹" + foodCost;
    stayTotal.innerHTML = "₹" + stayCost;
    grandTotal.innerHTML = "<strong>₹" + total + "</strong>";
}

adult.addEventListener("input", calculateTotal);
child.addEventListener("input", calculateTotal);
food.addEventListener("change", calculateTotal);
stay.addEventListener("change", calculateTotal);
rooms.addEventListener("input", calculateTotal);

bookingForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    const adultQty = Number(adult.value);
    const childQty = Number(child.value);

    if (adultQty === 0 && childQty === 0) {
        alert("Please select at least one ticket.");
        return;
    }

    const items = [];
    if (adultQty > 0 && ADULT_TICKET_ID) items.push({ ticket_type_id: ADULT_TICKET_ID, quantity: adultQty });
    if (childQty > 0 && CHILD_TICKET_ID) items.push({ ticket_type_id: CHILD_TICKET_ID, quantity: childQty });

    if (items.length === 0) {
        alert("Ticket types are still loading, please try again in a moment.");
        return;
    }

    const payload = {
        visit_date: document.getElementById("visitDate").value,
        booking_type: document.getElementById("bookingType").value,
        payment_method: document.getElementById("payment").value || null,
        address: document.getElementById("address").value || null,
        items: items,
    };

    try {
        const booking = await apiFetch("/bookings/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        alert(
            "🎉 Booking Successful!\n\n" +
            "Booking ID: " + booking.booking_code +
            "\nTotal Amount: ₹" + booking.total_amount
        );

        bookingForm.reset();
        calculateTotal();
    } catch (err) {
        alert("❌ Booking failed: " + err.message);
    }
});

loadTicketTypes();
