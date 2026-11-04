function setupRecipeBuilder(initialIngredients){
    const ingredients = initialIngredients.slice()
    const form = document.getElementById("recipe-form")
    const heading = document.getElementById('builder-heading')
    const list = document.getElementById('builder-list')
    const nameInput = document.getElementById('builder-name')
    const quantityInput = document.getElementById("builder-quantity")
    const unitSelect = document.getElementById("builder-unit")
    const addButton = document.getElementById("builder-add")
    const errorBox = document.getElementById("builder-error")
    const jsonInput = document.getElementById("builder-json")

    function formatIngredient(item){
        return `${item.name}: ${item.quantity}${item.unit}`
    }
    function showError(message){
        errorBox.textContent = message
        errorBox.hidden = false
    }
    function render(){
        list.innerHTML = ""
        heading.textContent = `Ingredients (${ingredients.length})`
        if (ingredients.length === 0){
            const empty = document.createElement("li")
            empty.textContent = "Nothing added yet"
            list.appendChild(empty)
        }
        ingredients.forEach(function (item, index){
            const li = document.createElement("li")
            li.classList.add("ingredients-item")
            const span = document.createElement("span")
            span.classList.add("ingredient-text")
            span.textContent = formatIngredient(item)
            const editBtn = document.createElement("button")
            editBtn.type = "button"
            editBtn.textContent = "Edit"
            editBtn.classList.add("edit-button")
            editBtn.addEventListener('click', function () {
                nameInput.value = item.name
                quantityInput.value = item.quantity
                unitSelect.value = item.unit
                ingredients.splice(index, 1)
                errorBox.hidden = true
                render()
                quantityInput.focus()
            })
            const removeBtn = document.createElement("button")
            removeBtn.type = "button"
            removeBtn.textContent = "Remove"
            removeBtn.classList.add("remove-button")
            removeBtn.addEventListener('click', function (){
                ingredients.splice(index, 1)
                render()
            })
            li.appendChild(span)
            li.appendChild(editBtn)
            li.appendChild(removeBtn)
            list.appendChild(li)
        })


    }
    

    function addIngredient(){
        const name = nameInput.value.trim()
        const quantityText = quantityInput.value.trim()
        const quantity = Number(quantityText)

        if (name === ""){
            showError("Enter an ingredient name")
            nameInput.focus()
            return
        }
        if (quantityText === "" || !Number.isFinite(quantity) || quantity <= 0){
            showError("Enter a quantity above zero")
            quantityInput.focus()
            return
        }
        errorBox.hidden = true
        ingredients.push({ name:name, quantity: quantity, unit: unitSelect.value })
        nameInput.value = ""
        quantityInput.value = ""
        render()
        nameInput.focus()
    }

    function addOnEnter(event){
        if (event.key === "Enter"){
            event.preventDefault()
            addIngredient()}
    }

    addButton.addEventListener("click", addIngredient)
    nameInput.addEventListener("keydown", addOnEnter)
    quantityInput.addEventListener("keydown", addOnEnter)

    form.addEventListener("submit", function (event) {
        console.log("Submitting ingredients:", JSON.stringify(ingredients));
        if (nameInput.value.trim() !== "" || quantityInput.value.trim() !== ""){
            event.preventDefault()
            showError("You've typed an ingredient but not added it - press Add first")
            return
        }
        if (ingredients.length === 0){
            event.preventDefault()
            showError("Add at least one ingredient")
            return
        }
        jsonInput.value = JSON.stringify(ingredients)
        console.log("Hidden input value:", jsonInput.value)
    })

    render()
}