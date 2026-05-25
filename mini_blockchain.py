# ============================================================
#  DECODE LABS - PROJECT 1: Mini Blockchain
#  Author: Abdulmuiz Najeemdeen
#  Language: Python 3
# ============================================================

# We need two built-in Python libraries:
# - hashlib: gives us access to the SHA-256 hashing algorithm
# - datetime: lets us stamp each block with the time it was created
import hashlib
import datetime


# ============================================================
# PART 1: THE BLOCK CLASS
# Think of a Block like one page in a notebook.
# Each page has its own content AND a reference to the previous page.
# ============================================================

class Block:
    def __init__(self, index, data, previous_hash):
        # index: the position of this block in the chain (0, 1, 2, 3...)
        self.index = index

        # timestamp: the exact time this block was created
        self.timestamp = str(datetime.datetime.now())

        # data: the "payload" - what this block is actually storing
        # e.g. {"sender": "Alice", "receiver": "Bob", "amount": 50}
        self.data = data

        # previous_hash: the hash of the block BEFORE this one
        # This is what "chains" blocks together
        self.previous_hash = previous_hash

        # nonce: a number we keep changing during mining
        # We need it to find a valid hash that meets our difficulty target
        self.nonce = 0

        # hash: the digital fingerprint of THIS block
        # We calculate it by running all the above through SHA-256
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        # We combine all the block's data into one long string
        # then pass it through SHA-256 to get a fixed 64-character fingerprint
        block_string = (
            str(self.index) +
            self.timestamp +
            str(self.data) +
            self.previous_hash +
            str(self.nonce)
        )

        # hashlib.sha256() takes bytes, so we encode the string first
        # .hexdigest() gives us the result as a readable hex string
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty):
        # difficulty tells us how many leading zeros the hash must start with
        # e.g. difficulty=4 means the hash must start with "0000"
        target = "0" * difficulty

        # Keep looping until we find a hash that meets the target
        print(f"\n  Mining Block {self.index}...")
        attempts = 0

        while not self.hash.startswith(target):
            self.nonce += 1       # change the nonce by 1
            self.hash = self.calculate_hash()  # recalculate the hash
            attempts += 1

        print(f"  Block {self.index} mined after {attempts} attempts!")
        print(f"  Valid Hash: {self.hash}")


# ============================================================
# PART 2: THE BLOCKCHAIN CLASS
# This is the full notebook - it holds ALL the blocks together
# and makes sure nobody has tampered with any page.
# ============================================================

class Blockchain:
    def __init__(self):
        # difficulty: how hard mining is (number of leading zeros required)
        # 4 is standard for a demo. Real Bitcoin uses much higher difficulty.
        self.difficulty = 4

        # chain: a Python list that holds all our Block objects in order
        # We start it with the Genesis Block (the very first block)
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        # The Genesis Block is Block 0 - it has no parent
        # So we hardcode its previous_hash as "0"
        print("Creating Genesis Block (Block 0)...")
        genesis = Block(0, "Genesis Block - The Beginning", "0")
        genesis.mine_block(self.difficulty)
        return genesis

    def get_latest_block(self):
        # Returns the last block currently in the chain
        return self.chain[-1]

    def add_block(self, new_block):
        # Before adding a new block, we connect it to the chain
        # by setting its previous_hash to the hash of the current last block
        new_block.previous_hash = self.get_latest_block().hash

        # Now we mine the block (find a valid hash)
        new_block.mine_block(self.difficulty)

        # Once mined, append it to the chain
        self.chain.append(new_block)
        print(f"  Block {new_block.index} successfully added to the chain.\n")

    def is_chain_valid(self):
        # This method checks the ENTIRE chain for tampering
        # It runs two checks on every block (except the Genesis Block)

        print("\n" + "="*55)
        print("  RUNNING CHAIN VALIDATION...")
        print("="*55)

        # We start from index 1 (skip Genesis Block)
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            # --- CHECK 1: Stored Hash Integrity ---
            # Recalculate the hash of the current block from scratch
            # If it doesn't match the stored hash, the data was tampered with
            recalculated_hash = current_block.calculate_hash()
            if current_block.hash != recalculated_hash:
                print(f"  [FAIL] Block {i}: Data has been TAMPERED with!")
                print(f"         Stored Hash:       {current_block.hash}")
                print(f"         Recalculated Hash: {recalculated_hash}")
                return False

            # --- CHECK 2: Chain Linkage Integrity ---
            # The current block's previous_hash must match
            # the actual hash of the block before it
            if current_block.previous_hash != previous_block.hash:
                print(f"  [FAIL] Block {i}: Chain BROKEN - previous hash mismatch!")
                print(f"         Expected: {previous_block.hash}")
                print(f"         Found:    {current_block.previous_hash}")
                return False

            print(f"  [OK] Block {i} - Integrity verified.")

        print("="*55)
        print("  RESULT: Blockchain is VALID. No tampering detected.")
        print("="*55)
        return True


# ============================================================
# PART 3: RUNNING THE PROGRAM
# This is the "main" section - it actually executes everything
# ============================================================

if __name__ == "__main__":
    print("\n" + "="*55)
    print("  DECODE LABS - MINI BLOCKCHAIN SIMULATION")
    print("="*55 + "\n")

    # Step 1: Create the blockchain (automatically creates Genesis Block)
    blockchain = Blockchain()

    # Step 2: Mine 3 additional blocks with transaction data
    print("\nAdding Block 1...")
    blockchain.add_block(Block(1, {"sender": "Alice", "receiver": "Bob", "amount": 100}, ""))

    print("Adding Block 2...")
    blockchain.add_block(Block(2, {"sender": "Bob", "receiver": "Charlie", "amount": 50}, ""))

    print("Adding Block 3...")
    blockchain.add_block(Block(3, {"sender": "Charlie", "receiver": "Alice", "amount": 25}, ""))

    # Step 3: Print the full chain
    print("\n" + "="*55)
    print("  FULL BLOCKCHAIN LEDGER")
    print("="*55)
    for block in blockchain.chain:
        print(f"\n  Block #{block.index}")
        print(f"  Data:          {block.data}")
        print(f"  Timestamp:     {block.timestamp}")
        print(f"  Nonce:         {block.nonce}")
        print(f"  Previous Hash: {block.previous_hash[:20]}...")
        print(f"  Hash:          {block.hash[:20]}...")

    # Step 4: Validate the chain (should be VALID)
    blockchain.is_chain_valid()

    # Step 5: TAMPERING SIMULATION
    # Manually alter Block 1's data (like a hacker would)
    print("\n\n" + "="*55)
    print("  TAMPERING SIMULATION")
    print("  Altering Block 1 data directly...")
    print("="*55)
    blockchain.chain[1].data = {"sender": "Alice", "receiver": "HACKER", "amount": 9999}
    print("  Block 1 data changed. Re-running validation...\n")

    # Step 6: Validate again - should now FAIL and catch the tampering
    result = blockchain.is_chain_valid()
    print(f"\n  Chain Valid: {result}")

    print("\n  Simulation complete. Alhamdulillah, blockchain works!\n")
