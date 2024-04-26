FROM --platform=linux/amd64 locustio/locust:2.20.1
RUN pip3 install oauthlib
RUN pip3 install requests_oauthlib
COPY . ./

# for standalone
ENTRYPOINT ["locust", "-f", "./locustfile.py"]
# for worker
# CMD [ "--worker", "--master-host", "MASTER_HOST_NAME"]
# for master
# CMD ["--master"]
