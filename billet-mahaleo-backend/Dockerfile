FROM python:3.13.5-slim-buster as build
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN pip install -e .

FROM python:3.13.5-slim-buster as runner
WORKDIR /app
COPY --from=build /app .


ARG DB_USER
ARG DB_PASSWORD
ARG DB_HOST
ARG DB_NAME
ARG DB_PORT
ARG PORT=3136

ENV DB_USER=${DB_USER}
ENV DB_PASSWORD=${DB_PASSWORD}
ENV DB_HOST=${DB_HOST}
ENV DB_NAME=${DB_NAME}
ENV DB_PORT=${DB_PORT}
ENV PORT=${PORT}

EXPOSE ${PORT}
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "${PORT}"]
