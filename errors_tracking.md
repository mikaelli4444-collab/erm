# 🐛 Project Error Log

## 📌 General Information:
- **Project Name: ProntoERP**  
- **Lasted update: 18/04/2026**  

---

# Error #1: SQLAlchemy: Cannot import Projects Model

**Date: 18/04/2026**  
**Module:** User, Projects  
**Type:** Configuration

## 🔍 Description
It’s an **ORM configuration error** where SQLAlchemy fails to resolve a model name used in a relationship.

In simple terms: you defined a relationship using `"Projects"`, but when SQLAlchemy tried to set up the models, it couldn’t find any class with that name loaded in memory. Because of that, it raises an `InvalidRequestError`, saying it cannot locate `"Projects"`.


## 🧠 Root Cause
The root cause is that the `Projects` model was **not imported (and therefore not loaded into memory)** before SQLAlchemy attempted to configure the relationships.

Because SQLAlchemy only knows about models that have been executed/imported, it could not resolve the string `"Projects"` during mapper initialization, leading to the error.

## 🧪 How to Reproduce
Exact steps:
1. delete `from projects.projects_model import Projects` in `main.py`

## 🛠 Applied Solution
The solution is to **ensure the `Projects` model is imported before any database operation is executed**.

In practice, this means importing it during application startup (for example, in `main.py` or a central models file), so SQLAlchemy registers it in memory before it tries to resolve relationships.


## 📈 Future Improvement
Import the model in another file and delete from main

## 📎 Relevant Code
...


# Error #2: Alembic: Target database is not up to date

**Date: 16/04/2026**  
**Module:** Alembic
**Type:** Configuration

---

## 🔍 Description
This error occurs when Alembic detects that the database schema version is behind the latest available migration.

In simple terms: Alembic expects the database to already have certain migrations applied, but the current state stored in the `alembic_version` table does not match the latest revision (head). Because of this mismatch, Alembic refuses to proceed with new operations and throws the error: “Target database is not up to date.”

## 🧠 Root Cause
The root cause is a desynchronization between migration files and the database state.

This typically happens when:
- Migration files are deleted or modified manually
- New migrations are created without applying previous ones
- The database was reset but Alembic history was not updated
- The `alembic_version` table contains a revision that does not match the current migration chain

As a result, Alembic detects inconsistency and blocks further actions.

## 🧪 How to Reproduce
Exact steps:
1. Create and apply a migration
2. Modify or delete a migration file in `versions/`
3. Attempt to generate or apply a new migration

Result: Alembic throws “Target database is not up to date.”

## 🛠 Applied Solution
The solution is to realign the database state with the migration history.

In development, this was solved by marking the database as up-to-date using:
- `alembic stamp head` → forces the database to match the latest revision without executing migrations

Alternatively, if migrations should be applied normally:
- `alembic upgrade head` → applies all pending migrations


## 📈 Future Improvement
- Avoid deleting or modifying migration files after they are created
- Always apply migrations before generating new ones
- Maintain a consistent migration history
- Use reset strategies (stamp or full rebuild) when the migration chain is broken

## 📎 Relevant Code
...


# Error #3: "POST /notification/notifications/join-request/accept?request_id=undefined HTTP/1.1" 422 Unprocessable Entity

**Date:** 23/04/2026  
**Module:** Notifications  
**Type:** Frontend / Data Consistency  

---

## 🔍 Description
This error occurs when the frontend sends a request to accept a company join request without a valid `request_id`.

Instead of sending a numeric identifier, the request is made with:

```request_id=undefined```

Since the backend expects `request_id` as an integer, FastAPI is unable to parse the value and returns a **422 Unprocessable Entity** response.

---

## 🧠 Root Cause
The root cause is a **data inconsistency between the backend and frontend**.

Specifically:
- Some notifications were created **without `join_request_id`**
- The frontend assumes that all `company_join_request` notifications include this field
- When rendering, `data.join_request_id` becomes `undefined`
- The frontend then sends this invalid value in the request

This mismatch leads to invalid API calls and the resulting 422 error.

---

## 🧪 How to Reproduce
Exact steps:
1. Create a notification of type `company_join_request` **without** `join_request_id`
2. Load notifications in the frontend
3. Click “Accept” on that notification
4. The request is sent as:

    /join-request/accept?request_id=undefined

Result: FastAPI returns **422 Unprocessable Entity**

---

## 🛠 Applied Solution
The issue was resolved by ensuring that every join request notification includes a valid `join_request_id`.

Fix applied in backend:
- Create the `CompanyJoinRequest` first
- Use `session.flush()` to generate the ID
- Inject `join_request_id` into the notification payload before saving

Example flow:
1. Create join request
2. Generate ID
3. Build message with `join_request_id`
4. Store notification

Additionally:
- Old invalid notifications were removed or ignored
- Frontend validation was added to prevent sending undefined values

---

## 📈 Future Improvement
- Enforce a strict schema per notification type
- Validate notification payloads before rendering
- Avoid relying on optional fields for critical actions
- Implement defensive checks in the frontend
- Consider centralizing notification creation logic

---

## 📎 Relevant Code
- Notification rendering (frontend)
- Join request creation endpoint
- Accept/reject request endpoints

---

## 🎯 Final Note
The issue was not just technical, but architectural:

> Notifications were allowed to exist without required data for critical actions.

Ensuring data consistency between database state and runtime events is essential to prevent 

# 🐛 Project Error Log

## 📌 General Information:
- **Project Name:** ERM System
- **Lasted update:** 14/05/2026

---

# Error #4: Mercado Pago Modal Not Opening

**Date:** 14/05/2026  
**Module:** Frontend / Mercado Pago SDK  
**Type:** JavaScript

## 🔍 Description
The Mercado Pago payment modal was not initializing correctly.
Clicking the "Choose Plan" button did nothing visually and the SDK iframe never loaded.

## 🧠 Root Cause
JavaScript execution was breaking before the SDK initialization due to
invalid references and logic outside the submit callback.

## 🧪 How to Reproduce
Exact steps:
1. Open plans page
2. Click "Choose Plan"
3. Modal fails to initialize

## 🛠 Applied Solution
Removed invalid variables and moved all payment form data generation
inside the Mercado Pago `onSubmit` callback.

## 📈 Future Improvement
Separate frontend SDK logic into a dedicated JavaScript file.

## 📎 Relevant Code

```javascript
onSubmit: event => {

    event.preventDefault();

    const formData = cardFormInstance.getCardFormData();

    document.getElementById("card_token_id").value = formData.token;

    document.getElementById("form-checkout").submit();
}
```


# Error #5: FastAPI Route Not Executing

**Date:** 14/05/2026  
**Module:** Payments Router  
**Type:** Backend / Debugging

## 🔍 Description
The endpoint `/payment/create_checkout` appeared to fail silently
and no debug prints were shown in the console.

Even though the frontend was sending the POST request correctly,
the backend logs never displayed the expected `print()` statements,
making it seem like the route was never being executed.

## 🧠 Root Cause
Multiple uvicorn processes were running simultaneously,
causing requests to hit a different process instance.

Because of that:
- one process was serving requests
- another process was showing logs
- debug output appeared inconsistent or completely missing

This created the illusion that FastAPI was ignoring the route.

## 🧪 How to Reproduce
Exact steps:
1. Start uvicorn with `--reload`
2. Accidentally launch another uvicorn instance
3. Trigger checkout request
4. Observe missing console logs
5. Receive unexpected behavior during debugging

## 🛠 Applied Solution
Closed conflicting uvicorn/python processes
and restarted the server with a single active instance.

After restarting:
- debug logs appeared correctly
- route execution became visible
- request flow debugging worked normally

## 📈 Future Improvement
Use:
- Docker
- a process manager
- or a dedicated development script

to avoid duplicated backend instances.

## 📎 Relevant Code

```bash
python -m uvicorn core.main:app --reload
```

# Error #6: Mercado Pago Card Token Service Not Found

**Date:** 14/05/2026
**Module:** Mercado Pago Subscription API
**Type:** API Integration

---

## 🔍 Description

Mercado Pago failed during recurring subscription creation
and returned the following error:

```
{
    "message":"Card token service not found",
    "status":404
}
```

The backend attempted to create a subscription using
a generated `card_token_id`, but Mercado Pago rejected
the token before processing the request.

---

## 🧠 Root Cause

The integration was mixing incompatible environments.

Specifically:
- the frontend generated the card token using TEST credentials
- the backend attempted to use different credentials/environment
- Mercado Pago could not locate the token internally

Since card tokens are environment-specific,
a TEST token cannot be used inside PROD requests
and vice versa.

---

## 🧪 How to Reproduce

Exact steps:

1. Generate a card token using TEST Public Key
2. Send subscription request using PROD Access Token
3. Create recurring subscription
4. Mercado Pago returns token service error

---

## 🛠 Applied Solution

Standardized all Mercado Pago credentials
to use the same environment consistently.

The following credentials were aligned:
- Public Key
- Access Token
- Subscription Plans
- Card Tokens

After synchronization:
- Mercado Pago recognized the token correctly
- requests advanced to the next validation layer

---

## 📈 Future Improvement

Create separate configuration files for:
- sandbox/testing
- staging
- production

to avoid mixing credentials accidentally.

Recommended:
- `.env.test`
- `.env.production`

---

## 📎 Relevant Code

MERCADO_PAGO_ACCESS_TOKEN=TEST-xxxxxxxx
PUBLIC_KEY=TEST-xxxxxxxx

---

## 📎 Relevant Console Output

``` bash
404
{"message":"Card token service not found","status":404}
```
---

## 📎 Important Observation

This error was actually a positive debugging milestone.

Before fixing it:
- the request was failing earlier
- the backend flow was incomplete

After reaching this error:
- token generation was confirmed working
- frontend SDK communication was confirmed
- Mercado Pago endpoint was being reached successfully

Meaning:
the integration pipeline itself was finally alive.

# Error #7: Mercado Pago Card Token Service Not Found

**Date:** 14/05/2026
**Module:** Mercado Pago Subscription API
**Type:** API Integration

---

## 🔍 Description

Mercado Pago failed during recurring subscription creation
and returned the following error:

```
{
    "message":"Card token service not found",
    "status":404
}
```

The backend attempted to create a subscription using
a generated `card_token_id`, but Mercado Pago rejected
the token before processing the request.

---

## 🧠 Root Cause

The integration was mixing incompatible environments.

Specifically:
- the frontend generated the card token using TEST credentials
- the backend attempted to use different credentials/environment
- Mercado Pago could not locate the token internally

Since card tokens are environment-specific,
a TEST token cannot be used inside PROD requests
and vice versa.

---

## 🧪 How to Reproduce

Exact steps:

1. Generate a card token using TEST Public Key
2. Send subscription request using PROD Access Token
3. Create recurring subscription
4. Mercado Pago returns token service error

---

## 🛠 Applied Solution

Standardized all Mercado Pago credentials
to use the same environment consistently.

The following credentials were aligned:
- Public Key
- Access Token
- Subscription Plans
- Card Tokens

After synchronization:
- Mercado Pago recognized the token correctly
- requests advanced to the next validation layer

---

## 📈 Future Improvement

Create separate configuration files for:
- sandbox/testing
- staging
- production

to avoid mixing credentials accidentally.

Recommended:
- `.env.test`
- `.env.production`

---

## 📎 Relevant Code

```
MERCADO_PAGO_ACCESS_TOKEN=TEST-xxxxxxxx
PUBLIC_KEY=TEST-xxxxxxxx
```

---

## 📎 Relevant Console Output
```
404
{"message":"Card token service not found","status":404}
```
---

## 📎 Important Observation

This error was actually a positive debugging milestone.

Before fixing it:
- the request was failing earlier
- the backend flow was incomplete

After reaching this error:
- token generation was confirmed working
- frontend SDK communication was confirmed
- Mercado Pago endpoint was being reached successfully

Meaning:
the integration pipeline itself was finally alive.


# Error #8: Mercado Pago Subscription Rejected Due To Insufficient Amount

Date: 14/05/2026
Module: Payments / Mercado Pago Subscription
Type: Payment Validation

## 🔍 Description

After fixing multiple Mercado Pago integration issues, the subscription request finally reached the credit card validation stage.

The API no longer returned internal server errors or malformed request errors.

Instead, Mercado Pago returned:

STATUS: 401

RESPONSE:
```
{
  "message":"CC_VAL_433 Credit card validation has failed",
  "code":"cc_rejected_insufficient_amount",
  "status":401
}
```

This means the subscription creation flow was technically working correctly, but the credit card itself could not authorize the recurring payment.

The error appeared during subscription creation using the `/preapproval` endpoint.

## 🧠 Root Cause

The problem was NOT related to:
- API credentials
- request structure
- missing payer data
- missing auto_recurring
- invalid token
- invalid CPF
- invalid payment method
- invalid issuer

The real root cause was:

The real card used for testing did not have enough available balance/credit limit to authorize the recurring payment.

Mercado Pago successfully validated:
- card token
- payer data
- CPF
- payment method
- issuer
- subscription structure

But rejected the authorization itself due to insufficient funds.

## 🧪 How to Reproduce

Exact steps:

1. Create a valid subscription request using:
   - card_token_id
   - payer_email
   - payer CPF
   - auto_recurring
   - payment_method_id
   - issuer_id

2. Use a real card with insufficient balance or limit

3. Send POST request to:
   https://api.mercadopago.com/preapproval

4. Mercado Pago returns:

{
  "message":"CC_VAL_433 Credit card validation has failed",
  "code":"cc_rejected_insufficient_amount",
  "status":401
}

## 🛠 Applied Solution

No code fix was required.

The integration itself was already working correctly.

The solution is to:
- test using a card with available balance/credit
OR
- use approved Mercado Pago test cards

This error actually confirmed that:
- the backend flow was functioning
- Mercado Pago accepted the request structure
- the payer data was valid
- the subscription request reached final authorization stage

## 📈 Future Improvement

- Add friendlier frontend error handling for payment rejection codes
- Translate Mercado Pago errors into readable UI messages
- Map common MP errors:
  - insufficient funds
  - invalid card
  - high risk
  - expired card
  - invalid security code
- Save failed payment attempts for debugging/admin panel

## 📎 Relevant Code
```
response = requests.post(
    url,
    json=data,
    headers=headers,
    timeout=15
)

print("STATUS:", response.status_code)
print("RESPONSE:", response.text)

if response.status_code not in [200, 201]:
    raise ValueError(
        f"Error creando suscripción: {response.text}"
    )
```