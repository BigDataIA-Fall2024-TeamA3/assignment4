# Use the official Airflow image with Python 3.8
FROM apache/airflow:2.10.2-python3.8

# Set environment variables
ENV AIRFLOW_HOME=/opt/airflow

# Copy the DAGs folder into the container
COPY dags/ $AIRFLOW_HOME/dags/

# Install additional Python packages if needed
RUN pip install boto3 tiktoken

# Initialize the Airflow database
RUN airflow db init

# Create an admin user
RUN airflow users create \
    --username admin \
    --firstname dummy \
    --lastname dummy \
    --role Admin \
    --email dummy@dummy.com \
    --password ""

# Expose the web server port
EXPOSE 8080

# Start the Airflow web server and scheduler
CMD ["bash", "-c", "airflow webserver --port 8080 & airflow scheduler"]