let isEditable = true;

// Toggle the edit mode for checklist
function toggleEdit() {
    isEditable = !isEditable;
    const inputs = document.querySelectorAll('.check-item-name, .check-item-desc');
    inputs.forEach(input => {
        input.disabled = !isEditable;
    });
}

// Confirm the checklist (lock it)
function confirmChecklist() {
    isEditable = false;
    const inputs = document.querySelectorAll('.check-item-name, .check-item-desc');
    inputs.forEach(input => {
        input.disabled = true;
    });
}

// Add a new item to the checklist
function addItem() {
    const checklist = document.getElementById('checklist');
    const newItem = document.createElement('div');
    newItem.className = 'checklist-item';

    const totalItems = checklist.getElementsByClassName('checklist-item').length + 1;

    newItem.innerHTML = `
        <div class="checklist-item-number">${totalItems}</div>
        <input type="text" class="check-item-name" placeholder="Enter Name">
        <input type="text" class="check-item-desc" placeholder="Enter Description/Checkpoints">
        <input type="text" class="check-item-checkpoints" placeholder="Enter Checkpoints (comma separated)">
        <span class="delete-btn" onclick="deleteItem(this)">-</span>
    `;

    checklist.appendChild(newItem);
}

// Delete the current item from the checklist
function deleteItem(button) {
    button.parentElement.remove();
    updateItemNumbers(); // Re-number the remaining items
}

// Update the numbering of all checklist items
function updateItemNumbers() {
    const checklistItems = document.querySelectorAll('.checklist-item');
    checklistItems.forEach((item, index) => {
        const numberElem = item.querySelector('.checklist-item-number');
        numberElem.textContent = index + 1;
    });
}

// Validate the checklist (trigger Python backend validation)
async function validateChecklist() {
    // Collect checklist items from the form
    const checklistItems = document.querySelectorAll('.checklist-item');
    const checklistData = [];

    checklistItems.forEach(item => {
        const name = item.querySelector('.check-item-name').value;
        const description = item.querySelector('.check-item-desc').value;
        const checkpoints = item.querySelector('.check-item-checkpoints').value.split(','); // assuming checkpoints are comma separated
        checklistData.push({ name, description, checkpoints });
    });

    // Create FormData to send files and checklist items
    const formData = new FormData();
    const fileUpload = document.getElementById('fileUpload');

    // Append each file to FormData
    for (let i = 0; i < fileUpload.files.length; i++) {
        formData.append('fileUpload', fileUpload.files[i]);
    }

    // Append the checklist items as a JSON string
    formData.append('checklist_items', JSON.stringify(checklistData));

    // Send the FormData to Flask backend
    fetch('/validate', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        // Process and display validation results
        let resultHtml = '<table><tr><th>Name</th><th>Document</th><th>Result</th></tr>';
        data.forEach(result => {
            const resultClass = result.result.includes('✅') ? 'passed' : 'failed';
            resultHtml += `
                <tr>
                    <td>${result.item}</td>
                    <td><a href="${result.file_url}" target="_blank">${result.document}</a></td>
                    <td class="${resultClass}">${result.result.includes('✅') ? '✔️' : '❌'}</td>
                </tr>
            `;
        });
        resultHtml += '</table>';
        document.getElementById('results').innerHTML = resultHtml;
    })
    .catch(error => console.error('
