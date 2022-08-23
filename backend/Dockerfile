FROM python:3.8-slim

WORKDIR /app
COPY . .
COPY ./backend/requirements.txt requirements.txt
RUN python -m pip install --upgrade pip
RUN pip3 install -r requirements.txt --no-cache-dir

ENV PYTHONPATH "${PYTHONPATH}:/app/backend"
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]