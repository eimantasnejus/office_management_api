FROM python:3.6.9

# The enviroment variable ensures that the python output is set straight
# to the terminal with out buffering it first
ENV PYTHONUNBUFFERED 1

# Set the working directory to /office_management_api and copy project files to it
RUN mkdir /office_management_api
WORKDIR /office_management_api
COPY . /office_management_api/

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

VOLUME /office_management_api

# Create database
CMD python manage.py migrate
