# eBayCrawl

Python service that discovers eBay listings, stores them in SQLite, post-processes matches, and sends Telegram notifications.

## Project Structure

- `src/eBay_Crawl/` - core application package (installable module)
- `tests/` - tests and local experimentation scripts
- `Jenkinsfile` - root Jenkins pipeline definition
- `Dockerfile` - container build definition for CI/CD
- `requirements.txt` - pinned dependencies used by Jenkins
- `setup.py` - package metadata and install entry points

## Local Setup

1. Create and activate a virtual environment **outside** the repository (or use `.venv/` at the repo root — it is gitignored):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies and this project (editable install recommended for development):

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

Alternatively, without installing the package:

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
python -m eBay_Crawl.main
```

3. Set required environment variables:

- `Telegram_API_KEY`
- `Telegram_Channel_id`

4. Run the app:

```bash
python -m eBay_Crawl.main
```

## Jenkins Pipeline

The root `Jenkinsfile` runs:
- dependency setup,
- `flake8` lint checks,
- `pytest` test execution,
- Docker image build.

## Note On CAPTCHA / Anti-Bot Challenges

If eBay presents anti-bot checks, avoid bypass tooling. Prefer compliant options:
- reduce request rate and add jitter/backoff,
- cache pages and avoid repeated fetches,
- use official APIs or approved data providers where possible,
- add manual review/fallback flows when automated access is blocked.