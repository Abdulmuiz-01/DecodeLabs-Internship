# ============================================================
#  DECODE LABS - PROJECT 3: ERC-20 Token Wallet & Value Transfer
#  Author: Abdulmuiz Najeemdeen
#  Language: Python 3
# ============================================================

# We need two built-in Python libraries:
# - decimal: gives us double-precision math (no rounding errors with large numbers)
# - re: lets us validate wallet addresses using regex patterns
import re
from decimal import Decimal, InvalidOperation

# ============================================================
# WHAT IS ERC-20?
# ERC-20 is a standard for tokens on the Ethereum blockchain.
# Think of it like a rulebook - any token that follows it
# can work with any wallet, exchange, or app automatically.
# The two most important functions are:
#   - balanceOf(address): "How much do you have?"
#   - transfer(to, amount): "Send some to someone else."
# ============================================================


# ============================================================
# PART 1: THE ERC20TOKEN CLASS
# This simulates a real token on the blockchain.
# It has a name, a symbol, a total supply, and tracks
# every wallet's balance in a dictionary (like a ledger).
# ============================================================

class ERC20Token:
    def __init__(self, name, symbol, total_supply, owner_address):
        # The token's name e.g. "DecodeCoin"
        self.name = name

        # The token's symbol e.g. "DCL" (like BTC, ETH, USDT)
        self.symbol = symbol

        # Total supply: how many tokens exist in total
        # We use Decimal() to avoid floating point precision errors
        self.total_supply = Decimal(str(total_supply))

        # The owner's address (the person who created the token)
        self.owner_address = owner_address

        # balances: a dictionary that maps each address to their token balance
        # At the start, all tokens go to the owner/creator
        # This is exactly how real ERC-20 tokens work on Ethereum
        self.balances = {
            owner_address: self.total_supply
        }

        # transaction_log: a list that records every transfer that happens
        # On a real blockchain, these are called "events"
        self.transaction_log = []

        print(f"\n{'='*55}")
        print(f"  TOKEN DEPLOYED SUCCESSFULLY")
        print(f"{'='*55}")
        print(f"  Name:         {self.name}")
        print(f"  Symbol:       {self.symbol}")
        print(f"  Total Supply: {self.total_supply} {self.symbol}")
        print(f"  Owner:        {self.owner_address}")
        print(f"{'='*55}\n")

    # --------------------------------------------------------
    # HELPER: validate_address()
    # Checks if an address looks like a real Ethereum address.
    # Real Ethereum addresses start with "0x" followed by
    # exactly 40 hexadecimal characters (0-9 and a-f).
    # Example: 0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B
    # --------------------------------------------------------
    def validate_address(self, address):
        # re.fullmatch checks the ENTIRE string against the pattern
        # ^0x means "must start with 0x"
        # [0-9a-fA-F]{40} means "followed by exactly 40 hex characters"
        pattern = r'^0x[0-9a-fA-F]{40}$'
        return bool(re.fullmatch(pattern, address))

    # --------------------------------------------------------
    # FUNCTION 1: balanceOf(address)
    # This is the "getter" - it just reads the balance.
    # It does NOT change anything on the ledger.
    # In real ERC-20, this is a "view" function - free to call,
    # no gas fee required.
    # --------------------------------------------------------
    def balanceOf(self, address):
        # First validate the address format
        if not self.validate_address(address):
            print(f"  [ERROR] Invalid address format: {address}")
            return None

        # .get() returns 0 if the address has never received tokens
        # This means any new address starts with 0 balance
        balance = self.balances.get(address, Decimal('0'))
        return balance

    # --------------------------------------------------------
    # FUNCTION 2: transfer(sender, to, amount)
    # This is the "setter" - it actually moves tokens.
    # This is the most important and most security-critical function.
    # Three things must happen in order:
    #   1. Validate all inputs (addresses + amount)
    #   2. Check sender has enough balance (prevent overdraft)
    #   3. Subtract from sender, add to recipient
    # --------------------------------------------------------
    def transfer(self, sender, to, amount):
        print(f"\n{'='*55}")
        print(f"  INITIATING TRANSFER")
        print(f"{'='*55}")
        print(f"  From:   {sender}")
        print(f"  To:     {to}")
        print(f"  Amount: {amount} {self.symbol}")
        print(f"{'='*55}")

        # --- INPUT PHASE: Validate everything before touching balances ---

        # Check 1: Sender address must be valid format
        if not self.validate_address(sender):
            print(f"  [FAIL] Invalid sender address format.")
            return False

        # Check 2: Recipient address must be valid format
        if not self.validate_address(to):
            print(f"  [FAIL] Invalid recipient address format.")
            return False

        # Check 3: Cannot send tokens to yourself
        if sender.lower() == to.lower():
            print(f"  [FAIL] Sender and recipient cannot be the same address.")
            return False

        # Check 4: Convert amount to Decimal for precision
        # This prevents floating point errors with large token amounts
        try:
            transfer_amount = Decimal(str(amount))
        except InvalidOperation:
            print(f"  [FAIL] Invalid amount entered: {amount}")
            return False

        # Check 5: Amount must be greater than zero
        # ERC-20 standard allows zero transfers but we block them here
        if transfer_amount <= Decimal('0'):
            print(f"  [FAIL] Transfer amount must be greater than zero.")
            return False

        # --- PROCESS PHASE: Check balance and execute transfer ---

        # Get the sender's current balance (default 0 if new address)
        sender_balance = self.balances.get(sender, Decimal('0'))

        # Check 6: THE MOST CRITICAL CHECK
        # Sender cannot transfer more than they have (overdraft prevention)
        # This is the require(balance >= amount) check from ERC-20
        if sender_balance < transfer_amount:
            print(f"  [FAIL] Insufficient funds!")
            print(f"         Available Balance: {sender_balance} {self.symbol}")
            print(f"         Requested Amount:  {transfer_amount} {self.symbol}")
            print(f"         Shortfall:         {transfer_amount - sender_balance} {self.symbol}")
            return False

        # --- STATE MUTATION: Actually move the tokens ---

        # Subtract from sender's balance
        self.balances[sender] = sender_balance - transfer_amount

        # Add to recipient's balance (create entry if new address)
        recipient_balance = self.balances.get(to, Decimal('0'))
        self.balances[to] = recipient_balance + transfer_amount

        # --- OUTPUT PHASE: Log the transaction ---

        # Record the transfer in our transaction log
        # On a real blockchain, this fires a "Transfer" event
        log_entry = {
            "from": sender,
            "to": to,
            "amount": transfer_amount,
            "symbol": self.symbol
        }
        self.transaction_log.append(log_entry)

        # Confirm success
        print(f"\n  [SUCCESS] Transfer completed!")
        print(f"  New Balance ({sender[:10]}...): {self.balances[sender]} {self.symbol}")
        print(f"  New Balance ({to[:10]}...):     {self.balances[to]} {self.symbol}")
        return True

    # --------------------------------------------------------
    # BONUS: print_transaction_history()
    # Shows all transfers that have happened
    # Like viewing your bank statement
    # --------------------------------------------------------
    def print_transaction_history(self):
        print(f"\n{'='*55}")
        print(f"  TRANSACTION HISTORY - {self.name} ({self.symbol})")
        print(f"{'='*55}")
        if not self.transaction_log:
            print("  No transactions yet.")
        for i, tx in enumerate(self.transaction_log, 1):
            print(f"\n  Transaction #{i}")
            print(f"  From:   {tx['from']}")
            print(f"  To:     {tx['to']}")
            print(f"  Amount: {tx['amount']} {tx['symbol']}")
        print(f"\n{'='*55}")

    # --------------------------------------------------------
    # BONUS: print_all_balances()
    # Shows every wallet's current balance
    # --------------------------------------------------------
    def print_all_balances(self):
        print(f"\n{'='*55}")
        print(f"  CURRENT BALANCES - {self.name} ({self.symbol})")
        print(f"{'='*55}")
        for address, balance in self.balances.items():
            print(f"  {address[:20]}... : {balance} {self.symbol}")
        print(f"{'='*55}")


# ============================================================
# PART 2: THE WALLET CLASS
# This simulates a user's wallet interface.
# It lets users interact with the token using human-readable
# inputs rather than raw function calls.
# ============================================================

class Wallet:
    def __init__(self, owner_name, address):
        # The human name of the wallet owner
        self.owner_name = owner_name

        # The Ethereum-style address of this wallet
        self.address = address

    def check_balance(self, token):
        # Ask the token contract what this wallet's balance is
        balance = token.balanceOf(self.address)
        if balance is not None:
            print(f"\n  Wallet: {self.owner_name} ({self.address[:15]}...)")
            print(f"  Balance: {balance} {token.symbol}")
        return balance

    def send(self, token, recipient_wallet, amount):
        # Call the token's transfer function
        # The sender is always this wallet's address
        return token.transfer(self.sender_address(), recipient_wallet.address, amount)

    def sender_address(self):
        return self.address


# ============================================================
# PART 3: RUNNING THE SIMULATION
# ============================================================

if __name__ == "__main__":
    print("\n" + "="*55)
    print("  DECODE LABS - ERC-20 TOKEN WALLET SIMULATION")
    print("="*55)

    # --- Step 1: Deploy the token ---
    # Create a token called "DecodeCoin" with symbol "DCL"
    # Total supply: 1,000,000 tokens
    # All tokens start in the owner's wallet

    OWNER_ADDRESS   = "0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B"
    ALICE_ADDRESS   = "0x1234567890AbcdEF1234567890aBCdef12345678"
    BOB_ADDRESS     = "0xDeF1234567890ABCdeF1234567890AbcDEF12345"
    CHARLIE_ADDRESS = "0xFeDcBa9876543210fEdCbA9876543210fEdCbA98"

    token = ERC20Token(
        name="DecodeCoin",
        symbol="DCL",
        total_supply=1000000,
        owner_address=OWNER_ADDRESS
    )

    # --- Step 2: Check initial balances ---
    print("\n  INITIAL BALANCES:")
    print(f"  Owner Balance:   {token.balanceOf(OWNER_ADDRESS)} DCL")
    print(f"  Alice Balance:   {token.balanceOf(ALICE_ADDRESS)} DCL")
    print(f"  Bob Balance:     {token.balanceOf(BOB_ADDRESS)} DCL")
    print(f"  Charlie Balance: {token.balanceOf(CHARLIE_ADDRESS)} DCL")

    # --- Step 3: Valid transfers ---
    print("\n\n  --- VALID TRANSFERS ---")

    # Owner sends 500,000 DCL to Alice
    token.transfer(OWNER_ADDRESS, ALICE_ADDRESS, 500000)

    # Owner sends 300,000 DCL to Bob
    token.transfer(OWNER_ADDRESS, BOB_ADDRESS, 300000)

    # Alice sends 100,000 DCL to Charlie
    token.transfer(ALICE_ADDRESS, CHARLIE_ADDRESS, 100000)

    # --- Step 4: Print all balances after valid transfers ---
    token.print_all_balances()

    # --- Step 5: Security tests - these should all FAIL ---
    print("\n\n  --- SECURITY TESTS (ALL SHOULD FAIL) ---")

    # Test 1: Overdraft attempt - Bob tries to send more than he has
    print("\n  TEST 1: Overdraft Attempt")
    token.transfer(BOB_ADDRESS, ALICE_ADDRESS, 999999)

    # Test 2: Invalid address format
    print("\n  TEST 2: Invalid Address Format")
    token.transfer("not-a-valid-address", ALICE_ADDRESS, 100)

    # Test 3: Zero amount transfer
    print("\n  TEST 3: Zero Amount Transfer")
    token.transfer(ALICE_ADDRESS, BOB_ADDRESS, 0)

    # Test 4: Negative amount
    print("\n  TEST 4: Negative Amount")
    token.transfer(ALICE_ADDRESS, BOB_ADDRESS, -500)

    # Test 5: Sending to yourself
    print("\n  TEST 5: Sending To Yourself")
    token.transfer(ALICE_ADDRESS, ALICE_ADDRESS, 100)

    # --- Step 6: Print final balances ---
    token.print_all_balances()

    # --- Step 7: Print full transaction history ---
    token.print_transaction_history()

    print("\n  Simulation complete. Alhamdulillah, ERC-20 wallet works!\n")
