FROM python:3.11.4-bookworm

RUN mkdir WORK_REPO
WORKDIR /WORK_REPO

# add the directory res to docker image
ADD res .

# copy the requiremnts.txt file and install it in the docker container
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# download mdh-lib
RUN wget https://metadatahub.de/cloud/s/JpgrZMQBMn6GWHs/download/mdh-2.3.1-py3-none-any.whl
RUN pip install mdh-2.3.1-py3-none-any.whl

# Install cron package
RUN apt-get update && apt-get install -y cron

# Set permissions for the cron job file
RUN chmod 0644 import-script/cronjob

# Apply the cron job
RUN crontab import-script/cronjob

# Start cron service and keep the container running
CMD python3 import-script/import_pipeline.py && env >> /etc/environment && service cron start && python3 app.py
