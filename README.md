# tech_learn

The environment: source .techlearn/bin/activate
export DJANGO_SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"
read -r -s -p "PostgreSQL password: " TECHLEARN_DB_PASSWORD
echo
export TECHLEARN_DB_PASSWORD
