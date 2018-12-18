FROM python:3.6

WORKDIR /itbapp

COPY requirements.txt ./

RUN pip install -r requirements.txt


ENTRYPOINT ["sh"]
