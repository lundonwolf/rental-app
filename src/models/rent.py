import datetime
from src.models.database import db

class RentPayment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenant.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, nullable=False, default=datetime.date.today)
    payment_method = db.Column(db.String(50), nullable=True) # e.g., Bank Transfer, Cash, Check
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Relationships
    tenant = db.relationship("Tenant", back_populates="payments")

    def __repr__(self):
        return f"<RentPayment {self.id} for Tenant {self.tenant_id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "amount": self.amount,
            "payment_date": self.payment_date.isoformat(),
            "payment_method": self.payment_method,
            "notes": self.notes,
            "created_at": self.created_at.isoformat()
        }

