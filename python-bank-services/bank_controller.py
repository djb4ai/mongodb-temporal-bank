import logging
import os
import json
from flask import Flask, request, jsonify, render_template, redirect, url_for
from werkzeug.exceptions import BadRequest

from bank_manager import BankManager
from bank import InsufficientFundsException
from json_util import serialize_to_json
from config.mongodb_config import MongodbConfig

logger = logging.getLogger(__name__)

class BankController:
    """
    Flask controller for bank API endpoints.
    """
    
    def __init__(self, bank_manager: BankManager, port: int = 8480):
        """
        Initialize the controller.
        
        Args:
            bank_manager: The bank manager to use
            port: The port to run the server on
        """
        self.bank_manager = bank_manager
        self.port = port
        self.app = Flask(__name__, 
                         template_folder='templates',
                         static_folder='static')
                         
        # Configure routes
        self._configure_routes()
        
        # Configure error handlers
        self._configure_error_handlers()
    
    def _configure_routes(self):
        """Configure the Flask application routes."""
        # API routes
        self.app.add_url_rule('/api/createBank', 'create_bank', self.create_bank, methods=['GET'])
        self.app.add_url_rule('/api/balance', 'get_balance', self.get_balance, methods=['GET'])
        self.app.add_url_rule('/api/deposit', 'deposit', self.deposit, methods=['GET'])
        self.app.add_url_rule('/api/withdraw', 'withdraw', self.withdraw, methods=['GET'])
        self.app.add_url_rule('/api/bankStatus', 'bank_status', self.bank_status, methods=['GET', 'POST'])
        self.app.add_url_rule('/api/banks', 'get_banks', self.get_banks, methods=['GET'])
        
        # Web UI routes
        self.app.add_url_rule('/', 'home', self.home)
        self.app.add_url_rule('/banks', 'banks_list', self.banks_list)
        self.app.add_url_rule('/banks/<bank_name>', 'bank_detail', self.bank_detail)
    
    def _configure_error_handlers(self):
        """Configure Flask error handlers."""
        @self.app.errorhandler(InsufficientFundsException)
        def handle_insufficient_funds(error):
            return jsonify({
                "status": "ERROR",
                "message": str(error)
            }), 400
            
        @self.app.errorhandler(ValueError)
        def handle_value_error(error):
            return jsonify({
                "status": "ERROR",
                "message": str(error)
            }), 400
            
        @self.app.errorhandler(404)
        def handle_not_found(error):
            return jsonify({
                "status": "ERROR",
                "message": "Resource not found"
            }), 404
    
    def start(self):
        """Start the Flask application."""
        self.app.run(host='0.0.0.0', port=self.port)
    
    # ===== API Endpoints =====
    
    def create_bank(self):
        """
        Create a new bank account.
        
        URL: /api/createBank?bankName={name}&initialBalance={balance}
        """
        bank_name = request.args.get('bankName')
        initial_balance = request.args.get('initialBalance', 0)
        
        if not bank_name:
            return jsonify({
                "status": "ERROR",
                "message": "Bank name is required"
            }), 400
        
        try:
            initial_balance = int(initial_balance)
        except ValueError:
            return jsonify({
                "status": "ERROR",
                "message": "Initial balance must be a number"
            }), 400
        
        bank = self.bank_manager.create_bank(bank_name, initial_balance)
        
        return jsonify({
            "status": "SUCCESS",
            "message": "Bank created successfully"
        })
    
    def get_balance(self):
        """
        Get the balance of a bank account.
        
        URL: /api/balance?bankName={name}
        """
        bank_name = request.args.get('bankName')
        
        if not bank_name:
            return jsonify({
                "status": "ERROR",
                "message": "Bank name is required"
            }), 400
        
        bank = self.bank_manager.get_bank(bank_name)
        
        if not bank:
            return jsonify({
                "status": "ERROR",
                "message": f"No such bank: {bank_name}"
            }), 404
        
        status = self.bank_manager.get_bank_status(bank_name)
        if status == "STOPPED":
            return jsonify({
                "status": "ERROR",
                "message": f"Bank {bank_name} is currently stopped"
            }), 400
            
        balance = bank.get_balance()
        
        return jsonify({
            "status": "SUCCESS",
            "balance": balance
        })
    
    def deposit(self):
        """
        Deposit money into a bank account.
        
        URL: /api/deposit?bankName={name}&amount={amount}&idempotencyKey={key}
        """
        bank_name = request.args.get('bankName')
        amount = request.args.get('amount')
        idempotency_key = request.args.get('idempotencyKey')
        
        if not bank_name or not amount or not idempotency_key:
            return jsonify({
                "status": "ERROR",
                "message": "Bank name, amount, and idempotency key are required"
            }), 400
        
        try:
            amount = int(amount)
        except ValueError:
            return jsonify({
                "status": "ERROR",
                "message": "Amount must be a number"
            }), 400
        
        bank = self.bank_manager.get_bank(bank_name)
        
        if not bank:
            return jsonify({
                "status": "ERROR",
                "message": f"No such bank: {bank_name}"
            }), 404
        
        status = self.bank_manager.get_bank_status(bank_name)
        if status == "STOPPED":
            return jsonify({
                "status": "ERROR",
                "message": f"Bank {bank_name} is currently stopped"
            }), 400
            
        try:
            tx_id = bank.deposit(amount, idempotency_key)
            
            return jsonify({
                "status": "SUCCESS",
                "transaction-id": tx_id
            })
        except ValueError as e:
            return jsonify({
                "status": "ERROR",
                "message": str(e)
            }), 400
    
    def withdraw(self):
        """
        Withdraw money from a bank account.
        
        URL: /api/withdraw?bankName={name}&amount={amount}&idempotencyKey={key}
        """
        bank_name = request.args.get('bankName')
        amount = request.args.get('amount')
        idempotency_key = request.args.get('idempotencyKey')
        
        if not bank_name or not amount or not idempotency_key:
            return jsonify({
                "status": "ERROR",
                "message": "Bank name, amount, and idempotency key are required"
            }), 400
        
        try:
            amount = int(amount)
        except ValueError:
            return jsonify({
                "status": "ERROR",
                "message": "Amount must be a number"
            }), 400
        
        bank = self.bank_manager.get_bank(bank_name)
        
        if not bank:
            return jsonify({
                "status": "ERROR",
                "message": f"No such bank: {bank_name}"
            }), 404
        
        status = self.bank_manager.get_bank_status(bank_name)
        if status == "STOPPED":
            return jsonify({
                "status": "ERROR",
                "message": f"Bank {bank_name} is currently stopped"
            }), 400
            
        try:
            tx_id = bank.withdraw(amount, idempotency_key)
            
            return jsonify({
                "status": "SUCCESS",
                "transaction-id": tx_id
            })
        except (ValueError, InsufficientFundsException) as e:
            return jsonify({
                "status": "ERROR",
                "message": str(e)
            }), 400
    
    def bank_status(self):
        """
        Get or set the status of a bank.
        
        GET: /api/bankStatus?bankName={name}
        POST: /api/bankStatus?bankName={name}&status={status}
        """
        bank_name = request.args.get('bankName')
        
        if not bank_name:
            return jsonify({
                "status": "ERROR",
                "message": "Bank name is required"
            }), 400
        
        if request.method == 'POST':
            new_status = request.args.get('status')
            
            if not new_status:
                return jsonify({
                    "status": "ERROR",
                    "message": "Status is required"
                }), 400
                
            if new_status not in ["ACTIVE", "STOPPED"]:
                return jsonify({
                    "status": "ERROR",
                    "message": "Status must be either ACTIVE or STOPPED"
                }), 400
                
            success = self.bank_manager.set_bank_status(bank_name, new_status)
            
            if not success:
                return jsonify({
                    "status": "ERROR",
                    "message": f"No such bank: {bank_name}"
                }), 404
                
            return jsonify({
                "status": "SUCCESS",
                "message": f"Bank status updated to {new_status}"
            })
        else:
            # GET request
            status = self.bank_manager.get_bank_status(bank_name)
            
            if status is None:
                return jsonify({
                    "status": "ERROR",
                    "message": f"No such bank: {bank_name}"
                }), 404
                
            return jsonify({
                "status": "SUCCESS",
                "bankStatus": status
            })
    
    def get_banks(self):
        """
        Get all banks.
        
        URL: /api/banks
        """
        banks = self.bank_manager.get_all_banks()
        bank_list = []
        
        for bank in banks:
            status = self.bank_manager.get_bank_status(bank.get_name())
            bank_list.append({
                "name": bank.get_name(),
                "balance": bank.get_balance(),
                "status": status
            })
        
        return jsonify({
            "status": "SUCCESS",
            "banks": bank_list
        })
    
    # ===== Web UI Routes =====
    
    def home(self):
        """Render the home page."""
        return redirect(url_for('banks_list'))
    
    def banks_list(self):
        """Render the banks list page."""
        banks = self.bank_manager.get_all_banks()
        bank_list = []
        
        for bank in banks:
            status = self.bank_manager.get_bank_status(bank.get_name())
            bank_list.append({
                "name": bank.get_name(),
                "balance": bank.get_balance(),
                "status": status
            })
        
        return render_template('banks_list.html', banks=bank_list)
    
    def bank_detail(self, bank_name):
        """
        Render the bank detail page.
        
        Args:
            bank_name: The name of the bank
        """
        bank = self.bank_manager.get_bank(bank_name)
        
        if not bank:
            return render_template('error.html', message=f"No such bank: {bank_name}")
        
        status = self.bank_manager.get_bank_status(bank_name)
        
        return render_template('bank_detail.html', 
                               name=bank.get_name(),
                               balance=bank.get_balance(), 
                               status=status)