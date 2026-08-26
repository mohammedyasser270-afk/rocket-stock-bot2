# Rocket Stock Scanner V1

A free scanner that runs with GitHub Actions and sends reports to Telegram.

## Features

- Pulls active NASDAQ, NYSE and AMEX stocks from Alpaca.
- Excludes many ETFs, funds, warrants, preferred shares and SPAC-like names.
- Price range: `$2–$50`.
- Previous-day volume filter: `300,000`.
- Previous-day dollar-volume filter: `$3,000,000`.
- Calculates:
  - EMA9
  - EMA20
  - EMA50
  - RSI14
  - MACD
  - Relative Volume
  - ATR
  - 20-day support and resistance
- Scores technical setups.
- Sends the best results to Telegram.
- Scheduled scans skip automatically while the US market is closed.
- Manual runs work even while the market is closed.

## GitHub Secrets

Under:

`Settings → Secrets and variables → Actions`

Create:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_USER_ID`
- `ALPACA_API_KEY`
- `ALPACA_SECRET_KEY`

## Installation

1. Upload the project contents to the root of your repository.
2. Keep the folder structure unchanged.
3. Open `Actions`.
4. Select `Rocket Stock Scanner`.
5. Select `Run workflow`.

## Important limitations

- Alpaca's free feed is IEX rather than Full SIP.
- GitHub scheduled workflows may run late.
- This is not a persistent Telegram command bot.
- Sharia compliance is not automatically verified.
- Entry, stop and target values are mechanical estimates.
- News and SEC catalysts are planned for the next version.
