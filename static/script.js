function setupLiveSearch(inputId, resultsId, items, onSelect) {
    const input = document.getElementById(inputId);
    const results = document.getElementById(resultsId);

    input.addEventListener("input", function () {
        const query = input.value.trim().toLowerCase();
        results.innerHTML = "";

        if (query === "") {
            return;
        }

        const matches = items.filter(function (name) {
            return name.toLowerCase().includes(query);
        });

        if (matches.length === 0) {
            const empty = document.createElement("li");
            empty.className = "search-empty";
            empty.textContent = "No matches";
            results.appendChild(empty);
            return;
        }

        matches.slice(0, 8).forEach(function (name) {
            const item = document.createElement("li");
            item.className = "search-result";
            item.textContent = name;
            item.addEventListener("click", function () {
                onSelect(name);
                results.innerHTML = "";
            });
            results.appendChild(item);
        });
    });
}

const RECENT_KEY = "smokehouseRecentRecipes";
const MAX_RECENT = 6;

function getRecent() {
    try {
        const stored = JSON.parse(localStorage.getItem(RECENT_KEY));
        return Array.isArray(stored) ? stored : [];
    } catch (error) {
        return [];
    }
}

function saveRecent(name) {
    const recent = getRecent().filter(function (item) {
        return item !== name;
    });
    recent.unshift(name);
    localStorage.setItem(RECENT_KEY, JSON.stringify(recent.slice(0, MAX_RECENT)));
}

function setupTableFilter(inputId, tableId) {
    const input = document.getElementById(inputId);
    const rows = document.querySelectorAll("#" + tableId + " tbody tr");

    input.addEventListener("input", function () {
        const query = input.value.trim().toLowerCase();
        rows.forEach(function (row) {
            const name = row.cells[0].textContent.toLowerCase();
            row.style.display = name.includes(query) ? "" : "none";
        });
    });
}

function showRecent(listId, validNames) {
    const list = document.getElementById(listId);
    list.innerHTML = "";

    const recent = getRecent().filter(function (name) {
        return validNames.includes(name);
    });

    if (recent.length === 0) {
        const empty = document.createElement("li");
        empty.className = "search-empty";
        empty.textContent = "Nothing searched yet";
        list.appendChild(empty);
        return;
    }

    recent.forEach(function (name) {
        const item = document.createElement("li");
        item.className = "recipe-card";
        const link = document.createElement("a");
        link.href = "/recipes/" + encodeURIComponent(name);
        link.textContent = name;
        item.appendChild(link);
        list.appendChild(item);
    });
}