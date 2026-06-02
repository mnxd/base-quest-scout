# Base Quest Scout

Read-only Base ecosystem opportunity radar.

This static GitHub Pages app classifies public Base opportunities and stops before wallet signatures, gas, transactions, KYC, payouts, registrations, or social posting.

## Safety Boundary

- No wallet connection.
- No signature.
- No gas or transaction.
- No claim, payout, KYC, or registration submit.
- No external social action.

## Closed Loop

Public discovery → risk classification → local candidate queue → human confirmation → account/wallet/social execution only after confirmation.

## Refresh

```bash
python scripts/build.py
python -m json.tool data/seeds.json >/dev/null
python -m json.tool data/latest.json >/dev/null
```

GitHub Actions refreshes the radar daily and can also be run manually.