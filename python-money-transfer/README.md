# Temporal-MongoDB Money Transfer Demo - Python

This is a Python port of the original Java Temporal-MongoDB Money Transfer Demo. It demonstrates how to use Temporal to orchestrate a money transfer between bank accounts.

## Prerequisites

- Python 3.11 or higher
- Temporal service
- MongoDB instance
- Banking service (python-bank-services) running on port 8480

## Installation

Create and activate a virtual environment (recommended):

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Start the Temporal Service

The steps that follow require a Temporal Service running locally, so start that now by
running the command below:

```
temporal server start-dev --db-filename temporal-service.db
```

This starts the Temporal Service, with the Web UI listening on its default port (8233). 
If that's unavailable, use the `--ui-port` option to specify a different one. 

The `--db-filename` option specifies the path to the file that the Temporal Service 
will use to store Event History and other data. It will create this file if it does 
not exist. If this option is omitted, the Temporal Service does not persist this data 
to disk, so it will be lost if you restart the Temporal Service.

## How to run the application

1. Start the banking services, as described in the
   [README for the banking services](../python-bank-services/README.md).
   
2. Start the Temporal worker:
   ```
   python workers.py
   ```
   
3. Start the workflow, specifying the sender, recipient, and amount:
   ```
   python starter.py Maria David 100
   ```

## Scenarios for demonstration

1. **Happy Path**: 
   The banking services are running and the transfer completes successfully, 
   without interruption, on the first attempt. Provided that the services 
   are running and the accounts for Maria and David have been created, that
   is what should happen when you run the commands above.

2. **Automatic Retries**: 
   Stop the sender's bank by setting its status to "STOPPED" in the banking UI, 
   and repeat the transfer. You'll see that the Workflow Execution does not complete. 
   Open the Web UI and the "Pending Activities" section will show what's wrong. 
   It will also show you how many attempts have been made for this Activity 
   so far and how long it will be until the next one. Start the bank and 
   you should observe that, with the outage now resolved, the Workflow runs 
   to completion as if there was never an outage at all.

3. **Automatic Retries** (business-level failures):
   This is similar to the above scenario, but it doesn't have to be an outage 
   that triggers a retry. It will happen with business-level failures, too. 
   To see this, try initiating a transfer using a sender for which there is
   no account. The `withdraw` call will fail because that account doesn't 
   exist, but it will be retried. If you then created the account, then the 
   problem will be resolved and the Workflow will run to completion. It's also
   possible to customize the Retry Policy to specify a particular type of error 
   as non-retryable, as is the case for insufficient funds. In that case, the 
   Workflow will fail because our business logic demands that behavior.

4. **Durable Execution**: 
   Uncomment the `await asyncio.sleep(30)` line in the Workflow implementation 
   class (and then restart the Worker, if it's already running, so the change 
   takes effect). Re-run the Workflow as in the Happy Path scenario, but while 
   that 30-second sleep is active (i.e., after the `withdraw` Activity but before 
   the `deposit` Activity), kill the Worker. Open the Temporal Web UI and observe
   that the withdraw Activity already completed, but the deposit Activity has 
   not yet run, and that there is no progress (because the only Worker is down).
   When you restart the Worker, you'll see that the Workflow continues from where
   it left off.

5. **Human-in-the-Loop**:
   Any transfer exceeding $500 is automatically placed on hold. A manager can 
   release the hold by sending a Signal to the Workflow Execution, which can
   be done with the `temporal` CLI or the Temporal Web UI. For example:
   
   ```
   temporal workflow signal --workflow-id transfer-600-maria-to-david --name approve --input '"John"'
   ```