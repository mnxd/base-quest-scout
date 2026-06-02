# Base Quest Scout

Read-only Base ecosystem opportunity radar.

The site classifies public Base opportunities and stops before wallet signatures, gas, transactions, KYC, payouts, reward claims, or social posting.

## Files

- `data/seeds.json` — manually curated public URLs to monitor.
- `scripts/build.py` — fetches public pages, classifies risk signals, and rebuilds the static page.
- `templates/index.html` — static page template with the Base app verification meta tag.
- `.github/workflows/update.yml` — daily rebuild plus manual workflow dispatch.

## Safety model

- `auto_track_zero_cost` — public/read-only information; safe to monitor automatically.
- `manual_confirmation_required` — account, wallet, or social boundary; ask the user first.
- `hard_stop` — signature, funds, gas, rewards, KYC, transaction, or payout; never act automatically.

Run locally:

```bash
python scripts/build.py
```
