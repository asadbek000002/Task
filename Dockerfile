FROM python:3.11.1-slim

# set work directory
WORKDIR /app

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install minimal system dependencies
#RUN apt-get update && apt-get install -y --no-install-recommends \
#    libpq-dev \
#    curl \
#    ca-certificates \
# && rm -rf /var/lib/apt/lists/*


## Install uv
#ADD https://astral.sh/uv/install.sh /uv-installer.sh
#RUN sh /uv-installer.sh && rm /uv-installer.sh
#ENV PATH="/root/.local/bin/:$PATH"

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies using uv
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .
