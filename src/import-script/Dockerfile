FROM python:3
RUN mkdir WORK_REPO
WORKDIR /WORK_REPO

# add the directory res to docker image
ADD res .

# copy the requiremnts.txt file and install it in the dopcker container
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# add the graphql file to the work repo
COPY /res/Data_Import/request.gql request.gql

# download mdh-lib
RUN wget https://metadatahub.de/cloud/s/JpgrZMQBMn6GWHs/download/mdh-2.3.1-py3-none-any.whl
RUN pip install mdh-2.3.1-py3-none-any.whl


# mdh-configurations
RUN mkdir Data_Import/mdh_home

# execute the python file to start transfer
CMD python Data_Import/SimpleTransfer.py
