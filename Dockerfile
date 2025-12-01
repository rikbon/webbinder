# Use a Conda base image
FROM continuumio/miniconda3

# Set the working directory in the container
WORKDIR /app

# Copy the environment file to the working directory
COPY environment.yml .

# Create the Conda environment
RUN conda env create -f environment.yml

# Copy the content of the local src directory to the working directory
COPY main.py .

# Activate the Conda environment and specify the command to run on container start
ENTRYPOINT ["conda", "run", "-n", "webbinder", "python", "main.py"]