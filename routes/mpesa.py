import os
import json
from flask import Blueprint, request, jsonify
from models import db, MpesaWebhookLog, MpesaTransaction
from mpesa.actions import stk_push

mpesa_bp = Blueprint("mpesa", __name__)


@mpesa_bp.route("/mpesa/stk-push", methods=["POST"])
def mpesa_stk_push():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    amount = data.get("amount")
    phone = data.get("phone")
    account = data.get("account")

    if not amount or not phone or not account:
        return jsonify({"error": "Fields 'amount', 'phone' and 'account' are required"}), 400

    # Build callback URL from environment or request root
    callback_base = os.getenv("WEBHOOK_BASE_URL") or request.url_root.rstrip("/")
    callback_url = f"{callback_base}/mpesa/callback"

    result = stk_push(amount, phone, account, callback_url)

    if result.get("success"):
        return jsonify({"ok": True, "message": result.get("message"), "data": result.get("data")}), 200

    return jsonify({"ok": False, "message": result.get("message"), "data": result.get("data")}), 500


@mpesa_bp.route("/mpesa/callback", methods=["POST"])
def mpesa_callback():
    # Store raw payload and headers for auditing
    try:
        payload = request.get_json(silent=True)
    except Exception:
        payload = None

    headers = dict(request.headers)

    log = MpesaWebhookLog(
        payload=json.dumps(payload) if payload is not None else None,
        headers=json.dumps(headers)
    )

    db.session.add(log)
    db.session.commit()

    # Attempt to update corresponding MpesaTransaction (idempotent)
    try:
        body = payload or {}
        stk = body.get("Body", {}).get("stkCallback") if isinstance(body, dict) else None
        if stk:
            checkout_id = stk.get("CheckoutRequestID") or stk.get("CheckoutRequestId")
            result_code = stk.get("ResultCode")
            result_desc = stk.get("ResultDesc")

            if checkout_id:
                tx = MpesaTransaction.query.filter_by(checkout_request_id=checkout_id).first()
                if tx:
                    tx.result_code = int(result_code) if result_code is not None else None
                    tx.result_desc = result_desc
                    tx.status = "success" if int(result_code) == 0 else "failed"
                    db.session.commit()
    except Exception:
        # swallow errors but keep audit log
        pass

    # Respond 200 OK to acknowledge receipt
    return jsonify({"ResultCode": 0, "ResultDesc": "Accepted"}), 200
