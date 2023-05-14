FROM python:3
RUN mkdir WORK_REPO
WORKDIR /WORK_REPO

# add the directory res to docker image
ADD res .

# copy the requiremnts.txt file and install it in the dopcker container
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# execute the python file
CMD python Data_Import/SimpleTransfer.py
