# get a base image for python
FROM python:3.11-slim

# set some environment variable
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# set project directory
WORKDIR /home/ecurl/samsara_demo

# install some dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy application source code
COPY . .

# command to run the demo
CMD ["python", "demo.py"]

