from flask import Blueprint, jsonify, render_template, Response, abort
from src.models.database import db
from src.models.tenant import Tenant
from src.models.rent import RentPayment
from src.models.utility import UtilityBill, UtilityBillSplit
import datetime
import csv
import io

reports_bp = Blueprint("reports_bp", __name__, template_folder="../templates")

# --- Invoice Generation (HTML) --- 
@reports_bp.route("/invoice/tenant/<int:tenant_id>/<int:year>/<int:month>", methods=["GET"])
def generate_invoice(tenant_id, year, month):
    try:
        tenant = Tenant.query.get_or_404(tenant_id)
        
        # Validate month and year
        if not (1 <= month <= 12):
            abort(400, description="Invalid month specified.")
        
        # Calculate start and end of the month
        start_date = datetime.date(year, month, 1)
        next_month = month + 1
        next_year = year
        if next_month > 12:
            next_month = 1
            next_year += 1
        end_date = datetime.date(next_year, next_month, 1) - datetime.timedelta(days=1)

        # Get utility splits for the tenant within the billing period that overlaps the month
        # This logic might need refinement depending on how billing periods align with months
        # Simple approach: Get splits from bills ending within the month
        utility_splits = UtilityBillSplit.query\
            .join(UtilityBill)\
            .filter(UtilityBillSplit.tenant_id == tenant_id)\
            .filter(UtilityBill.billing_period_end >= start_date)\
            .filter(UtilityBill.billing_period_end <= end_date)\
            .all()

        total_utilities = sum(split.amount_owed for split in utility_splits)
        total_due = tenant.base_rent_amount + total_utilities

        # Get payments made by the tenant during this month
        payments_this_month = RentPayment.query\
            .filter(RentPayment.tenant_id == tenant_id)\
            .filter(RentPayment.payment_date >= start_date)\
            .filter(RentPayment.payment_date <= end_date)\
            .all()
        total_paid = sum(payment.amount for payment in payments_this_month)

        invoice_data = {
            "tenant": tenant,
            "month_year": start_date.strftime("%B %Y"),
            "invoice_date": datetime.date.today(),
            "base_rent": tenant.base_rent_amount,
            "utility_splits": utility_splits,
            "total_utilities": total_utilities,
            "total_due": total_due,
            "payments_made": payments_this_month,
            "total_paid": total_paid,
            "balance_forward": 0 # Placeholder - calculate previous balance if needed
        }

        # Render an HTML template
        return render_template("invoice.html", **invoice_data)

    except ValueError:
         abort(400, description="Invalid date format for year/month.")
    except Exception as e:
        print(f"Error generating invoice: {e}")
        abort(500, description="Internal server error generating invoice.")

# --- Receipt Generation (HTML) --- 
@reports_bp.route("/receipt/payment/<int:payment_id>", methods=["GET"])
def generate_receipt(payment_id):
    try:
        payment = RentPayment.query.get_or_404(payment_id)
        tenant = payment.tenant # Assumes relationship is loaded

        receipt_data = {
            "payment": payment,
            "tenant_name": tenant.name if tenant else "N/A",
            "receipt_date": datetime.date.today()
        }
        
        return render_template("receipt.html", **receipt_data)

    except Exception as e:
        print(f"Error generating receipt: {e}")
        abort(500, description="Internal server error generating receipt.")

# --- Data Export (CSV) --- 

# Export all payments for a specific tenant
@reports_bp.route("/export/payments/tenant/<int:tenant_id>", methods=["GET"])
def export_tenant_payments_csv(tenant_id):
    tenant = Tenant.query.get_or_404(tenant_id)
    payments = RentPayment.query.filter_by(tenant_id=tenant_id).order_by(RentPayment.payment_date.asc()).all()

    if not payments:
        return jsonify({"message": "No payments found for this tenant."}), 404

    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header row
    writer.writerow(["Payment ID", "Payment Date", "Amount", "Method", "Notes"])
    
    # Data rows
    for payment in payments:
        writer.writerow([
            payment.id,
            payment.payment_date.isoformat(),
            payment.amount,
            payment.payment_method or "",
            payment.notes or ""
        ])
    
    output.seek(0)
    
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=payments_{tenant.name.replace(	' 	', 	'_'	)}_{tenant_id}.csv"}
    )

# Export all utility bills (optional: add filters for date range, category)
@reports_bp.route("/export/bills", methods=["GET"])
def export_utility_bills_csv():
    bills = UtilityBill.query.order_by(UtilityBill.billing_period_end.asc()).all()

    if not bills:
        return jsonify({"message": "No utility bills found."}), 404

    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header row
    writer.writerow(["Bill ID", "Category", "Billing Start", "Billing End", "Bill Date", "Total Amount", "Usage Data", "Notes"])
    
    # Data rows
    for bill in bills:
        writer.writerow([
            bill.id,
            bill.category.name if bill.category else "",
            bill.billing_period_start.isoformat(),
            bill.billing_period_end.isoformat(),
            bill.bill_date.isoformat() if bill.bill_date else "",
            bill.total_amount,
            bill.usage_data or "",
            bill.notes or ""
        ])
    
    output.seek(0)
    
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=utility_bills.csv"}
    )

