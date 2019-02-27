
1. hodir; usenvm; vir hover; pip install -r backend/requirements.txt

2. hodir; usenvm; cd dashboard; yarn install

3. hodir; ./scripts/sync_secrets.sh

4. hodir; usenvm; ./backend/scripts/alembic/local_alembic_migrate.sh

5. psql hover-local -c "truncate users cascade";

6. hodir; usenvm; vir hover; cd backend; PYTHONPATH=$(pwd):$PYTHONPATH python backend/utilities/create_local_data.py

