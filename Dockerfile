FROM nexus.bmbzr.ir/base/python:3.10
RUN mkdir /app
WORKDIR /app
COPY requirements.txt .
RUN pip install --proxy=http://angrynerd:l00pback@192.168.88.231:456 --upgrade pip
RUN pip install --proxy=http://angrynerd:l00pback@192.168.88.231:456 -r requirements.txt -v
ENV HOST=0.0.0.0
ENV PORT=9000
ENV PROXY=http://angrynerd:l00pback@192.168.88.231:456
ENV FORCE_RENEW=False
ENV INSTANCE=v1
EXPOSE 9000
ADD . .
RUN pip install -e .
ENTRYPOINT ./runserver.sh
