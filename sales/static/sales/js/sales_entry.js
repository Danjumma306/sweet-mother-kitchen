(function () {
    const ACTION_INC = "inc";
    const ACTION_DEC = "dec";
    const ACTION_REMOVE = "remove";
    const order_state = new Map();

    const item_grid = document.getElementById("item-grid");
    const order_lines = document.getElementById("order-lines");
    const order_empty = document.getElementById("order-empty");
    const order_fields = document.getElementById("order-fields");
    const grand_total = document.getElementById("grand-total");
    const save_sale = document.getElementById("save-sale");
    const payment_input = document.getElementById("payment_method_input");
    const menu_search = document.getElementById("menu-search");
    const cat_tabs = document.getElementById("cat-tabs");
    const pay_grid = document.getElementById("pay-grid");
    const category_all = cat_tabs.dataset.categoryAll || "all";

    let active_category = category_all;
    let search_query = "";

    function format_money(amount) {
        return amount.toFixed(2);
    }

    function line_key(item_id) {
        return String(item_id);
    }

    function sync_hidden_fields() {
        order_fields.innerHTML = "";
        order_state.forEach(function (line) {
            const item_input = document.createElement("input");
            item_input.type = "hidden";
            item_input.name = "item";
            item_input.value = line.item_id;

            const qty_input = document.createElement("input");
            qty_input.type = "hidden";
            qty_input.name = "quantity";
            qty_input.value = String(line.quantity);

            order_fields.appendChild(item_input);
            order_fields.appendChild(qty_input);
        });
    }

    function render_order() {
        const lines = Array.from(order_state.values());
        order_empty.style.display = lines.length ? "none" : "block";

        order_lines.querySelectorAll(".order-line").forEach(function (node) {
            node.remove();
        });

        let total = 0;
        lines.forEach(function (line) {
            const line_total = line.quantity * line.price;
            total += line_total;

            const row = document.createElement("div");
            row.className = "order-line";
            row.dataset.itemId = line.item_id;
            row.innerHTML =
                '<div>'
                + '<p class="order-line-name"></p>'
                + '<p class="order-line-unit"></p>'
                + '</div>'
                + '<div class="order-line-total"></div>'
                + '<div class="order-line-actions">'
                + '<div class="qty-stepper">'
                + '<button type="button" class="qty-btn" data-action="dec" aria-label="Decrease quantity">−</button>'
                + '<span class="qty-val"></span>'
                + '<button type="button" class="qty-btn" data-action="inc" aria-label="Increase quantity">+</button>'
                + '</div>'
                + '<button type="button" class="remove-line" data-action="remove" aria-label="Remove item">'
                + '<svg viewBox="0 0 24 24"><use href="#icon-trash"/></svg>'
                + '</button>'
                + '</div>';

            row.querySelector(".order-line-name").textContent = line.name;
            row.querySelector(".order-line-unit").textContent = "GH₵ " + format_money(line.price) + " each";
            row.querySelector(".order-line-total").textContent = "GH₵ " + format_money(line_total);
            row.querySelector(".qty-val").textContent = String(line.quantity);
            order_lines.appendChild(row);
        });

        grand_total.textContent = format_money(total);
        save_sale.disabled = lines.length === 0;
        sync_hidden_fields();
    }

    function add_item(card) {
        const item_id = card.dataset.itemId;
        const key = line_key(item_id);
        const existing = order_state.get(key);
        if (existing) {
            existing.quantity += 1;
        } else {
            order_state.set(key, {
                item_id: item_id,
                name: card.dataset.itemName,
                price: parseFloat(card.dataset.itemPrice || "0"),
                quantity: 1,
            });
        }
        render_order();
    }

    function filter_menu() {
        const cards = item_grid.querySelectorAll(".menu-card");
        cards.forEach(function (card) {
            const name = (card.dataset.itemName || "").toLowerCase();
            const category = card.dataset.category || "";
            const matches_category = active_category === category_all || category === active_category;
            const matches_search = !search_query || name.indexOf(search_query) !== -1;
            card.style.display = matches_category && matches_search ? "" : "none";
        });
    }

    item_grid.addEventListener("click", function (event) {
        const add_btn = event.target.closest(".item-add");
        if (!add_btn) {
            return;
        }
        const card = add_btn.closest(".menu-card");
        if (card) {
            add_item(card);
        }
    });

    order_lines.addEventListener("click", function (event) {
        const btn = event.target.closest("[data-action]");
        if (!btn) {
            return;
        }
        const row = btn.closest(".order-line");
        if (!row) {
            return;
        }
        const key = line_key(row.dataset.itemId);
        const line = order_state.get(key);
        if (!line) {
            return;
        }

        const action = btn.dataset.action;
        if (action === ACTION_INC) {
            line.quantity += 1;
        } else if (action === ACTION_DEC) {
            line.quantity -= 1;
            if (line.quantity < 1) {
                order_state.delete(key);
            }
        } else if (action === ACTION_REMOVE) {
            order_state.delete(key);
        }
        render_order();
    });

    cat_tabs.addEventListener("click", function (event) {
        const tab = event.target.closest(".cat-tab");
        if (!tab) {
            return;
        }
        active_category = tab.dataset.category || category_all;
        cat_tabs.querySelectorAll(".cat-tab").forEach(function (node) {
            node.classList.toggle("is-active", node === tab);
        });
        filter_menu();
    });

    menu_search.addEventListener("input", function () {
        search_query = menu_search.value.trim().toLowerCase();
        filter_menu();
    });

    pay_grid.addEventListener("click", function (event) {
        const option = event.target.closest(".pay-option");
        if (!option) {
            return;
        }
        pay_grid.querySelectorAll(".pay-option").forEach(function (node) {
            node.classList.toggle("is-selected", node === option);
        });
        payment_input.value = option.dataset.method;
    });

    render_order();
})();
