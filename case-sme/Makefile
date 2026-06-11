.PHONY: setup start stop restart logs seed dbt-run ibis-run pipeline test clean

setup:
	cp -n .env.example .env || true
	docker compose build

start:
	docker compose up -d

stop:
	docker compose down

restart:
	docker compose down && docker compose up -d

logs:
	docker compose logs -f

logs-airflow:
	docker compose logs -f airflow-webserver airflow-scheduler

logs-streamlit:
	docker compose logs -f streamlit

seed:
	docker compose exec -it airflow-webserver python /opt/airflow/seed/generate_data.py

dbt-run:
	docker compose exec -it airflow-webserver bash -c "cd /opt/airflow/transform_dbt && dbt run --profiles-dir ."

ibis-run:
	docker compose exec -it airflow-webserver python /opt/airflow/transform_ibis/run_transforms.py

pipeline:
	docker compose exec -it airflow-webserver python -c "from dlt_pipelines.pos_pipeline import run_pipeline; run_pipeline()"
	docker compose exec -it airflow-webserver python -c "from dlt_pipelines.inventory_pipeline import run_pipeline; run_pipeline()"
	docker compose exec -it airflow-webserver bash -c "cd /opt/airflow/transform_dbt && dbt run --profiles-dir ."
	docker compose exec -it airflow-webserver python /opt/airflow/transform_ibis/run_transforms.py

test:
	docker compose exec postgres psql -U sme_user -d sme_db -c "SELECT count(*) as order_count FROM raw.orders;"
	docker compose exec postgres psql -U sme_user -d sme_db -c "SELECT count(*) as item_count FROM raw.order_items;"
	docker compose exec postgres psql -U sme_user -d sme_db -c "SELECT count(*) as staging_orders_count FROM staging.stg_orders;"
	docker compose exec postgres psql -U sme_user -d sme_db -c "SELECT count(*) as mart_forecast_count FROM marts.mart_inventory_forecast;"
	docker compose exec postgres psql -U sme_user -d sme_db -c "SELECT count(*) as analytics_popularity_count FROM analytics.menu_popularity;"
	@echo "✅ All database checks passed!"

clean:
	docker compose down -v
	@echo "✅ Cleaned all volumes"
