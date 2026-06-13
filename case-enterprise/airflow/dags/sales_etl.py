from airflow.decorators import dag, task
import pendulum

@dag(
    schedule="@daily",
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
)
def sales_etl():

    @task
    def extract():
        return [100, 200, 300]

    @task
    def transform(rows):
        return sum(rows)

    @task
    def load(total):
        print(f"revenue={total}")

    load(transform(extract()))

sales_etl()