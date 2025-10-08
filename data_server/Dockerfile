# get a base image for python
FROM python:3.11-slim

# set some environment variable
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# set local project directory - define working directory in container
WORKDIR /data_server
COPY . /data_server
ENV PYTHONPATH="/data_server"

# install some dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# expose server
EXPOSE 5000

# command to run the demo
CMD ["python", "src/host_local_server.py"]

