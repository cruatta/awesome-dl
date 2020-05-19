FROM python:3.7

COPY ./dist /dist

WORKDIR /dist

RUN pip install awesome_dl*.whl

EXPOSE 8080

CMD ["python3", "-m", "uvicorn", "awesomedl:app", "--host", "0.0.0.0", "--port", "8080"]