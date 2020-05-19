FROM python:3.7

COPY ./dist /dist

WORKDIR /dist

RUN pip install awesome_dl*.whl

EXPOSE 8080

RUN useradd app -d /app -m -r -s /sbin/nologin

USER app

WORKDIR /app

CMD ["python3", "-m", "uvicorn", "awesomedl:app", "--host", "0.0.0.0", "--port", "8080"]