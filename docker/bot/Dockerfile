
# Use an official Python runtime as the base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy files to the working directory
COPY bot.py .
COPY api.py .
COPY database.py .
COPY util/ ./util
COPY guildcogs ./guildcogs
COPY cogs ./cogs
COPY assets ./assets
COPY config.py .

# Set the command to run the bot.py file
CMD ["python", "bot.py"]
