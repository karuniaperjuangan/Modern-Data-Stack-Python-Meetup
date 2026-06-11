FROM pgduckdb/pgduckdb:16-v1.1.1

# Copy init script
COPY init.sql /docker-entrypoint-initdb.d/01-init.sql

# Set default environment variables
ENV POSTGRES_USER=sme_user
ENV POSTGRES_PASSWORD=sme_password_2024
ENV POSTGRES_DB=sme_db
