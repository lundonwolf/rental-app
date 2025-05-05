import datetime
from src.models.database import db

class Tenant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    move_in_date = db.Column(db.Date, nullable=True)
    base_rent_amount = db.Column(db.Float, nullable=False, default=0.0)
    notes = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Relationships
    payments = db.relationship("RentPayment", back_populates="tenant", lazy=True, cascade="all, delete-orphan")
    utility_splits = db.relationship("UtilityBillSplit", back_populates="tenant", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Tenant {self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "move_in_date": self.move_in_date.isoformat() if self.move_in_date else None,
            "base_rent_amount": self.base_rent_amount,
            "notes": self.notes,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat()
        }

