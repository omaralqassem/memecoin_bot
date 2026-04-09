from solders.keypair import Keypair
import json

kp = Keypair()

# Save to file
with open("devnet.json", "w") as f:
    json.dump(list(kp.to_bytes()), f)

print("✅ Wallet created: devnet.json")
print("Public Key:", kp.pubkey())