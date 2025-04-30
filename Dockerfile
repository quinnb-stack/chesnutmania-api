FROM python:3.13.3-slim-bullseye

WORKDIR /code

COPY ./requirements /code/requirements/

# Install dependencies and cleanup
RUN apt-get update && apt-get install -y \
    build-essential \
    apt-transport-https ca-certificates gnupg curl \
    telnet netcat-traditional libcairo2-dev \
    git vim net-tools && \
    curl -sSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" \
    > /etc/apt/sources.list.d/google-cloud-sdk.list && \
    apt-get update && apt-get install -y google-cloud-cli=473.0.0-0 && \
    apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements/requirements.txt

COPY . /code/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]