FROM python:3

WORKDIR .

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . . 
COPY ./proto . 

CMD python3 server.py --port 8080 --host 0.0.0.0

EXPOSE 8080/tcp

