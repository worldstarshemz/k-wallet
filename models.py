"""Database models for Bank Wallet application"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    """User account model"""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(100),
        nullable=False
    )

    account = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    pin = db.Column(
        db.String(255),
        nullable=False
    )

    balance = db.Column(
        db.Float,
        default=1000.00
    )

    photo = db.Column(
        db.String(200),
        default="default.png"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def set_pin(self, pin):
        """Hash and set user PIN"""
        self.pin = generate_password_hash(pin)

    def check_pin(self, pin):
        """Verify PIN"""
        return check_password_hash(self.pin, pin)


class Transaction(db.Model):
    """Transaction record model"""
    __tablename__ = "transactions"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    sender = db.Column(
        db.String(20),
        nullable=False
    )

    receiver = db.Column(
        db.String(20),
        nullable=False
    )

    amount = db.Column(
        db.Float,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


class Admin(db.Model):
    """Admin user model"""
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def set_password(self, password):
        """Hash and set admin password"""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Verify admin password"""
        return check_password_hash(self.password, password)


# ==========================
# M-Pesa Models
# ==========================

class MpesaTransaction(db.Model):
    """Records STK Push requests and results"""
    __tablename__ = "mpesa_transactions"

    id = db.Column(db.Integer, primary_key=True)
    merchant_request_id = db.Column(db.String(100), nullable=True)
    checkout_request_id = db.Column(db.String(100), nullable=True, index=True)
    amount = db.Column(db.Float, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    result_code = db.Column(db.Integer, nullable=True)
    result_desc = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(30), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class MpesaWebhookLog(db.Model):
    """Raw webhook payloads from Daraja for auditing"""
    __tablename__ = "mpesa_webhook_logs"

    id = db.Column(db.Integer, primary_key=True)
    payload = db.Column(db.Text, nullable=True)
    headers = db.Column(db.Text, nullable=True)
    received_at = db.Column(db.DateTime, default=datetime.utcnow)
