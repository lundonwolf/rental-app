from flask import Blueprint, request, jsonify
from src.models.database import db
from src.models.rent import RentPayment
from src.models.tenant import Tenant # Needed for validation
import datetime

payments_bp = Blueprint("payments_bp", __name__)

# Add a rent payment for a specific tenant
@payments_bp.route("/tenant/<int:tenant_id>", methods=["POST"])
def add_payment(tenant_id):
    # Check if tenant exists
    tenant = Tenant.query.get_or_404(tenant_id)
    data = request.get_json()
    if not data or data.get("amount") is None:
        return jsonify({"error": "Missing required field: amount"}), 400

    try:
        payment_date = datetime.date.today()
        if data.get("payment_date"):
            payment_date = datetime.date.fromisoformat(data["payment_date"])

        new_payment = RentPayment(
            tenant_id=tenant_id,
            amount=float(data["amount"]),
            payment_date=payment_date,
            payment_method=data.get("payment_method"),
            notes=data.get("notes")
        )
        db.session.add(new_payment)
        db.session.commit()
        return jsonify(new_payment.to_dict()), 201
    except ValueError as e:
         return jsonify({"error": f"Invalid data format: {e}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500

# Get all payments for a specific tenant
@payments_bp.route("/tenant/<int:tenant_id>", methods=["GET"])
def get_payments_for_tenant(tenant_id):
    # Check if tenant exists
    tenant = Tenant.query.get_or_404(tenant_id)
    try:
        payments = RentPayment.query.filter_by(tenant_id=tenant_id).order_by(RentPayment.payment_date.desc()).all()
        return jsonify([payment.to_dict() for payment in payments]), 200
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

# Get a specific payment by ID
@payments_bp.route("/<int:payment_id>", methods=["GET"])
def get_payment(payment_id):
    try:
        payment = RentPayment.query.get_or_404(payment_id)
        return jsonify(payment.to_dict()), 200
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

# Update a specific payment
@payments_bp.route("/<int:payment_id>", methods=["PUT"])
def update_payment(payment_id):
    payment = RentPayment.query.get_or_404(payment_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        if "amount" in data: payment.amount = float(data["amount"])
        if "payment_date" in data:
            payment.payment_date = datetime.date.fromisoformat(data["payment_date"]) if data["payment_date"] else datetime.date.today()
        if "payment_method" in data: payment.payment_method = data["payment_method"]
        if "notes" in data: payment.notes = data["notes"]
        # tenant_id should generally not be changed, handle if necessary

        db.session.commit()
        return jsonify(payment.to_dict()), 200
    except ValueError as e:
         return jsonify({"error": f"Invalid data format: {e}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500

# Delete a specific payment
@payments_bp.route("/<int:payment_id>", methods=["DELETE"])
def delete_payment(payment_id):
    payment = RentPayment.query.get_or_404(payment_id)
    try:
        db.session.delete(payment)
        db.session.commit()
        return jsonify({"message": f"Payment {payment_id} deleted successfully."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500

