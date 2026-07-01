import os
import time
import base64
import requests
from datetime import datetime

from mpesa.client import MpesaToken
from models import db, MpesaTransaction
from config import Config

MPESA_ENV = os.getenv("MPESA_ENV", "sandbox")
SHORTCODE = os.getenv("MPESA_SHORTCODE")
PASSKEY = os.getenv("MPESA_PASSKEY")

STK_PUSH_URL = (
    "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    if MPESA_ENV == "sandbox"
    else "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
)


def _timestamp():
    return datetime.utcnow().strftime("%Y%m%d%H%M%S")


def _password(shortcode, passkey, timestamp):
    raw = f"{shortcode}{passkey}{timestamp}"
    return base64.b64encode(raw.encode()).decode()


def stk_push(amount, phone, account_ref, callback_url):
    """Initiate an STK Push via Daraja and persist the request.

    Returns a dict with keys: success (bool), message, data
    """
    if not SHORTCODE or not PASSKEY:
        return {"success": False, "message": "MPESA_SHORTCODE and MPESA_PASSKEY not configured"}

    # create a DB record first
    tx = MpesaTransaction(
        amount=float(amount),
        phone_number=str(phone),
        status="pending",
        created_at=datetime.utcnow()
    )

    db.session.add(tx)
    db.session.commit()

    timestamp = _timestamp()
    password = _password(SHORTCODE, PASSKEY, timestamp)

    token = MpesaToken.get_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "BusinessShortCode": SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone,
        "PartyB": SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": callback_url,
        "AccountReference": account_ref,
        "TransactionDesc": f"Payment for {account_ref}"
    }

    r = requests.post(STK_PUSH_URL, json=payload, headers=headers, timeout=15)

    try:
        r.raise_for_status()
        data = r.json()
    except Exception as exc:
        # update tx as failed
        tx.status = "failed"
        tx.result_desc = str(exc)
        db.session.commit()
        return {"success": False, "message": "STK Push request failed", "data": r.text}

    # typical response contains MerchantRequestID and CheckoutRequestID
    tx.merchant_request_id = data.get("MerchantRequestID")
    tx.checkout_request_id = data.get("CheckoutRequestID")
    db.session.commit()

    return {"success": True, "message": "STK Push initiated", "data": data}
