FROM python:3.9.0


COPY requirements.txt requirements.txt
RUN pip install --upgrade pip --no-cache-dir
# install requirements.  Do the lines one at a time, as this seems to have better behavior with avoiding
# compiling during pip installs. extra logic is to prevent pip from choking on empty lines
RUN pip install -r requirements.txt --no-cache-dir

ENV ENV_TYPE docker

COPY ./neuro ./neuro
COPY ./setup.py .
RUN pip install -e . 
EXPOSE 80 

ENV OMP_NUM_THREADS 1

CMD ["neuro", "--workers=4"] 