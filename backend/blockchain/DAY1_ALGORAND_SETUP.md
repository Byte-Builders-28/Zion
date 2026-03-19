# Day 1 — Algorand Wallet + On-Chain Incident Logging (Interactive Guide)

> ✅ This guide covers the full Day 1 flow: **Install → Generate Wallet → Fund → .env → Logger → Test**.
> 
> Use the links below to jump around, and tick the checklist items as you finish them.

---

## Progress

- [ ] Step 1: Install SDKs
- [ ] Step 2: Generate wallet (run once)
- [ ] Step 3: Fund the wallet (testnet)
- [ ] Step 4: Write `backend/.env`
- [ ] Step 5: Add logger module (already done)
- [ ] Step 6: Run the test script

---

## Navigation

- [Step 1 → Install](#step-1---install)
- [Step 2 → Generate Wallet](#step-2---generate-wallet)
- [Step 3 → Fund Wallet](#step-3---fund-wallet)
- [Step 4 → Write `.env`](#step-4---write-env)
- [Step 5 → Logger Module](#step-5---logger-module)
- [Step 6 → Run the Test](#step-6---run-the-test)

---

## Step 1 - Install

✅ **Goal:** Install the Algorand SDK + dotenv.

```bash
pip install py-algorand-sdk python-dotenv
```

[⬅️ Back to top](#day-1---algorand-wallet--on-chain-incident-logging-interactive-guide) · [Next →](#step-2---generate-wallet)

---

## Step 2 - Generate Wallet (run once)

✅ **Goal:** Create a testnet wallet and print address + mnemonic.

```bash
python Zion/backend/blockchain/generate_wallet.py
```

> 🔴 **DANGER:** The mnemonic is the wallet keys. Anyone with it can drain the wallet.
> - Store it only in `backend/.env`.
> - Never commit it to GitHub.

[⬅️ Back](#step-1---install) · [Next →](#step-3---fund-wallet)

---

## Step 3 - Fund Wallet (testnet)

✅ **Goal:** Give the wallet 10 ALGO so you can send transactions.

1) Open the dispenser:

👉 https://dispenser.testnet.aws.algodev.network/

2) Paste your wallet address (starts with a capital letter, ~58 chars)
3) Click **Dispense**
4) Wait a few seconds, then verify the balance.

### Verify balance (optional)

Run:

```bash
python -c "from blockchain.algorand_logger import print_balance; print_balance()"
```

📌 If the wallet is funded, you’ll see something like:

```
Address: <your address>
Balance: 10.000000 ALGO (10000000 microAlgos)
```

[⬅️ Back](#step-2---generate-wallet) · [Next →](#step-4---write-env)

---

## Step 4 - Write `.env`

✅ **Goal:** Save your wallet details where the Python scripts can load them, and keep them out of Git.

Create `backend/.env` with:

```env
ALGO_MNEMONIC=word1 word2 ... word25
ALGO_ADDRESS=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
ALGO_NETWORK=testnet
```

> ✅ Tip: Use `backend/.env` only. Do not put the mnemonic in any `.py` file.

[⬅️ Back](#step-3---fund-wallet) · [Next →](#step-5---logger-module)

---

## Step 5 - Logger Module (already in place)

✅ **Goal:** Confirm the logger module exists and can write incidents on-chain.

The following files are already in `Zion/backend/blockchain/`:

- `algorand_logger.py` — logs incidents by writing JSON into the Algorand note field
- `generate_wallet.py` — generates a new wallet
- `test_algorand.py` — sends a test incident and prints the TX ID + explorer URL

> ✅ Tip: You can inspect `algorand_logger.py` to see the exact fields being written.

[⬅️ Back](#step-4---write-env) · [Next →](#step-6---run-the-test)

---

## Step 6 - Run the Test

✅ **Goal:** Send one on-chain incident transaction and verify it appears on AlgoExplorer.

```bash
python Zion/backend/blockchain/test_algorand.py
```

You should see output similar to:

```
[ALGO] Incident SG-TEST-001 logged on-chain
[ALGO] TX ID:   <TX_ID>
[ALGO] Explorer: https://testnet.algoexplorer.io/tx/<TX_ID>

TX ID:   <TX_ID>
Link:    https://testnet.algoexplorer.io/tx/<TX_ID>
```

✅ **Verify:** Open the explorer link and click the **Note** tab — you should see the full incident JSON.

---

## Checklist (click as you do it)

- [ ] Installed packages (py-algorand-sdk, python-dotenv)
- [ ] Generated wallet (saved address + mnemonic in `backend/.env`)
- [ ] Funded wallet via dispenser
- [ ] Verified wallet balance
- [ ] Ran `test_algorand.py` and got a TX ID
- [ ] Verified the TX in AlgoExplorer (Note tab shows JSON)

---

## Troubleshooting

- If `python` fails with `ModuleNotFoundError: No module named 'algosdk'`, rerun:

```bash
pip install py-algorand-sdk
```

- If `algorand_logger` errors about `ALGO_MNEMONIC` or `ALGO_ADDRESS`, confirm `backend/.env` is present and correct.

- If the TX never confirms, ensure you have funds in the wallet (see Step 3 verification).
