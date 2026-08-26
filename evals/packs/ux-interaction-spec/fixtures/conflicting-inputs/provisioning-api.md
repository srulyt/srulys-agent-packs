# Entitlement provisioning API — integration notes

The access-governance service does not grant warehouse access itself. On
approval it calls the entitlement service, which does the actual grant.

## The call

`POST /v1/grants`

Request body: `{ principal, resource, level, expires_at }`

Response: `202 Accepted` with `{ grant_id, status: "provisioning" }`.

**This is asynchronous.** The grant is not live when the call returns.

## Provisioning lifecycle

| `status` | Meaning | Typical duration |
|---|---|---|
| `provisioning` | Accepted, work queued | — |
| `active` | Grant is live; the principal can query the resource | 30 seconds to 4 minutes, p99 ~11 minutes |
| `failed` | Provisioning failed; the principal has no access | terminal until retried |
| `partial` | Some backing stores granted, others not | requires manual repair |

Poll `GET /v1/grants/{grant_id}` or subscribe to the `grant.status_changed`
webhook.

## Failure modes we actually see

- **Warehouse maintenance window** — grants queue and go `active` late,
  sometimes hours later. No error is raised.
- **Principal not yet synced from the identity provider** — returns `failed`
  with `reason: unknown_principal`. Common for employees in their first 48
  hours.
- **Resource renamed between approval and provisioning** — returns `failed`
  with `reason: resource_not_found`.
- **Partial grant** — the read grant lands but the write grant does not. The
  principal has an access level lower than what was approved, and nothing
  tells them.

## Revocation

`DELETE /v1/grants/{grant_id}` is also asynchronous and returns `202`. Between
the call and the grant leaving `active`, the principal still has access.
