
1. padir; usenvm; vir paloma; pip install -r paloma_api/paloma_api/requirements.txt

2. padir; usenvm; cd dashboard; yarn install

3. padir; ./scripts/sync_secrets.sh

4. padir; usenvm; ./paloma_api/scripts/alembic/local_alembic_migrate.sh

5. psql paloma-local -c "truncate users cascade";

6. padir; usenvm; vir paloma; cd paloma_api; PYTHONPATH=$(pwd):$PYTHONPATH python paloma_api/utilities/create_local_data.py

