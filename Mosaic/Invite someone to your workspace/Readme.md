# Mosaic — mosaic-002 — Invite someone to your workspace.

## Challenge Information

- **Challenge:** Mosaic
- **Platform:** BugForge
- **Category:** Web Application Security
- **Difficulty:** As assigned by the platform
- **Hint:** Invite someone to your workspace.
- **Vulnerability:** Broken Access Control / Privilege Escalation
- **Affected Endpoint:** `POST /api/invites/accept`

## Objective

Investigate the workspace invitation functionality in Mosaic, identify an authorization weakness, and determine whether an invited user can obtain privileges beyond the role assigned by the workspace owner.

## Tools Used

- Web browser
- Firefox Developer Tools
- Network tab for inspecting HTTP requests and responses
- Two separate browser sessions to simulate different users

## Step 1: Create the First Workspace

1. Open the Mosaic challenge application.
2. Create a new workspace.
3. Open the default board created by the application.
4. Open Developer Tools using `F12`.
5. Navigate to the **Network** tab and select **Fetch/XHR**.
6. Observe the API requests generated while interacting with the board.

The application retrieves board information through:

```http
GET /api/boards
```

The response includes board metadata such as:

- Board ID
- Workspace ID
- Owner ID
- Board visibility
- Current user's role
- Board contents

Record the board ID and workspace ID for reference during the investigation.

## Step 2: Inspect the Sharing Functionality

Click the board's **Share** button and inspect the following request:

```http
GET /api/boards/<board-id>/sharing
```

The initial response was:

```json
{
  "members": [],
  "invites": [],
  "share": null,
  "people": []
}
```

The sharing interface provided several options:

- Allow everyone in the workspace to edit.
- Restrict access to people explicitly added or invited.
- Invite someone by email with an assigned role.
- Create an invitation link that permits viewing the canvas for seven days.

The email invitation feature was selected for further testing.

## Step 3: Create an Invitation

Enter an email address for a second test account and assign the role `editor`.

The application sends a request to:

```http
POST /api/boards/<board-id>/invites
Content-Type: application/json
```

Example request body:

```json
{
  "email": "testuser@mail.com",
  "role": "editor"
}
```

The server responds with HTTP status `201 Created` and returns an invitation token:

```json
{
  "token": "<invitation-token>"
}
```

Keep the token available for the subsequent invitation acceptance test. Do not publish real session cookies, CSRF tokens, or live invitation tokens in the report.

## Step 4: Accept the Invitation as the Second User

1. Open a separate private browser window.
2. Create or access a second test account and workspace.
3. Open the invitation link received from the first account.
4. Inspect the resulting requests in the Network tab.
5. Locate the invitation acceptance request.

The application sends:

```http
POST /api/invites/accept
Content-Type: application/json
```

The original request body contains:

```json
{
  "token": "<invitation-token>",
  "role": "editor"
}
```

The server initially accepts the invitation with the assigned editor role.

## Step 5: Test for Privilege Escalation

The acceptance request includes a client-supplied `role` parameter. This parameter was modified in the authorized challenge environment to test whether the server independently validates the role stored in the invitation.

Change the request body to:

```json
{
  "token": "<invitation-token>",
  "role": "owner"
}
```

Resend the request using the browser's available request-editing or replay functionality.

**Observation:** The server accepted the modified request and returned a successful response containing the board ID and challenge flag.

This demonstrated that the server trusted the role supplied during invitation acceptance instead of enforcing the role assigned when the invitation was created.

## Step 6: Capture the Flag

The successful response contained:

```json
{
  "id": "<board-id>",
  "flag": "<challenge-flag>"
}
```

The flag returned during this challenge was:

```text
bug{hNf8rZOnOUfaGqJaakZvsmMgN8ny4i3F}
```

## Vulnerability Analysis

### Root Cause

The server failed to enforce the invitation's assigned role during acceptance. Instead, it allowed the invitee to submit a higher-privilege role in the request body.

The invitation token should identify an invitation record containing the authorized workspace, invited user or email, assigned role, expiration, and acceptance status. The server should use that record as the source of truth.

### Security Impact

An attacker who can accept an invitation may be able to obtain privileges beyond those authorized by the workspace owner. Depending on the application's permission model, this could enable unauthorized workspace administration, access management, or changes to shared resources.

### Classification

- **OWASP Top 10 (2021):** A01 — Broken Access Control
- **CWE-269:** Improper Privilege Management
- **Related weakness:** CWE-863 — Incorrect Authorization

## Recommended Remediation

1. Retrieve the invitation record using the invitation token.
2. Assign the role stored in the server-side invitation record.
3. Ignore or reject any client-supplied role that attempts to override the invitation.
4. Verify that the authenticated user is eligible to accept the invitation.
5. Validate invitation expiration, intended recipient, and single-use status.
6. Perform invitation acceptance and membership creation transactionally.
7. Add tests confirming that an editor invitation cannot be converted into an owner invitation by modifying the request body.

## Conclusion

The Mosaic challenge demonstrated a privilege escalation vulnerability in the invitation acceptance workflow.

By inspecting the HTTP requests, comparing the intended invitation role with the acceptance request, and testing a modified role parameter, it was possible to identify insufficient server-side authorization checks and retrieve the challenge flag.

**Key takeaway:** Never trust client-supplied privilege values. The server must enforce authorization using trusted, server-side records.

## Disclaimer

All testing described in this document was performed within the authorized BugForge challenge environment for educational purposes.