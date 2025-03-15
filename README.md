# MongoDB-Temporal Money Transfer Application (Python Version)

This repository contains Python ports of the original Java applications for demonstrating money transfers using MongoDB and Temporal. The project consists of two main components:

1. **Python Bank Services**: A Flask-based web application that provides banking services like deposits, withdrawals, and balance checks. It uses MongoDB for persistence and offers both a REST API and a web-based UI.

2. **Python Money Transfer**: A Temporal workflow application that orchestrates money transfers between accounts using the banking services. It demonstrates Temporal's capabilities for reliable workflows, retries, and durability.

## Prerequisites

- Python 3.11 or higher
- MongoDB cluster
- Temporal server
- (Optional) Docker for containerization

## Quick Start

### Setting up the Bank Services

1. Navigate to the python-bank-services directory:
   ```
   cd python-bank-services
   ```

2. Set up your Python environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set the MongoDB connection string environment variable:
   ```
   export MONGO_CONNECTION_STRING="mongodb://localhost:27017"
   ```

4. Start the banking application:
   ```
   python main.py
   ```
   
5. Access the web UI at http://localhost:8480 to create and manage bank accounts

### Setting up the Money Transfer Application

1. In a separate terminal, navigate to the python-money-transfer directory:
   ```
   cd python-money-transfer
   ```

2. Set up your Python environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Start the Temporal server (if not already running):
   ```
   temporal server start-dev --db-filename temporal-service.db
   ```

4. Start the Temporal worker:
   ```
   python workers.py
   ```

5. In another terminal, initiate a money transfer:
   ```
   python starter.py Maria David 100
   ```

## Project Structure

```
mongodb-java-money-transfer/
├── python-bank-services/         # Bank Services Application
│   ├── config/                   # Configuration modules
│   ├── repository/               # MongoDB repository
│   ├── static/                   # Static web assets
│   ├── templates/                # HTML templates
│   ├── bank.py                   # Bank model
│   ├── bank_controller.py        # API endpoints
│   ├── bank_manager.py           # Banking business logic
│   ├── json_util.py              # JSON utilities
│   ├── main.py                   # Application entry point
│   └── requirements.txt          # Dependencies
└── python-money-transfer/        # Money Transfer Application
    ├── activities/               # Temporal activities
    ├── bankapi/                  # Banking API client
    ├── models/                   # Data models
    ├── workflows/                # Temporal workflows
    ├── exceptions.py             # Custom exceptions
    ├── starter.py                # Workflow starter
    ├── workers.py                # Temporal worker
    └── requirements.txt          # Dependencies
```

## Key Features

- **Thread-safe banking operations**: Uses Python's threading.Lock for concurrent access
- **Idempotent operations**: Prevents duplicate transactions using idempotency keys
- **Web-based UI**: Modern UI for managing bank accounts
- **REST API**: Consistent API endpoints for banking operations
- **Durable workflows**: Temporal ensures workflow completion despite failures
- **Automatic retries**: Failed operations are retried with configurable policies
- **MongoDB persistence**: All account data and transactions are stored in MongoDB

## Demonstration Scenarios

Refer to the README files in each project directory for details on demonstration scenarios:

- [Python Bank Services README](python-bank-services/README.md)
- [Python Money Transfer README](python-money-transfer/README.md)

## Differences from the Java Version

- Uses Flask for web services instead of Javalin
- Implements a web-based UI instead of a Swing GUI
- Uses Python's threading.Lock for thread safety instead of Java synchronization
- Uses Python's asyncio for asynchronous operations in the Temporal workflow
- Uses the Temporal Python SDK instead of the Java SDK

## License

This project is licensed under the same license as the original Java project.