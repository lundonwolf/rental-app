document.addEventListener("DOMContentLoaded", () => {
    // --- DOM Elements --- 
    // Navigation
    const navTenantsBtn = document.getElementById("nav-tenants");
    const navUtilitiesBtn = document.getElementById("nav-utilities");
    // Sections
    const tenantsSection = document.getElementById("tenants-section");
    const tenantDetailsSection = document.getElementById("tenant-details-section");
    const utilitiesSection = document.getElementById("utilities-section");
    const billDetailsSection = document.getElementById("bill-details-section");
    const mainSections = document.querySelectorAll(".main-section");

    // Tenant Elements
    const tenantList = document.getElementById("tenant-list");
    const addTenantBtn = document.getElementById("add-tenant-btn");
    const tenantModal = document.getElementById("tenant-modal");
    const tenantForm = document.getElementById("tenant-form");
    const tenantModalTitle = document.getElementById("tenant-modal-title");
    const tenantIdInput = document.getElementById("tenant-id");
    const tenantNameInput = document.getElementById("tenant-name");
    const tenantEmailInput = document.getElementById("tenant-email");
    const tenantPhoneInput = document.getElementById("tenant-phone");
    const tenantMoveInInput = document.getElementById("tenant-move-in");
    const tenantRentInput = document.getElementById("tenant-rent");
    const tenantNotesInput = document.getElementById("tenant-notes");
    const tenantActiveInput = document.getElementById("tenant-active");
    const tenantDetailsName = document.getElementById("tenant-details-name");
    const tenantInfoDiv = document.getElementById("tenant-info");
    const backToTenantsBtn = document.getElementById("back-to-tenants-btn");

    // Payment Elements
    const paymentList = document.getElementById("payment-list");
    const addPaymentBtn = document.getElementById("add-payment-btn");
    const paymentModal = document.getElementById("payment-modal");
    const paymentForm = document.getElementById("payment-form");
    const paymentModalTitle = document.getElementById("payment-modal-title");
    const paymentIdInput = document.getElementById("payment-id");
    const paymentTenantIdInput = document.getElementById("payment-tenant-id");
    const paymentAmountInput = document.getElementById("payment-amount");
    const paymentDateInput = document.getElementById("payment-date");
    const paymentMethodInput = document.getElementById("payment-method");
    const paymentNotesInput = document.getElementById("payment-notes");

    // Utility Category Elements
    const categoryList = document.getElementById("category-list");
    const addCategoryBtn = document.getElementById("add-category-btn");
    const categoryModal = document.getElementById("category-modal");
    const categoryForm = document.getElementById("category-form");
    const categoryModalTitle = document.getElementById("category-modal-title");
    const categoryIdInput = document.getElementById("category-id");
    const categoryNameInput = document.getElementById("category-name");
    const categoryDescriptionInput = document.getElementById("category-description");
    const categoryFilterSelect = document.getElementById("category-filter");
    const billCategorySelect = document.getElementById("bill-category"); // In bill modal

    // Utility Bill Elements
    const billList = document.getElementById("bill-list");
    const addBillBtn = document.getElementById("add-bill-btn");
    const billModal = document.getElementById("bill-modal");
    const billForm = document.getElementById("bill-form");
    const billModalTitle = document.getElementById("bill-modal-title");
    const billIdInput = document.getElementById("bill-id");
    const billStartDateInput = document.getElementById("bill-start-date");
    const billEndDateInput = document.getElementById("bill-end-date");
    const billDateInput = document.getElementById("bill-date");
    const billAmountInput = document.getElementById("bill-amount");
    const billUsageInput = document.getElementById("bill-usage");
    const billNotesInput = document.getElementById("bill-notes");
    const billDetailsHeader = document.getElementById("bill-details-header");
    const billInfoDiv = document.getElementById("bill-info");
    const backToUtilitiesBtn = document.getElementById("back-to-utilities-btn");

    // CSV Import Elements
    const importCsvBtn = document.getElementById("import-csv-btn");
    const csvImportModal = document.getElementById("csv-import-modal");
    const csvImportForm = document.getElementById("csv-import-form");
    const csvFileInput = document.getElementById("csv-file");
    const csvImportStatus = document.getElementById("csv-import-status");

    // Bill Split Elements
    const splitList = document.getElementById("split-list");
    const manageSplitBtn = document.getElementById("manage-split-btn");
    const splitModal = document.getElementById("split-modal");
    const splitForm = document.getElementById("split-form");
    const splitModalTitle = document.getElementById("split-modal-title");
    const splitBillIdInput = document.getElementById("split-bill-id");
    const splitTenantInputsDiv = document.getElementById("split-tenant-inputs");
    const splitBillTotalSpan = document.getElementById("split-bill-total");
    const splitCalculatedTotalSpan = document.getElementById("split-calculated-total");
    const splitWarning = document.getElementById("split-warning");
    const splitEquallyBtn = document.getElementById("split-equally-btn");

    // --- State Variables --- 
    let currentTenantId = null;
    let currentBillId = null;
    let utilityCategories = []; // Cache categories
    let activeTenants = []; // Cache active tenants for splitting

    // --- API Helper --- 
    async function apiRequest(url, method = "GET", body = null, isFormData = false) {
        const options = {
            method,
            headers: {},
        };
        if (isFormData) {
            options.body = body; // FormData sets Content-Type automatically
        } else if (body) {
            options.headers["Content-Type"] = "application/json";
            options.body = JSON.stringify(body);
        }
        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }
            if (response.status === 204 || response.headers.get("content-length") === "0") {
                return null; // Handle no content responses
            }
            return await response.json();
        } catch (error) {
            console.error("API Request Error:", error);
            alert(`Error: ${error.message}`);
            throw error; // Re-throw to handle in calling function if needed
        }
    }

    // --- Navigation --- 
    function showSection(sectionId) {
        mainSections.forEach(section => {
            section.style.display = section.id === sectionId ? "block" : "none";
        });
        // Reset details if going back to main lists
        if (sectionId === "tenants-section") currentTenantId = null;
        if (sectionId === "utilities-section") currentBillId = null;
    }

    // --- Modal Handling --- 
    window.closeModal = function(modalId) { // Make it global for onclick
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = "none";
        }
    }

    // Close modals if clicked outside content
    window.onclick = function(event) {
        if (event.target.classList.contains("modal")) {
            event.target.style.display = "none";
        }
    }

    // --- Tenant Functions --- 
    async function loadTenants(updateCache = true) {
        try {
            const tenants = await apiRequest("/api/tenants");
            if (updateCache) {
                activeTenants = tenants.filter(t => t.is_active);
            }
            tenantList.innerHTML = ""; // Clear list
            tenants.forEach(tenant => {
                const li = document.createElement("li");
                li.textContent = `${tenant.name} (Rent: $${tenant.base_rent_amount.toFixed(2)}) ${tenant.is_active ? "" : "(Inactive)"}`;
                li.dataset.tenantId = tenant.id;
                li.addEventListener("click", () => showTenantDetails(tenant.id));
                
                const editBtn = document.createElement("button");
                editBtn.textContent = "Edit";
                editBtn.classList.add("edit-btn");
                editBtn.onclick = (e) => { e.stopPropagation(); openTenantModal(tenant); };
                
                const deleteBtn = document.createElement("button");
                deleteBtn.textContent = tenant.is_active ? "Deactivate" : "Activate";
                deleteBtn.classList.add("delete-btn");
                deleteBtn.onclick = (e) => { e.stopPropagation(); toggleTenantStatus(tenant); };

                li.appendChild(deleteBtn);
                li.appendChild(editBtn);
                tenantList.appendChild(li);
            });
        } catch (error) { /* Handled by apiRequest */ }
    }

    function openTenantModal(tenant = null) {
        tenantForm.reset();
        if (tenant) {
            tenantModalTitle.textContent = "Edit Tenant";
            tenantIdInput.value = tenant.id;
            tenantNameInput.value = tenant.name;
            tenantEmailInput.value = tenant.email || "";
            tenantPhoneInput.value = tenant.phone || "";
            tenantMoveInInput.value = tenant.move_in_date || "";
            tenantRentInput.value = tenant.base_rent_amount;
            tenantNotesInput.value = tenant.notes || "";
            tenantActiveInput.checked = tenant.is_active;
        } else {
            tenantModalTitle.textContent = "Add Tenant";
            tenantIdInput.value = "";
            tenantActiveInput.checked = true; // Default to active
        }
        tenantModal.style.display = "block";
    }

    async function handleTenantFormSubmit(event) {
        event.preventDefault();
        const tenantData = {
            name: tenantNameInput.value,
            email: tenantEmailInput.value,
            phone: tenantPhoneInput.value,
            move_in_date: tenantMoveInInput.value || null,
            base_rent_amount: parseFloat(tenantRentInput.value),
            notes: tenantNotesInput.value,
            is_active: tenantActiveInput.checked,
        };

        const tenantId = tenantIdInput.value;
        const url = tenantId ? `/api/tenants/${tenantId}` : "/api/tenants";
        const method = tenantId ? "PUT" : "POST";

        try {
            await apiRequest(url, method, tenantData);
            closeModal(	"tenant-modal	");
            loadTenants(); // Refresh list and cache
        } catch (error) { /* Handled by apiRequest */ }
    }

    async function toggleTenantStatus(tenant) {
        const newStatus = !tenant.is_active;
        const action = newStatus ? "activate" : "deactivate";
        if (confirm(`Are you sure you want to ${action} tenant '${tenant.name}'?`)) {
            try {
                await apiRequest(`/api/tenants/${tenant.id}`, "PUT", { is_active: newStatus });
                loadTenants(); // Refresh list and cache
                // If currently viewing this tenant, refresh details
                if (currentTenantId === tenant.id) {
                    showTenantDetails(tenant.id);
                }
            } catch (error) { /* Handled by apiRequest */ }
        }
    }

    // --- Tenant Details & Payments --- 
    async function showTenantDetails(tenantId) {
        currentTenantId = tenantId;
        try {
            const tenant = await apiRequest(`/api/tenants/${tenantId}`);
            tenantDetailsName.textContent = `${tenant.name}	's Details`;
            tenantInfoDiv.innerHTML = `
                <p><strong>Email:</strong> ${tenant.email || 'N/A'}</p>
                <p><strong>Phone:</strong> ${tenant.phone || 'N/A'}</p>
                <p><strong>Move-in Date:</strong> ${tenant.move_in_date || 'N/A'}</p>
                <p><strong>Base Rent:</strong> $${tenant.base_rent_amount.toFixed(2)}</p>
                <p><strong>Status:</strong> ${tenant.is_active ? 'Active' : 'Inactive'}</p>
                <p><strong>Notes:</strong> ${tenant.notes || 'None'}</p>
            `;
            showSection("tenant-details-section");
            loadPayments(tenantId);
        } catch (error) {
            showSection("tenants-section"); // Go back if tenant fetch fails
        }
    }

    async function loadPayments(tenantId) {
        try {
            const payments = await apiRequest(`/api/payments/tenant/${tenantId}`);
            paymentList.innerHTML = ""; // Clear list
            let totalPaid = 0;
            payments.forEach(payment => {
                totalPaid += payment.amount;
                const li = document.createElement("li");
                li.textContent = `Date: ${payment.payment_date}, Amount: $${payment.amount.toFixed(2)}, Method: ${payment.payment_method || 'N/A'}`;
                if (payment.notes) {
                    li.textContent += ` (Notes: ${payment.notes})`;
                }
                
                const editBtn = document.createElement("button");
                editBtn.textContent = "Edit";
                editBtn.classList.add("edit-btn");
                editBtn.onclick = (e) => { e.stopPropagation(); openPaymentModal(payment); };
                
                const deleteBtn = document.createElement("button");
                deleteBtn.textContent = "Delete";
                deleteBtn.classList.add("delete-btn");
                deleteBtn.onclick = (e) => { e.stopPropagation(); deletePayment(payment.id); };

                li.appendChild(deleteBtn);
                li.appendChild(editBtn);
                paymentList.appendChild(li);
            });
        } catch (error) { /* Handled by apiRequest */ }
    }

    function openPaymentModal(payment = null) {
        paymentForm.reset();
        paymentTenantIdInput.value = currentTenantId; // Set tenant ID for new payments
        paymentDateInput.valueAsDate = new Date(); // Default to today

        if (payment) {
            paymentModalTitle.textContent = "Edit Payment";
            paymentIdInput.value = payment.id;
            paymentAmountInput.value = payment.amount;
            paymentDateInput.value = payment.payment_date;
            paymentMethodInput.value = payment.payment_method || "";
            paymentNotesInput.value = payment.notes || "";
        } else {
            paymentModalTitle.textContent = "Add Payment";
            paymentIdInput.value = "";
        }
        paymentModal.style.display = "block";
    }

    async function handlePaymentFormSubmit(event) {
        event.preventDefault();
        const paymentData = {
            amount: parseFloat(paymentAmountInput.value),
            payment_date: paymentDateInput.value,
            payment_method: paymentMethodInput.value,
            notes: paymentNotesInput.value,
        };

        const paymentId = paymentIdInput.value;
        const tenantId = paymentTenantIdInput.value;
        const url = paymentId ? `/api/payments/${paymentId}` : `/api/payments/tenant/${tenantId}`;
        const method = paymentId ? "PUT" : "POST";

        try {
            await apiRequest(url, method, paymentData);
            closeModal(	"payment-modal	");
            loadPayments(tenantId); // Refresh payment list for the current tenant
        } catch (error) { /* Handled by apiRequest */ }
    }

    async function deletePayment(paymentId) {
        if (confirm(`Are you sure you want to delete this payment record? This action cannot be undone.`)) {
            try {
                await apiRequest(`/api/payments/${paymentId}`, "DELETE");
                loadPayments(currentTenantId); // Refresh payment list
            } catch (error) { /* Handled by apiRequest */ }
        }
    }

    // --- Utility Category Functions --- 
    async function loadUtilityCategories(updateFilter = true, updateBillForm = true) {
        try {
            utilityCategories = await apiRequest("/api/utilities/categories");
            categoryList.innerHTML = ""; // Clear list
            
            // Populate filter dropdown
            if (updateFilter) {
                categoryFilterSelect.innerHTML = 	'<option value="all">All Categories</option>	';
                utilityCategories.forEach(cat => {
                    const option = document.createElement("option");
                    option.value = cat.id;
                    option.textContent = cat.name;
                    categoryFilterSelect.appendChild(option);
                });
            }
            // Populate bill form dropdown
            if (updateBillForm) {
                 billCategorySelect.innerHTML = 	'<option value="">Select Category</option>	';
                 utilityCategories.forEach(cat => {
                    const option = document.createElement("option");
                    option.value = cat.id;
                    option.textContent = cat.name;
                    billCategorySelect.appendChild(option);
                });
            }

            // Populate category list UI
            utilityCategories.forEach(cat => {
                const li = document.createElement("li");
                li.textContent = cat.name;
                li.dataset.categoryId = cat.id;
                // Add Edit and Delete buttons
                const editBtn = document.createElement("button");
                editBtn.textContent = "Edit";
                editBtn.classList.add("edit-btn");
                editBtn.onclick = (e) => { e.stopPropagation(); openCategoryModal(cat); };
                
                const deleteBtn = document.createElement("button");
                deleteBtn.textContent = "Delete";
                deleteBtn.classList.add("delete-btn");
                deleteBtn.onclick = (e) => { e.stopPropagation(); deleteCategory(cat.id, cat.name); };

                li.appendChild(deleteBtn);
                li.appendChild(editBtn);
                categoryList.appendChild(li);
            });
        } catch (error) { /* Handled by apiRequest */ }
    }

    function openCategoryModal(category = null) {
        categoryForm.reset();
        if (category) {
            categoryModalTitle.textContent = "Edit Category";
            categoryIdInput.value = category.id;
            categoryNameInput.value = category.name;
            categoryDescriptionInput.value = category.description || "";
        } else {
            categoryModalTitle.textContent = "Add Category";
            categoryIdInput.value = "";
        }
        categoryModal.style.display = "block";
    }

    async function handleCategoryFormSubmit(event) {
        event.preventDefault();
        const categoryData = {
            name: categoryNameInput.value,
            description: categoryDescriptionInput.value,
        };

        const categoryId = categoryIdInput.value;
        const url = categoryId ? `/api/utilities/categories/${categoryId}` : "/api/utilities/categories";
        const method = categoryId ? "PUT" : "POST";

        try {
            await apiRequest(url, method, categoryData);
            closeModal(	"category-modal	");
            loadUtilityCategories(); // Refresh list and dropdowns
            loadBills(); // Refresh bills as category names might change
        } catch (error) { /* Handled by apiRequest */ }
    }

    async function deleteCategory(categoryId, categoryName) {
        if (confirm(`Are you sure you want to delete category '${categoryName}'? This will also delete all associated bills and splits.`)) {
            try {
                await apiRequest(`/api/utilities/categories/${categoryId}`, "DELETE");
                loadUtilityCategories(); // Refresh list and dropdowns
                loadBills(); // Refresh bills as some might be deleted
            } catch (error) { /* Handled by apiRequest */ }
        }
    }

    // --- Utility Bill Functions --- 
    async function loadBills() {
        try {
            // TODO: Add filtering based on categoryFilterSelect.value
            const bills = await apiRequest("/api/utilities/bills");
            billList.innerHTML = ""; // Clear list
            bills.forEach(bill => {
                const li = document.createElement("li");
                li.textContent = `${bill.category_name}: ${bill.billing_period_start} to ${bill.billing_period_end} - $${bill.total_amount.toFixed(2)}`;
                li.dataset.billId = bill.id;
                li.addEventListener("click", () => showBillDetails(bill.id));

                const editBtn = document.createElement("button");
                editBtn.textContent = "Edit";
                editBtn.classList.add("edit-btn");
                editBtn.onclick = (e) => { e.stopPropagation(); openBillModal(bill); };
                
                const deleteBtn = document.createElement("button");
                deleteBtn.textContent = "Delete";
                deleteBtn.classList.add("delete-btn");
                deleteBtn.onclick = (e) => { e.stopPropagation(); deleteBill(bill.id); };

                li.appendChild(deleteBtn);
                li.appendChild(editBtn);
                billList.appendChild(li);
            });
        } catch (error) { /* Handled by apiRequest */ }
    }

    function openBillModal(bill = null) {
        billForm.reset();
        // Ensure categories are loaded in the dropdown
        if (billCategorySelect.options.length <= 1) {
             loadUtilityCategories(false, true); // Don't update filter, just bill form
        }
        billDateInput.valueAsDate = new Date(); // Default bill date

        if (bill) {
            billModalTitle.textContent = "Edit Bill";
            billIdInput.value = bill.id;
            billCategorySelect.value = bill.category_id;
            billStartDateInput.value = bill.billing_period_start;
            billEndDateInput.value = bill.billing_period_end;
            billDateInput.value = bill.bill_date || "";
            billAmountInput.value = bill.total_amount;
            billUsageInput.value = bill.usage_data || "";
            billNotesInput.value = bill.notes || "";
        } else {
            billModalTitle.textContent = "Add Bill";
            billIdInput.value = "";
        }
        billModal.style.display = "block";
    }

    async function handleBillFormSubmit(event) {
        event.preventDefault();
        const billData = {
            category_id: parseInt(billCategorySelect.value),
            billing_period_start: billStartDateInput.value,
            billing_period_end: billEndDateInput.value,
            bill_date: billDateInput.value || null,
            total_amount: parseFloat(billAmountInput.value),
            usage_data: billUsageInput.value,
            notes: billNotesInput.value,
        };

        if (!billData.category_id) {
            alert("Please select a category.");
            return;
        }

        const billId = billIdInput.value;
        const url = billId ? `/api/utilities/bills/${billId}` : "/api/utilities/bills";
        const method = billId ? "PUT" : "POST";

        try {
            await apiRequest(url, method, billData);
            closeModal(	"bill-modal	");
            loadBills(); // Refresh list
        } catch (error) { /* Handled by apiRequest */ }
    }

    async function deleteBill(billId) {
        if (confirm(`Are you sure you want to delete this bill record? This action cannot be undone.`)) {
            try {
                await apiRequest(`/api/utilities/bills/${billId}`, "DELETE");
                loadBills(); // Refresh list
                 // If viewing this bill, go back to list
                if (currentBillId === billId) {
                    showSection("utilities-section");
                }
            } catch (error) { /* Handled by apiRequest */ }
        }
    }

    // --- CSV Import Functions --- 
    function openCsvImportModal() {
        csvImportForm.reset();
        csvImportStatus.textContent = "";
        csvImportModal.style.display = "block";
    }

    async function handleCsvImportFormSubmit(event) {
        event.preventDefault();
        const file = csvFileInput.files[0];
        if (!file) {
            alert("Please select a CSV file.");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        csvImportStatus.textContent = "Importing...";
        try {
            const result = await apiRequest("/api/utilities/bills/import_csv", "POST", formData, true);
            csvImportStatus.textContent = result.message || "Import successful!";
            // Optionally show details: result.imported_ids
            loadUtilityCategories(); // Categories might have been added
            loadBills(); // Refresh bill list
            // Keep modal open to show status, or close after delay?
            // closeModal(	"csv-import-modal	"); 
        } catch (error) {
            csvImportStatus.textContent = `Import failed: ${error.message}`;
            if (error.details) { // Show detailed errors if provided by backend
                csvImportStatus.innerHTML += "<br>Details:<br>" + error.details.join("<br>");
            }
        }
    }

    // --- Bill Details & Splits --- 
    async function showBillDetails(billId) {
        currentBillId = billId;
        try {
            const bill = await apiRequest(`/api/utilities/bills/${billId}`);
            billDetailsHeader.textContent = `Bill Details: ${bill.category_name} (${bill.billing_period_start} - ${bill.billing_period_end})`;
            billInfoDiv.innerHTML = `
                <p><strong>Total Amount:</strong> $${bill.total_amount.toFixed(2)}</p>
                <p><strong>Bill Date:</strong> ${bill.bill_date || 'N/A'}</p>
                <p><strong>Usage:</strong> ${bill.usage_data || 'N/A'}</p>
                <p><strong>Notes:</strong> ${bill.notes || 'None'}</p>
            `;
            showSection("bill-details-section");
            displaySplits(bill.splits || []);
        } catch (error) {
            showSection("utilities-section"); // Go back if bill fetch fails
        }
    }

    function displaySplits(splits) {
        splitList.innerHTML = "";
        if (!splits || splits.length === 0) {
            splitList.innerHTML = "<li>No splits defined for this bill yet.</li>";
            return;
        }
        splits.forEach(split => {
            const li = document.createElement("li");
            li.textContent = `${split.tenant_name}: $${split.amount_owed.toFixed(2)} - ${split.is_paid ? 'Paid' : 'Unpaid'}`;
            if (split.is_paid && split.paid_date) {
                li.textContent += ` on ${split.paid_date}`;
            }
            // Add button to mark as paid/unpaid?
            const togglePaidBtn = document.createElement("button");
            togglePaidBtn.textContent = split.is_paid ? "Mark Unpaid" : "Mark Paid";
            togglePaidBtn.onclick = () => toggleSplitPaidStatus(split);
            li.appendChild(togglePaidBtn);

            splitList.appendChild(li);
        });
    }

    async function toggleSplitPaidStatus(split) {
        const newStatus = !split.is_paid;
        const updateData = { is_paid: newStatus };
        if (newStatus && !split.paid_date) {
            // Optionally prompt for date or just set to today
            updateData.paid_date = new Date().toISOString().split('T')[0]; 
        } else if (!newStatus) {
             updateData.paid_date = null; // Clear date if marking unpaid
        }

        try {
            const updatedSplit = await apiRequest(`/api/utilities/splits/${split.id}`, "PUT", updateData);
            // Refresh the details view
            showBillDetails(split.bill_id);
        } catch (error) { /* Handled by apiRequest */ }
    }

    // --- Manage Bill Split Modal --- 
    async function openSplitModal() {
        if (!currentBillId) return;

        splitForm.reset();
        splitTenantInputsDiv.innerHTML = "Loading tenants...";
        splitCalculatedTotalSpan.textContent = "0.00";
        splitWarning.style.display = "none";

        try {
            // Ensure active tenants are cached
            if (activeTenants.length === 0) {
                await loadTenants(true); 
            }
            const bill = await apiRequest(`/api/utilities/bills/${currentBillId}`);
            
            splitModalTitle.textContent = `Split Bill: ${bill.category_name} (${bill.billing_period_start} - ${bill.billing_period_end})`;
            splitBillIdInput.value = bill.id;
            splitBillTotalSpan.textContent = bill.total_amount.toFixed(2);
            
            splitTenantInputsDiv.innerHTML = ""; // Clear loading message
            const existingSplits = bill.splits ? bill.splits.reduce((acc, s) => { acc[s.tenant_id] = s.amount_owed; return acc; }, {}) : {};

            activeTenants.forEach(tenant => {
                const div = document.createElement("div");
                div.classList.add("split-tenant-row");
                const label = document.createElement("label");
                label.textContent = `${tenant.name}: $`;
                const input = document.createElement("input");
                input.type = "number";
                input.step = "0.01";
                input.min = "0";
                input.dataset.tenantId = tenant.id;
                input.value = (existingSplits[tenant.id] || 0).toFixed(2);
                input.addEventListener("input", calculateSplitTotal);
                
                div.appendChild(label);
                div.appendChild(input);
                splitTenantInputsDiv.appendChild(div);
            });

            calculateSplitTotal(); // Initial calculation
            splitModal.style.display = "block";

        } catch (error) {
            splitTenantInputsDiv.innerHTML = "Error loading data.";
        }
    }

    function calculateSplitTotal() {
        let total = 0;
        const inputs = splitTenantInputsDiv.querySelectorAll("input[type='number']");
        inputs.forEach(input => {
            total += parseFloat(input.value) || 0;
        });
        splitCalculatedTotalSpan.textContent = total.toFixed(2);

        const billTotal = parseFloat(splitBillTotalSpan.textContent);
        if (Math.abs(total - billTotal) > 0.01) {
            splitWarning.style.display = "block";
        } else {
            splitWarning.style.display = "none";
        }
    }

    function splitEqually() {
        const inputs = splitTenantInputsDiv.querySelectorAll("input[type='number']");
        const numTenants = inputs.length;
        if (numTenants === 0) return;

        const billTotal = parseFloat(splitBillTotalSpan.textContent);
        const amountPerTenant = (billTotal / numTenants).toFixed(2);
        // Adjust last tenant for rounding differences
        const remainder = billTotal - (amountPerTenant * numTenants);

        inputs.forEach((input, index) => {
            let amount = parseFloat(amountPerTenant);
            if (index === numTenants - 1) { // Last tenant gets remainder
                 amount += remainder;
            }
            input.value = amount.toFixed(2);
        });
        calculateSplitTotal();
    }

    async function handleSplitFormSubmit(event) {
        event.preventDefault();
        const billId = splitBillIdInput.value;
        const billTotal = parseFloat(splitBillTotalSpan.textContent);
        const inputs = splitTenantInputsDiv.querySelectorAll("input[type='number']");
        let calculatedTotal = 0;
        const splitsData = [];

        inputs.forEach(input => {
            const amount = parseFloat(input.value) || 0;
            calculatedTotal += amount;
            if (amount > 0) { // Only include tenants with non-zero amount
                splitsData.push({
                    tenant_id: parseInt(input.dataset.tenantId),
                    amount_owed: amount
                });
            }
        });

        if (Math.abs(calculatedTotal - billTotal) > 0.01) {
            alert("Warning: The total split amount does not match the bill total. Please adjust the amounts.");
            return;
        }

        try {
            await apiRequest(`/api/utilities/bills/${billId}/split`, "POST", { splits: splitsData });
            closeModal(	"split-modal	");
            showBillDetails(billId); // Refresh details view
        } catch (error) { /* Handled by apiRequest */ }
    }

    // --- Event Listeners --- 
    // Navigation
    navTenantsBtn.addEventListener("click", () => showSection("tenants-section"));
    navUtilitiesBtn.addEventListener("click", () => showSection("utilities-section"));

    // Tenants
    addTenantBtn.addEventListener("click", () => openTenantModal());
    tenantForm.addEventListener("submit", handleTenantFormSubmit);
    backToTenantsBtn.addEventListener("click", () => showSection("tenants-section"));

    // Payments
    addPaymentBtn.addEventListener("click", () => openPaymentModal());
    paymentForm.addEventListener("submit", handlePaymentFormSubmit);

    // Utility Categories
    addCategoryBtn.addEventListener("click", () => openCategoryModal());
    categoryForm.addEventListener("submit", handleCategoryFormSubmit);

    // Utility Bills
    addBillBtn.addEventListener("click", () => openBillModal());
    billForm.addEventListener("submit", handleBillFormSubmit);
    backToUtilitiesBtn.addEventListener("click", () => showSection("utilities-section"));
    // categoryFilterSelect.addEventListener("change", loadBills); // Add filtering later

    // CSV Import
    importCsvBtn.addEventListener("click", openCsvImportModal);
    csvImportForm.addEventListener("submit", handleCsvImportFormSubmit);

    // Bill Splits
    manageSplitBtn.addEventListener("click", openSplitModal);
    splitEquallyBtn.addEventListener("click", splitEqually);
    splitForm.addEventListener("submit", handleSplitFormSubmit);

    // --- Initial Load --- 
    showSection("tenants-section"); // Start on tenants page
    loadTenants();
    loadUtilityCategories(); // Load categories for dropdowns
    loadBills(); // Load initial bills
});

