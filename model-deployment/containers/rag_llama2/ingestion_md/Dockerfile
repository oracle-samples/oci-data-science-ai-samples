FROM python:3.10

RUN mkdir /app

WORKDIR /app

COPY requirements.txt requirements.txt
COPY main.py main.py
COPY start.sh start.sh

# Installing the server dependencies.
RUN pip3 install -r requirements.txt

EXPOSE 8080

RUN chmod +x start.sh

CMD ["./start.sh"]