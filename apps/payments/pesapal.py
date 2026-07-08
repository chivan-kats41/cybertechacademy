"""
CyberTech Academy - Pesapal Payment Integration
"""
import requests
from django.conf import settings


def get_pesapal_token():
    url = f"{settings.PESAPAL_BASE_URL}/api/Auth/RequestToken"
    payload = {
        "consumer_key":    settings.PESAPAL_CONSUMER_KEY,
        "consumer_secret": settings.PESAPAL_CONSUMER_SECRET,
    }
    resp = requests.post(url, json=payload, headers={"Accept": "application/json"})
    data = resp.json()
    return data.get("token")


def register_ipn(token, callback_url):
    url = f"{settings.PESAPAL_BASE_URL}/api/URLSetup/RegisterIPN"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type":  "application/json",
    }
    payload = {
        "url":          callback_url,
        "ipn_notification_type": "GET",
    }
    resp = requests.post(url, json=payload, headers=headers)
    return resp.json().get("ipn_id")


def submit_order(token, ipn_id, order_data):
    url = f"{settings.PESAPAL_BASE_URL}/api/Transactions/SubmitOrderRequest"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type":  "application/json",
    }
    payload = {
        "id":               order_data["reference"],
        "currency":         "UGX",
        "amount":           float(order_data["amount"]),
        "description":      order_data["description"],
        "callback_url":     order_data["callback_url"],
        "notification_id":  ipn_id,
        "billing_address": {
            "email_address": order_data["email"],
            "first_name":    order_data["first_name"],
            "last_name":     order_data["last_name"],
            "phone_number":  order_data.get("phone", ""),
            "country_code":  "UG",
        }
    }
    resp = requests.post(url, json=payload, headers=headers)
    data = resp.json()
    return data.get("redirect_url"), data.get("order_tracking_id")


def verify_transaction(token, order_tracking_id):
    url = f"{settings.PESAPAL_BASE_URL}/api/Transactions/GetTransactionStatus"
    headers = {"Authorization": f"Bearer {token}"}
    params  = {"orderTrackingId": order_tracking_id}
    resp = requests.get(url, headers=headers, params=params)
    return resp.json()
