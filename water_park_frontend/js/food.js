// Must be logged in to place a food order
requireLogin();

let cart = [];
let foodItemsByName = {}; // "Veg Combo" -> {id, price}

// Fetch the real food item IDs from the backend so we can submit an order.
// The card buttons in food.html already know the name+price; we just need
// the matching database ID for each one.
async function loadFoodItems() {
    try {
        const items = await apiFetch("/food/items");
        items.forEach(item => {
            foodItemsByName[item.name] = item;
        });
    } catch (err) {
        console.error("Could not load food items:", err);
        alert("Could not load the food menu from the server. Is the backend running?");
    }
}

function addToCart(name, price, quantityId) {
    let qty = parseInt(document.getElementById(quantityId).value);

    if (isNaN(qty) || qty <= 0) {
        alert("Please enter a valid quantity.");
        return;
    }

    let existing = cart.find(item => item.name === name);
    if (existing) {
        existing.quantity = qty;
        existing.total = qty * price;
    } else {
        cart.push({ name: name, price: price, quantity: qty, total: qty * price });
    }

    updateCart();
}

function updateCart() {
    let table = document.getElementById("cartTable");
    table.innerHTML = "";
    let grandTotal = 0;

    if (cart.length === 0) {
        table.innerHTML = `<tr><td colspan="3" style="text-align:center">No items added.</td></tr>`;
    }

    cart.forEach(function (item) {
        grandTotal += item.total;
        table.innerHTML += `
        <tr>
        <td>${item.name}</td>
        <td>${item.quantity}</td>
        <td>₹${item.total}</td>
        </tr>
        `;
    });

    document.getElementById("grandTotal").innerHTML = "<strong>₹" + grandTotal + "</strong>";
}

document.getElementById("confirmBooking").addEventListener("click", async function () {
    if (cart.length === 0) {
        alert("Please add at least one food item.");
        return;
    }

    const items = [];
    for (const cartItem of cart) {
        const foodItem = foodItemsByName[cartItem.name];
        if (!foodItem) {
            alert("Menu is still loading, please try again in a moment.");
            return;
        }
        items.push({ food_item_id: foodItem.id, quantity: cartItem.quantity });
    }

    try {
        const order = await apiFetch("/food/orders", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ items }),
        });

        alert(
            "🎉 Food Booking Successful!\n\n" +
            "Order ID: " + order.order_code +
            "\nTotal Amount: ₹" + order.total_amount
        );

        clearCart();
    } catch (err) {
        alert("❌ Food order failed: " + err.message);
    }
});

document.getElementById("clearCart").addEventListener("click", clearCart);

function clearCart() {
    cart = [];
    document.getElementById("vegQty").value = 0;
    document.getElementById("burgerQty").value = 0;
    document.getElementById("pizzaQty").value = 0;
    document.getElementById("nonvegQty").value = 0;
    document.getElementById("friesQty").value = 0;
    document.getElementById("drinkQty").value = 0;
    document.getElementById("iceQty").value = 0;
    updateCart();
}

updateCart();
loadFoodItems();
