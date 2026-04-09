#transaction_parser.py
from typing import Optional, Tuple

def extract_mint_and_wallet(tx):
    try:
        instructions = tx.transaction.transaction.message.instructions
        for instr in instructions:
            program = str(instr.program_id)
            if "Tokenkeg" in program: 
                data = instr.parsed
                if data and data.get("type") == "initializeMint":
                    mint = data["info"]["mint"]
                    wallet = tx.transaction.transaction.message.account_keys[0].pubkey
                    return mint, wallet
        return None, None
    except Exception:
        return None, None