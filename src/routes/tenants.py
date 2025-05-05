from flask import Blueprint, request, jsonify
from src.models.database import db
from src.models.tenant import Tenant
from src.models.rent import RentPayment # Needed for calculating totals
import datetime

tenants_bp = Blueprint("tenants_bp", __name__)

# Create a new tenant
@tenants_bp.route("", methods=["POST"])
def add_tenant():
    data = request.get_json()
    if not data or not data.get("name") or data.get("base_rent_amount") is None:
        return jsonify({"error": "Missing required fields: name and base_rent_amount"}), 400

    try:
        move_in_date = None
        if data.get("move_in_date"):
            move_in_date = datetime.date.fromisoformat(data["move_in_date"])

        new_tenant = Tenant(
            name=data["name"],
            email=data.get("email"),
            phone=data.get("phone"),
            move_in_date=move_in_date,
            base_rent_amount=float(data["base_rent_amount"]),
            notes=data.get("notes"),
            is_active=data.get("is_active", True)
        )
        db.session.add(new_tenant)
        db.session.commit()
        return jsonify(new_tenant.to_dict()), 201
    except ValueError as e:
         return jsonify({"error": f"Invalid data format: {e}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500

# Get all active tenants
@tenants_bp.route("", methods=["GET"])
def get_tenants():
    try:
        tenants = Tenant.query.filter_by(is_active=True).order_by(Tenant.name).all()
        return jsonify([tenant.to_dict() for tenant in tenants]), 200
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

# Get a specific tenant by ID
@tenants_bp.route("/<int:tenant_id>", methods=["GET"])
def get_tenant(tenant_id):
    try:
        tenant = Tenant.query.get_or_404(tenant_id)
        # Optionally, calculate and add payment summary here if needed frequently
        # payment_total = db.session.query(db.func.sum(RentPayment.amount)).filter(RentPayment.tenant_id == tenant_id).scalar() or 0
        # tenant_data = tenant.to_dict()
        # tenant_data["total_paid"] = payment_total
        return jsonify(tenant.to_dict()), 200
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

# Update a tenant
@tenants_bp.route("/<int:tenant_id>", methods=["PUT"])
def update_tenant(tenant_id):
    tenant = Tenant.query.get_or_404(tenant_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        if "name" in data: tenant.name = data["name"]
        if "email" in data: tenant.email = data["email"]
        if "phone" in data: tenant.phone = data["phone"]
        if "move_in_date" in data:
             tenant.move_in_date = datetime.date.fromisoformat(data["move_in_date"]) if data["move_in_date"] else None
        if "base_rent_amount" in data: tenant.base_rent_amount = float(data["base_rent_amount"])
        if "notes" in data: tenant.notes = data["notes"]
        if "is_active" in data: tenant.is_active = bool(data["is_active"])

        db.session.commit()
        return jsonify(tenant.to_dict()), 200
    except ValueError as e:
         return jsonify({"error": f"Invalid data format: {e}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500

# Delete (deactivate) a tenant
@tenants_bp.route("/<int:tenant_id>", methods=["DELETE"])
def delete_tenant(tenant_id):
    tenant = Tenant.query.get_or_404(tenant_id)
    try:
        # Instead of deleting, we mark as inactive
        tenant.is_active = False
        db.session.commit()
        # Alternatively, to permanently delete:
        # db.session.delete(tenant)
        # db.session.commit()
        return jsonify({"message": f"Tenant {tenant_id} marked as inactive."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500

