
# Load .env.example
export $(grep -v '^#' .env | xargs)

./venv/bin/uvicorn core.main:app --reload