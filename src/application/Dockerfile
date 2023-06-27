FROM  python:3
RUN mkdir WORK_REPO
WORKDIR /WORK_REPO

# add the directory res to docker image
ADD res .

# copy the requiremnts.txt file and install it in the docker container
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# copy the config.ini file to the working directory
ADD config.ini config.ini

# download mdh-lib
RUN wget https://metadatahub.de/cloud/s/JpgrZMQBMn6GWHs/download/mdh-2.3.1-py3-none-any.whl
RUN pip install mdh-2.3.1-py3-none-any.whl

# mdh-configurations
RUN mkdir mdh_home

CMD python3 import-script/import_pipeline.py && python3 app.py


