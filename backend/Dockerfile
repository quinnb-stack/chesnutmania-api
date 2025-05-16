FROM python:3.11-slim-bullseye

WORKDIR /code

COPY ./requirements /code/requirements

# Install system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    apt-transport-https \
    ca-certificates \
    gnupg \
    curl \
    telnet \
    netcat-traditional \
    libcairo2-dev \
    git \
    vim \
    net-tools

# Add Google Cloud CLI APT source
RUN curl -sSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" \
    > /etc/apt/sources.list.d/google-cloud-sdk.list && \
    apt-get update && \
    apt-get install -y google-cloud-cli && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements/requirements.txt

COPY  ./app /code/app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]