# get a base image for python
FROM python:3.11-slim

# set some environment variable
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# set local project directory - define working directory in container
WORKDIR /samsara_demo
COPY . /samsara_demo
ENV PYTHONPATH="/samsara_demo"

# install some dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# command to run the demo
CMD ["python", "src/demo.py"]

