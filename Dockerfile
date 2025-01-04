# Use an official Python runtime as a parent image 
FROM python:3.9-slim 
# Set the working directory in the container 
WORKDIR /app 
# Copy the requirements file into the container 
COPY sfsgl/requirements.txt /app/ 
# Install any needed packages specified in requirements.txt 
RUN pip install --no-cache-dir -r requirements.txt 
# Copy the current directory contents into the container at /app 
COPY sfsgl /app 
# Make port 5001 and 5002 available to the world outside this container 
EXPOSE 5001 
EXPOSE 5002 
# Define environment variable 
ENV NAME World 
# Run app.py when the container launches 
CMD ["python", "app.py"]