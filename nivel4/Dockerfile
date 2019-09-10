FROM python
RUN apt-get update
RUN apt-get install nano
RUN mkdir /nivel4
WORKDIR /nivel4
COPY . /nivel4
RUN pip install --no-cache-dir -r nivel4_app/requirements.txt
CMD ["python", "nivel4_app/nivel4.py"]
