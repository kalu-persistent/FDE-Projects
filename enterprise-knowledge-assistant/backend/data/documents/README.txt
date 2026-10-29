NovaSphere Technologies Pvt. Ltd. - Dummy KB Documents

These files are fictional and intended only for RAG testing.
Suggested ingestion ACLs:
01, 02, 03, 04, 05, 06 -> ALL
07 -> HR,ADMIN

Recommended commands:
docker compose run --rm api python -m app.ingest --folder data/documents/public --roles ALL
docker compose run --rm api python -m app.ingest --folder data/documents/hr-restricted --roles HR,ADMIN
