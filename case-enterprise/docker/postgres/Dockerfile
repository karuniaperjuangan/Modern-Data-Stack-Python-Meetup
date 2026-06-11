FROM postgres:16

COPY init.sql /docker-entrypoint-initdb.d/01-init.sql

ENV POSTGRES_USER=erp_user
ENV POSTGRES_PASSWORD=erp_password_2024
ENV POSTGRES_DB=erp_db
