import datetime
from src.models.database import db

# Model for Utility Categories (e.g., Internet, Water, Gas)
class UtilityCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Relationship
    bills = db.relationship("UtilityBill", back_populates="category", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<UtilityCategory {self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description
        }

# Model for individual Utility Bills
class UtilityBill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("utility_category.id"), nullable=False)
    billing_period_start = db.Column(db.Date, nullable=False)
    billing_period_end = db.Column(db.Date, nullable=False)
    bill_date = db.Column(db.Date, nullable=True, default=datetime.date.today)
    total_amount = db.Column(db.Float, nullable=False)
    usage_data = db.Column(db.Text, nullable=True) # Store usage details, maybe JSON string or simple text
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    # Path to the uploaded bill file (optional)
    file_path = db.Column(db.String(255), nullable=True)

    # Relationships
    category = db.relationship("UtilityCategory", back_populates="bills")
    splits = db.relationship("UtilityBillSplit", back_populates="bill", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<UtilityBill {self.id} for Category {self.category_id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else None,
            "billing_period_start": self.billing_period_start.isoformat(),
            "billing_period_end": self.billing_period_end.isoformat(),
            "bill_date": self.bill_date.isoformat() if self.bill_date else None,
            "total_amount": self.total_amount,
            "usage_data": self.usage_data,
            "notes": self.notes,
            "file_path": self.file_path,
            "created_at": self.created_at.isoformat()
        }

# Model for splitting a utility bill among tenants
class UtilityBillSplit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey("utility_bill.id"), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenant.id"), nullable=False)
    amount_owed = db.Column(db.Float, nullable=False)
    is_paid = db.Column(db.Boolean, default=False, nullable=False)
    paid_date = db.Column(db.Date, nullable=True)

    # Relationships
    bill = db.relationship("UtilityBill", back_populates="splits")
    tenant = db.relationship("Tenant", back_populates="utility_splits")

    def __repr__(self):
        return f"<UtilityBillSplit {self.id} for Bill {self.bill_id}, Tenant {self.tenant_id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "bill_id": self.bill_id,
            "tenant_id": self.tenant_id,
            "tenant_name": self.tenant.name if self.tenant else None,
            "amount_owed": self.amount_owed,
            "is_paid": self.is_paid,
            "paid_date": self.paid_date.isoformat() if self.paid_date else None
        }

