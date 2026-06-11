.PHONY: setup start stop restart logs logs-airflow logs-streamlit logs-minio seed dlt-run dbt-run ibis-run pipeline test clean

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

logs-minio:
	docker compose logs -f minio

seed:
	docker compose exec -it airflow-webserver python /opt/airflow/seed/generate_data.py

dlt-run:
	docker compose exec -it airflow-webserver python /opt/airflow/dlt_pipelines/erp_sales_pipeline.py
	docker compose exec -it airflow-webserver python /opt/airflow/dlt_pipelines/erp_inventory_pipeline.py
	docker compose exec -it airflow-webserver python /opt/airflow/dlt_pipelines/erp_finance_pipeline.py
	docker compose exec -it airflow-webserver python /opt/airflow/dlt_pipelines/ecommerce_pipeline.py

dbt-run:
	docker compose exec -it airflow-webserver bash -c "cd /opt/airflow/transform_dbt && dbt run --profiles-dir ."

ibis-run:
	docker compose exec -it airflow-webserver python /opt/airflow/transform_ibis/run_transforms.py

pipeline:
	docker compose exec -it airflow-webserver python /opt/airflow/seed/generate_data.py
	docker compose exec -it airflow-webserver python /opt/airflow/dlt_pipelines/erp_sales_pipeline.py
	docker compose exec -it airflow-webserver python /opt/airflow/dlt_pipelines/erp_inventory_pipeline.py
	docker compose exec -it airflow-webserver python /opt/airflow/dlt_pipelines/erp_finance_pipeline.py
	docker compose exec -it airflow-webserver python /opt/airflow/dlt_pipelines/ecommerce_pipeline.py
	docker compose exec -it airflow-webserver python /opt/airflow/dlt_pipelines/iceberg_helper.py
	docker compose exec -it airflow-webserver bash -c "cd /opt/airflow/transform_dbt && dbt run --profiles-dir ."
	docker compose exec -it airflow-webserver python /opt/airflow/transform_ibis/run_transforms.py

test:
	@echo "Checking containers..."
	docker compose ps
	@echo "Checking PostgreSQL..."
	docker compose exec postgres psql -U erp_user -d erp_db -c "SELECT count(*) as sales_orders FROM sap.sales_orders;"
	@echo "Checking MinIO..."
	docker compose exec minio-setup mc ls local/lakehouse/ || true
	@echo "Checking Iceberg REST Catalog..."
	curl -s http://localhost:8181/v1/config | head -20
	@echo "Checking Streamlit..."
	curl -s http://localhost:8502/_stcore/health
	@echo ""
	@echo "✅ All checks completed!"

clean:
	docker compose down -v
	@echo "✅ Cleaned all volumes"
