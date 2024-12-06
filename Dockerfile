FROM python:3.8-slim-buster

RUN pip install requests
RUN apt update && apt install sqlite3

ADD README.md .
ADD Dockerfile .

ADD database.py .
ADD network.py .
ADD request_retrier.py .
ADD bot.py .

CMD ["python", "bot.py"]