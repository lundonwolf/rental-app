from flask import Blueprint, request, jsonify
from src.models.database import db
from src.models.utility import UtilityCategory, UtilityBill, UtilityBillSplit
from src.models.tenant import Tenant # Needed for splitting bills
import datetime
import csv
import io

utilities_bp = Blueprint("utilities_bp", __name__)

# --- Utility Category Routes --- 

# Create a new utility category
@utilities_bp.route("/categories", methods=["POST"])
def add_utility_category():
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "Missing required field: name"}), 400

    # Check if category already exists (case-insensitive)
    existing_category = UtilityCategory.query.filter(UtilityCategory.name.ilike(data["name"])).first()
    if existing_category:
        return jsonify({"error": f"Utility category 	'{data['name']}	' already exists."}), 409 # 409 Conflict

    try:
        new_category = UtilityCategory(
            name=data["name"],
            description=data.get("description")
        )
        db.session.add(new_category)
        db.session.commit()
        return jsonify(new_category.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500

# Get all utility categories
@utilities_bp.route("/categories", methods=["GET"])
def get_utility_categories():
    try:
        categories = UtilityCategory.query.order_by(UtilityCategory.name).all()
        return jsonify([category.to_dict() for category in categories]), 200
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

# Update a utility category
@utilities_bp.route("/categories/<int:category_id>", methods=["PUT"])
def update_utility_category(category_id):
    category = UtilityCategory.query.get_or_404(category_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        if "name" in data:
             # Check if new name conflicts with another category
            new_name = data["name"]
            existing_category = UtilityCategory.query.filter(UtilityCategory.name.ilike(new_name), UtilityCategory.id != category_id).first()
            if existing_category:
                return jsonify({"error": f"Utility category 	'{new_name}	' already exists."}), 409
            category.name = new_name
        if "description" in data: category.description = data["description"]

        db.session.commit()
        return jsonify(category.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500

# Delete a utility category (Caution: Deletes associated bills and splits due to cascade)
@utilities_bp.route("/categories/<int:category_id>", methods=["DELETE"])
def delete_utility_category(category_id):
    category = UtilityCategory.query.get_or_404(category_id)
    try:
        db.session.delete(category)
        db.session.commit()
        return jsonify({"message": f"Utility category 	'{category.name}	' and associated bills deleted successfully."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500

# --- Utility Bill Routes --- 

# Add a new utility bill
@utilities_bp.route("/bills", methods=["POST"])
def add_utility_bill():
    data = request.get_json()
    required_fields = ["category_id", "billing_period_start", "billing_period_end", "total_amount"]
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": f"Missing required fields: {', '.join(required_fields)}"}), 400

    # Validate category exists
    category = UtilityCategory.query.get(data["category_id"])
    if not category:
        return jsonify({"error": f"Utility category with ID {data['category_id']} not found."}), 404

    try:
        start_date = datetime.date.fromisoformat(data["billing_period_start"])
        end_date = datetime.date.fromisoformat(data["billing_period_end"])
        bill_date = datetime.date.fromisoformat(data["bill_date"]) if data.get("bill_date") else datetime.date.today()

        new_bill = UtilityBill(
            category_id=data["category_id"],
            billing_period_start=start_date,
            billing_period_end=end_date,
            bill_date=bill_date,
            total_amount=float(data["total_amount"]),
            usage_data=data.get("usage_data"),
            notes=data.get("notes"),
            file_path=data.get("file_path") # Handle file upload separately if needed
        )
        db.session.add(new_bill)
        db.session.commit()

        # Auto-split bill equally among active tenants if requested (or by default?)
        # Add a flag or config for this later. For now, manual split.

        return jsonify(new_bill.to_dict()), 201
    except ValueError as e:
         return jsonify({"error": f"Invalid data format: {e}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500

# Get all utility bills (potentially filtered/paginated later)
@utilities_bp.route("/bills", methods=["GET"])
def get_utility_bills():
    try:
        # Add filtering by category, date range etc. later
        bills = UtilityBill.query.order_by(UtilityBill.billing_period_end.desc()).all()
        return jsonify([bill.to_dict() for bill in bills]), 200
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

# Get a specific utility bill
@utilities_bp.route("/bills/<int:bill_id>", methods=["GET"])
def get_utility_bill(bill_id):
    try:
        bill = UtilityBill.query.get_or_404(bill_id)
        bill_data = bill.to_dict()
        # Include split details
        splits = UtilityBillSplit.query.filter_by(bill_id=bill_id).all()
        bill_data["splits"] = [split.to_dict() for split in splits]
        return jsonify(bill_data), 200
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

# Update a utility bill
@utilities_bp.route("/bills/<int:bill_id>", methods=["PUT"])
def update_utility_bill(bill_id):
    bill = UtilityBill.query.get_or_404(bill_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        if "category_id" in data:
            category = UtilityCategory.query.get(data["category_id"])
            if not category: return jsonify({"error": f"Utility category ID {data['category_id']} not found."}), 404
            bill.category_id = data["category_id"]
        if "billing_period_start" in data: bill.billing_period_start = datetime.date.fromisoformat(data["billing_period_start"])
        if "billing_period_end" in data: bill.billing_period_end = datetime.date.fromisoformat(data["billing_period_end"])
        if "bill_date" in data: bill.bill_date = datetime.date.fromisoformat(data["bill_date"]) if data["bill_date"] else None
        if "total_amount" in data: bill.total_amount = float(data["total_amount"])
        if "usage_data" in data: bill.usage_data = data["usage_data"]
        if "notes" in data: bill.notes = data["notes"]
        if "file_path" in data: bill.file_path = data["file_path"]

        db.session.commit()
        return jsonify(bill.to_dict()), 200
    except ValueError as e:
         return jsonify({"error": f"Invalid data format: {e}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500

# Delete a utility bill
@utilities_bp.route("/bills/<int:bill_id>", methods=["DELETE"])
def delete_utility_bill(bill_id):
    bill = UtilityBill.query.get_or_404(bill_id)
    try:
        db.session.delete(bill)
        db.session.commit()
        return jsonify({"message": f"Utility bill {bill_id} deleted successfully."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500

# --- Utility Bill Split Routes --- 

# Split a bill (manual for now, could be automated based on active tenants)
@utilities_bp.route("/bills/<int:bill_id>/split", methods=["POST"])
def split_utility_bill(bill_id):
    bill = UtilityBill.query.get_or_404(bill_id)
    data = request.get_json()
    # Expected data format: { "splits": [ { "tenant_id": X, "amount_owed": Y }, ... ] }
    if not data or "splits" not in data or not isinstance(data["splits"], list):
        return jsonify({"error": "Invalid data format. Expected {'splits': [{'tenant_id': X, 'amount_owed': Y}, ...]}"}), 400

    total_split_amount = sum(item.get("amount_owed", 0) for item in data["splits"]) 
    # Basic validation: check if split total matches bill total (allow small tolerance for float issues)
    if abs(total_split_amount - bill.total_amount) > 0.01:
        return jsonify({"error": f"Total split amount (${total_split_amount:.2f}) does not match bill total (${bill.total_amount:.2f})."}), 400

    try:
        # Remove existing splits for this bill before adding new ones
        UtilityBillSplit.query.filter_by(bill_id=bill_id).delete()

        new_splits = []
        for item in data["splits"]:
            tenant_id = item.get("tenant_id")
            amount_owed = item.get("amount_owed")
            if tenant_id is None or amount_owed is None:
                raise ValueError("Each split must have 'tenant_id' and 'amount_owed'.")
            
            # Validate tenant exists
            tenant = Tenant.query.get(tenant_id)
            if not tenant:
                 raise ValueError(f"Tenant with ID {tenant_id} not found.")

            split = UtilityBillSplit(
                bill_id=bill_id,
                tenant_id=tenant_id,
                amount_owed=float(amount_owed),
                is_paid=item.get("is_paid", False), # Allow setting initial paid status
                paid_date=datetime.date.fromisoformat(item["paid_date"]) if item.get("paid_date") else None
            )
            new_splits.append(split)
        
        db.session.add_all(new_splits)
        db.session.commit()
        return jsonify([s.to_dict() for s in new_splits]), 201

    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": f"Invalid split data: {e}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500

# Update a specific split (e.g., mark as paid)
@utilities_bp.route("/splits/<int:split_id>", methods=["PUT"])
def update_utility_split(split_id):
    split = UtilityBillSplit.query.get_or_404(split_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        if "amount_owed" in data: split.amount_owed = float(data["amount_owed"])
        if "is_paid" in data: 
            split.is_paid = bool(data["is_paid"])
            # Set paid_date if marking as paid and date not provided
            if split.is_paid and not split.paid_date and "paid_date" not in data:
                split.paid_date = datetime.date.today()
        if "paid_date" in data: 
            split.paid_date = datetime.date.fromisoformat(data["paid_date"]) if data["paid_date"] else None
            # If setting paid_date, ensure is_paid is True
            if split.paid_date:
                split.is_paid = True
            
        db.session.commit()
        # After updating a split, maybe re-check if the total split amount still matches the bill total?
        # This could get complex if allowing individual split amount edits.
        return jsonify(split.to_dict()), 200
    except ValueError as e:
         return jsonify({"error": f"Invalid data format: {e}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500

# --- CSV Import Route --- 

# Define expected CSV format
# Example: category_name,billing_start,billing_end,total_amount,bill_date(optional),usage(optional),notes(optional)
CSV_HEADERS = ["category_name", "billing_start", "billing_end", "total_amount", "bill_date", "usage", "notes"]

@utilities_bp.route("/bills/import_csv", methods=["POST"])
def import_utility_bills_csv():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if not file or not file.filename.lower().endswith('.csv'):
        return jsonify({"error": "Invalid file type. Please upload a CSV file."}), 400

    try:
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        if not csv_reader.fieldnames or not all(h in csv_reader.fieldnames for h in CSV_HEADERS[:4]): # Check required headers
             return jsonify({"error": f"CSV file must contain headers: {', '.join(CSV_HEADERS[:4])}. Found: {csv_reader.fieldnames}"}), 400

        imported_bills = []
        errors = []
        line_num = 1 # For error reporting

        # Cache categories to avoid repeated DB lookups
        categories_cache = {cat.name.lower(): cat.id for cat in UtilityCategory.query.all()}

        for row in csv_reader:
            line_num += 1
            try:
                category_name = row.get("category_name", "").strip()
                billing_start_str = row.get("billing_start", "").strip()
                billing_end_str = row.get("billing_end", "").strip()
                total_amount_str = row.get("total_amount", "").strip()

                if not all([category_name, billing_start_str, billing_end_str, total_amount_str]):
                    errors.append(f"Line {line_num}: Missing required data (category_name, billing_start, billing_end, total_amount).")
                    continue

                # Find or create category ID
                category_id = categories_cache.get(category_name.lower())
                if not category_id:
                    # Option 1: Error out
                    # errors.append(f"Line {line_num}: Utility category '{category_name}' not found. Please create it first.")
                    # continue
                    # Option 2: Create category on the fly (use with caution)
                    new_cat = UtilityCategory(name=category_name)
                    db.session.add(new_cat)
                    db.session.flush() # Get the ID before commit
                    category_id = new_cat.id
                    categories_cache[category_name.lower()] = category_id
                    print(f"Created new category: {category_name}")

                start_date = datetime.date.fromisoformat(billing_start_str)
                end_date = datetime.date.fromisoformat(billing_end_str)
                total_amount = float(total_amount_str)
                bill_date = datetime.date.fromisoformat(row["bill_date"].strip()) if row.get("bill_date", "").strip() else datetime.date.today()
                usage = row.get("usage", "").strip() or None
                notes = row.get("notes", "").strip() or None

                new_bill = UtilityBill(
                    category_id=category_id,
                    billing_period_start=start_date,
                    billing_period_end=end_date,
                    bill_date=bill_date,
                    total_amount=total_amount,
                    usage_data=usage,
                    notes=notes
                )
                db.session.add(new_bill)
                imported_bills.append(new_bill)

            except ValueError as e:
                errors.append(f"Line {line_num}: Invalid data format - {e}. Row: {row}")
            except Exception as e:
                errors.append(f"Line {line_num}: Unexpected error - {e}. Row: {row}")

        if errors:
            db.session.rollback() # Rollback all changes if any error occurred
            return jsonify({"error": "Errors occurred during import. No bills were added.", "details": errors}), 400
        else:
            db.session.commit()
            return jsonify({"message": f"Successfully imported {len(imported_bills)} utility bills.", "imported_ids": [bill.id for bill in imported_bills]}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to process CSV file: {str(e)}"}), 500

