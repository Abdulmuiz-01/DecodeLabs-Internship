# ============================================================
#  DECODE LABS - PROJECT 2: Decentralized Voting System
#  Author: Abdulmuiz Najeemdeen
#  Language: Python 3
# ============================================================

# ============================================================
# WHAT IS A DECENTRALIZED VOTING SYSTEM?
# In a real election, you trust a central authority to count votes.
# In blockchain voting, the rules are written in code.
# Nobody can change the rules, nobody can vote twice,
# and the result is calculated automatically and transparently.
#
# This simulates how the famous Ballot.sol smart contract
# works on the Ethereum blockchain - but in Python.
# ============================================================


# ============================================================
# PART 1: THE VOTER CLASS
# Represents a single voter on the blockchain.
# Each voter has:
#   - weight: 1 if authorized, 0 if not
#   - voted: True/False - have they cast their vote?
#   - vote: which proposal index they voted for
# ============================================================

class Voter:
    def __init__(self):
        # weight: 0 = not authorized, 1 = authorized to vote
        # Only the chairperson can set this to 1
        self.weight = 0

        # voted: tracks if this voter has already cast their vote
        # Once True, they can NEVER vote again (no double voting)
        self.voted = False

        # vote: stores which proposal index they voted for
        # -1 means they haven't voted yet
        self.vote = -1


# ============================================================
# PART 2: THE PROPOSAL CLASS
# Represents a single option that voters can vote for.
# Each proposal has a name and a running vote count.
# ============================================================

class Proposal:
    def __init__(self, name):
        # The name of the proposal e.g. "Candidate A"
        self.name = name

        # vote_count: how many votes this proposal has received
        # Starts at 0, increases by 1 each time someone votes for it
        self.vote_count = 0


# ============================================================
# PART 3: THE BALLOT CLASS
# This is the main voting contract - it manages everything.
# The person who creates it becomes the "chairperson"
# and has special powers to authorize voters.
# ============================================================

class Ballot:
    def __init__(self, chairperson_address, proposal_names):
        # The chairperson is the ONLY person who can give voting rights
        # This is set once at creation and never changes
        self.chairperson = chairperson_address

        # voters: a dictionary mapping each address to their Voter object
        # Like a voter registration database
        self.voters = {}

        # proposals: a list of Proposal objects
        # Created from the list of names passed in
        self.proposals = []
        for name in proposal_names:
            self.proposals.append(Proposal(name))

        # The chairperson automatically gets voting rights
        self.voters[chairperson_address] = Voter()
        self.voters[chairperson_address].weight = 1

        # voting_open: controls whether voting is active
        self.voting_open = True

        print(f"\n{'='*55}")
        print(f"  BALLOT DEPLOYED SUCCESSFULLY")
        print(f"{'='*55}")
        print(f"  Chairperson: {chairperson_address}")
        print(f"  Proposals:")
        for i, proposal in enumerate(self.proposals):
            print(f"    [{i}] {proposal.name}")
        print(f"{'='*55}\n")

    # --------------------------------------------------------
    # HELPER: validate_address()
    # Same as Project 3 - checks Ethereum address format
    # --------------------------------------------------------
    def validate_address(self, address):
        import re
        pattern = r'^0x[0-9a-fA-F]{40}$'
        return bool(re.fullmatch(pattern, address))

    # --------------------------------------------------------
    # FUNCTION 1: giveRightToVote(voter_address)
    # Only the chairperson can call this.
    # It authorizes a specific address to cast a vote.
    # Security checks:
    #   - Only chairperson can authorize
    #   - Cannot authorize someone who already voted
    #   - Cannot authorize someone who is already authorized
    # --------------------------------------------------------
    def giveRightToVote(self, caller, voter_address):
        print(f"\n  [giveRightToVote] Caller: {caller[:15]}...")
        print(f"  [giveRightToVote] Target: {voter_address[:15]}...")

        # Check 1: Only the chairperson can give voting rights
        if caller != self.chairperson:
            print(f"  [FAIL] Only the chairperson can give voting rights.")
            return False

        # Check 2: Validate the voter's address format
        if not self.validate_address(voter_address):
            print(f"  [FAIL] Invalid voter address format.")
            return False

        # Check 3: Create voter entry if they don't exist yet
        if voter_address not in self.voters:
            self.voters[voter_address] = Voter()

        voter = self.voters[voter_address]

        # Check 4: Cannot authorize someone who already voted
        if voter.voted:
            print(f"  [FAIL] This voter has already cast their vote.")
            return False

        # Check 5: Cannot authorize someone who is already authorized
        if voter.weight >= 1:
            print(f"  [FAIL] This voter already has voting rights.")
            return False

        # Grant voting rights by setting weight to 1
        voter.weight = 1
        print(f"  [SUCCESS] Voting rights granted to {voter_address[:15]}...")
        return True

    # --------------------------------------------------------
    # FUNCTION 2: vote(voter_address, proposal_index)
    # A voter casts their vote for a specific proposal.
    # Security checks:
    #   - Voter must be authorized (weight >= 1)
    #   - Voter cannot have already voted
    #   - Proposal index must be valid
    #   - Voting must still be open
    # --------------------------------------------------------
    def vote(self, voter_address, proposal_index):
        print(f"\n{'='*55}")
        print(f"  VOTE BEING CAST")
        print(f"{'='*55}")
        print(f"  Voter:    {voter_address[:20]}...")
        print(f"  Proposal: [{proposal_index}] ", end="")

        # Check 1: Voting must still be open
        if not self.voting_open:
            print(f"\n  [FAIL] Voting has been closed.")
            return False

        # Check 2: Voter must exist in the system
        if voter_address not in self.voters:
            print(f"\n  [FAIL] Address not registered. No voting rights.")
            return False

        voter = self.voters[voter_address]

        # Check 3: Voter must be authorized (weight must be 1)
        if voter.weight == 0:
            print(f"\n  [FAIL] This address has no voting rights.")
            return False

        # Check 4: Voter cannot vote twice
        # This is the most critical security check in any voting system
        if voter.voted:
            print(f"\n  [FAIL] This voter has already voted. No double voting.")
            return False

        # Check 5: Proposal index must be valid
        if proposal_index < 0 or proposal_index >= len(self.proposals):
            print(f"\n  [FAIL] Invalid proposal index: {proposal_index}")
            print(f"         Valid range: 0 to {len(self.proposals) - 1}")
            return False

        # Print the proposal name now that we know it's valid
        print(self.proposals[proposal_index].name)

        # --- CAST THE VOTE ---
        # Mark the voter as having voted (prevents double voting)
        voter.voted = True
        voter.vote = proposal_index

        # Increment the proposal's vote count
        self.proposals[proposal_index].vote_count += 1

        print(f"  [SUCCESS] Vote cast for '{self.proposals[proposal_index].name}'!")
        return True

    # --------------------------------------------------------
    # FUNCTION 3: winningProposal()
    # Calculates which proposal has the most votes.
    # Uses if/else logic to loop through all proposals
    # and track the highest vote count.
    # --------------------------------------------------------
    def winningProposal(self):
        print(f"\n{'='*55}")
        print(f"  CALCULATING WINNING PROPOSAL...")
        print(f"{'='*55}")

        # Start with 0 winning votes and no winner yet
        winning_vote_count = 0
        winning_proposal_index = 0

        # Loop through all proposals and find the highest vote count
        for i in range(len(self.proposals)):
            if self.proposals[i].vote_count > winning_vote_count:
                winning_vote_count = self.proposals[i].vote_count
                winning_proposal_index = i

        # Handle edge case: no votes cast at all
        if winning_vote_count == 0:
            print(f"  No votes have been cast yet.")
            return None

        winner = self.proposals[winning_proposal_index]
        print(f"\n  WINNER: {winner.name}")
        print(f"  Votes:  {winner.vote_count}")
        print(f"\n  Full Results:")
        for i, proposal in enumerate(self.proposals):
            marker = " <-- WINNER" if i == winning_proposal_index else ""
            print(f"    [{i}] {proposal.name}: {proposal.vote_count} votes{marker}")
        print(f"{'='*55}")

        return winning_proposal_index

    # --------------------------------------------------------
    # BONUS: print_voter_status()
    # Shows the current status of all registered voters
    # --------------------------------------------------------
    def print_voter_status(self):
        print(f"\n{'='*55}")
        print(f"  VOTER STATUS REGISTRY")
        print(f"{'='*55}")
        for address, voter in self.voters.items():
            status = "Authorized" if voter.weight >= 1 else "Not Authorized"
            voted_str = f"Voted for [{voter.vote}] {self.proposals[voter.vote].name}" if voter.voted else "Has Not Voted"
            print(f"  {address[:20]}...")
            print(f"    Status: {status} | {voted_str}")
        print(f"{'='*55}")

    # --------------------------------------------------------
    # BONUS: close_voting()
    # Closes the ballot so no more votes can be cast
    # --------------------------------------------------------
    def close_voting(self):
        self.voting_open = False
        print(f"\n  [NOTICE] Voting has been officially closed.")
        print(f"  Final vote count is now locked.")


# ============================================================
# PART 4: RUNNING THE SIMULATION
# ============================================================

if __name__ == "__main__":
    print("\n" + "="*55)
    print("  DECODE LABS - DECENTRALIZED VOTING SYSTEM")
    print("="*55)

    # --- Step 1: Define addresses ---
    CHAIRPERSON = "0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B"
    VOTER_1     = "0x1234567890AbcdEF1234567890aBCdef12345678"
    VOTER_2     = "0xDeF1234567890ABCdeF1234567890AbcDEF12345"
    VOTER_3     = "0xFeDcBa9876543210fEdCbA9876543210fEdCbA98"
    VOTER_4     = "0xABcDEf1234567890ABCDef1234567890abcdef12"
    OUTSIDER    = "0x9999999999999999999999999999999999999999"

    # --- Step 2: Deploy the ballot with 3 proposals ---
    ballot = Ballot(
        chairperson_address=CHAIRPERSON,
        proposal_names=["Proposal Alpha", "Proposal Beta", "Proposal Gamma"]
    )

    # --- Step 3: Chairperson gives voting rights ---
    print("\n  --- GRANTING VOTING RIGHTS ---")
    ballot.giveRightToVote(CHAIRPERSON, VOTER_1)
    ballot.giveRightToVote(CHAIRPERSON, VOTER_2)
    ballot.giveRightToVote(CHAIRPERSON, VOTER_3)
    ballot.giveRightToVote(CHAIRPERSON, VOTER_4)

    # --- Step 4: Voters cast their votes ---
    print("\n\n  --- CASTING VOTES ---")
    ballot.vote(CHAIRPERSON, 0)   # Chairperson votes for Proposal Alpha
    ballot.vote(VOTER_1, 1)       # Voter 1 votes for Proposal Beta
    ballot.vote(VOTER_2, 1)       # Voter 2 votes for Proposal Beta
    ballot.vote(VOTER_3, 2)       # Voter 3 votes for Proposal Gamma
    ballot.vote(VOTER_4, 1)       # Voter 4 votes for Proposal Beta

    # --- Step 5: Print voter status ---
    ballot.print_voter_status()

    # --- Step 6: Security tests - all should FAIL ---
    print("\n\n  --- SECURITY TESTS (ALL SHOULD FAIL) ---")

    # Test 1: Double voting attempt
    print("\n  TEST 1: Double Voting Attempt")
    ballot.vote(VOTER_1, 0)

    # Test 2: Unauthorized voter (outsider) tries to vote
    print("\n  TEST 2: Unauthorized Voter Attempt")
    ballot.vote(OUTSIDER, 0)

    # Test 3: Non-chairperson tries to give voting rights
    print("\n  TEST 3: Non-Chairperson Giving Rights")
    ballot.giveRightToVote(VOTER_1, OUTSIDER)

    # Test 4: Invalid proposal index
    print("\n  TEST 4: Invalid Proposal Index")
    ballot.vote(VOTER_4, 99)

    # --- Step 7: Close voting ---
    ballot.close_voting()

    # Test 5: Voting after closing
    print("\n  TEST 5: Voting After Closing")
    ballot.vote(OUTSIDER, 0)

    # --- Step 8: Calculate and announce the winner ---
    ballot.winningProposal()

    print("\n  Simulation complete. Alhamdulillah, voting system works!\n")
