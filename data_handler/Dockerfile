# get a base image for python
FROM python:3.11-slim

# set some environment variable
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# set local project directory - define working directory in container
WORKDIR /data_handler
COPY . /data_handler
ENV PYTHONPATH="/data_handler"

# install some dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# command to run the demo
CMD ["python", "src/get_data_main.py"]

