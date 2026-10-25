# AI Inventory Agent

A Django inventory assistant with a chat interface, stock tools, price and VAT calculations, and optional Gemini integration.

## Features

- Add, remove, and inspect inventory using local commands
- Set item prices and calculate totals with VAT
- Use a browser-based chat interface
- Connect Gemini privately for optional AI responses

![Working local command demonstration](docs/demo.png)

The local inventory commands work without an API key. Live Gemini responses have not been verified.

## Run locally on Windows

Use Python 3.12 or newer:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:DJANGO_DEBUG="True"
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test chat
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8001
```

On macOS/Linux, activate your environment and use `export DJANGO_DEBUG=True`. Open [localhost:8001](http://127.0.0.1:8001/) and try:

1. `add 10 chocolate bars`
2. `set price of chocolate bar to 2.00`
3. `what is the cost of 3 items of chocolate bar after adding 10% VAT`
4. `remove 2 chocolate bars`
5. `check chocolate bars`
6. `show inventory`

The quote returns 6.60 without changing stock. After removal, 8 bars remain.

## Optional Gemini integration

Copy `.env.example` to `.env`, set `GEMINI_API_KEY` privately, and restart. `chat/agent.py` handles Gemini separately from local commands. Model availability and live responses require verification with a valid key.

## Configuration and security

- Debug is disabled by default. Explicit local debug mode generates a temporary signing key; sessions reset on restart.
- For deployment, configure a new private `DJANGO_SECRET_KEY` and `DJANGO_ALLOWED_HOSTS`; keep debug disabled. Generate a key locally with `python -c "import secrets; print(secrets.token_urlsafe(50))"`. Never reuse historical signing keys.
- Keep `.env`, API keys, databases, logs, and virtual environments out of Git.
- Automated secret checks run on pushes and pull requests. Publishing this repository shares source code; it does not deploy the application.
