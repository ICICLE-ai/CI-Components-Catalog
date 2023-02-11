# Image: tapis/ci-catalog

FROM python:3.10
RUN pip install Flask==2.2
RUN pip install pyyaml
RUN pip install requests

# application directory
RUN mkdir /catalog

# data & default config
ADD components-data.yaml /catalog/components-data.yaml
ADD config.yaml /catalog/config.yaml

# code 
ADD catalog /catalog

WORKDIR /catalog

CMD ["python", "app.py"]