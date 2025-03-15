# **MongoDB Banking Application (Python)**

This is a Python port of the original Java MongoDB Banking Application. It provides a web-based interface for managing bank accounts and a REST API for performing banking operations.

## **Setup**

### **1. Prerequisites**

* Python 3.11 or higher
* MongoDB cluster
* Temporal CLI (for the money transfer application)

---

### **2. Environment Variables**

Set the MongoDB connection string as an environment variable.
This is likely to be `mongodb://127.0.0.1:27017` for a local MongoDB cluster.

```bash
export MONGO_CONNECTION_STRING="your_connection_string_here"
```

### **3. Installation**

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

---

## **Running the Application**

Start the server:

```bash
python main.py
```

The server will start at http://localhost:8480. You can access the web UI by opening this URL in your browser.

To run the server without the web UI (API only):

```bash
python main.py --no-web
```

---

## **API Endpoints**

### **Base URL**

All endpoints are available at `http://localhost:8480`.

### **Create Account**

Creates a new bank account.

**Endpoint:**

```http
GET /api/createBank?bankName={name}&initialBalance={balance}
```

**Example:**

```bash
curl -X GET "http://localhost:8480/api/createBank?bankName=Maria&initialBalance=1000"
```

**Response:**

```json
{
  "status": "SUCCESS",
  "message": "Bank created successfully"
}
```

---

### **Get Balance**

Retrieve the balance of a bank account.

**Endpoint:**

```http
GET /api/balance?bankName={name}
```

**Example:**

```bash
curl -X GET "http://localhost:8480/api/balance?bankName=Maria"
```

**Response:**

```json
{
  "status": "SUCCESS",
  "balance": 1000
}
```

---

### **Deposit**

Deposit money into a specific bank.

**Endpoint:**

```http
GET /api/deposit?bankName={name}&amount={amount}&idempotencyKey={key}
```

**Example:**

```bash
curl -X GET "http://localhost:8480/api/deposit?bankName=Maria&amount=500&idempotencyKey=key123"
```

**Response:**

```json
{
  "status": "SUCCESS",
  "transaction-id": "D123456789"
}
```

---

### **Withdraw**

Withdraw money from a specific bank.

**Endpoint:**

```http
GET /api/withdraw?bankName={name}&amount={amount}&idempotencyKey={key}
```

**Example:**

```bash
curl -X GET "http://localhost:8480/api/withdraw?bankName=Maria&amount=200&idempotencyKey=key456"
```

**Response:**

```json
{
  "status": "SUCCESS",
  "transaction-id": "W987654321"
}
```

---

### **Bank Status**

Get or set the status of a bank.

**Get Status:**

```http
GET /api/bankStatus?bankName={name}
```

**Set Status:**

```http
POST /api/bankStatus?bankName={name}&status={ACTIVE|STOPPED}
```

---

### **Get All Banks**

Get information about all banks.

**Endpoint:**

```http
GET /api/banks
```

**Response:**

```json
{
  "status": "SUCCESS",
  "banks": [
    {
      "name": "Maria",
      "balance": 1300,
      "status": "ACTIVE"
    },
    {
      "name": "David",
      "balance": 800,
      "status": "ACTIVE"
    }
  ]
}
```

---

## **Web UI**

The application provides a web-based user interface that allows you to:

1. View all bank accounts
2. Create new bank accounts
3. View the details of a bank account
4. Deposit and withdraw funds
5. Start and stop banks

Access the web UI at `http://localhost:8480` in your web browser.

---

## **Troubleshooting**

### **Environment Variable Not Set**

If the application cannot connect to MongoDB, ensure the `MONGO_CONNECTION_STRING` environment variable is set correctly.

### **Service Unavailable**

If the service is unreachable, ensure the server is running on `http://localhost:8480`.

### **MongoDB Issues**

Ensure the MongoDB instance is running and accessible from the application.