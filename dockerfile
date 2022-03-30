#Deriving the latest base image
FROM python:3.8


#Labels as key value pair
LABEL Maintainer="harr0u"


# i have chosen /usr/app/src
WORKDIR /usr/app/src

#to COPY the remote file at working directory in container
COPY . ./

#CMD instruction should be used to run the software
#contained by your image, along with any arguments.
RUN pip install -r requirements.txt
CMD [ "python", "./main.py"]