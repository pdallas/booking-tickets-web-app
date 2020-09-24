FROM ubuntu:16.04 
MAINTAINER Dallas Panagiotis <panagiotisdallasunipi@gmail.com>
RUN apt-get update
RUN apt-get install -y python3 python3-pip 
RUN pip3 install flask pymongo
RUN mkdir /app
COPY . /app
WORKDIR /app
EXPOSE 5000
ENTRYPOINT ["python3","-u","app.py"]