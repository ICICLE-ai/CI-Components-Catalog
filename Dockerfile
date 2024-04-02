# Image: tapis/ci-catalog

FROM python:3.10.13-slim-bullseye

ENV APP_CONFIG_PATH=/catalog/config.yaml
ENV CONFIG_FILE=$CONFIG_FILE

RUN pip install Flask==2.2
RUN pip install pyyaml==6.0
RUN pip install requests==2.28.2
RUN pip install tapipy==1.2.20
RUN pip install neo4j
RUN pip install pytest
RUN pip install iciflaskn

# application directory
RUN mkdir /catalog

# data & default config
ADD components-data.yaml /catalog/components-data.yaml
RUN echo ${CONFIG_FILE} | base64 -d > /catalog/config.yaml

# code 
ADD catalog /catalog

WORKDIR /catalog

CMD ["python", "app.py"]
