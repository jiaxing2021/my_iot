# FROM python:3.13.0a4-slim-bookworm
FROM python:3.8-slim-bullseye
# FROM python:3
# FROM python:3.11

COPY . .
# CMD ["python","./get-pip.py"]
# RUN pip3 install torch
RUN pip3 install cherrypy requests
CMD ["python3","./main_catalog.py"]

# CMD ["bash"]