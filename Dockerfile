FROM ubuntu:18.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl

# Copy the current directory contents into the container at /app
ADD . /app

# Set the working directory to /app
WORKDIR /app

# # Docker

# # Download command
RUN curl -fsSL https://get.docker.com -o get-docker.sh
# Install docker using the command
RUN sh get-docker.sh
RUN dockerd > /dev/null 2>&1 &
# kubectl

# Download command
RUN curl -LO https://dl.k8s.io/release/v1.27.2/bin/linux/amd64/kubectl
# Install kubectl binary using the command
RUN install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Kind

# Download command
RUN curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.19.0/kind-linux-amd64

# Install kind binary using the command
RUN chmod +x ./kind
RUN mv ./kind /usr/local/bin/kind

# knative cli

# Download command
RUN curl -L https://github.com/knative/client/releases/download/knative-v1.10.0/kn-linux-amd64 --output kn
# Install kn binary using the command
RUN chmod +x ./kn
RUN mv ./kn /usr/local/bin/kn

# Kn-plugin-quickstart

# Download command
RUN curl -L https://github.com/knative-sandbox/kn-plugin-quickstart/releases/download/knative-v1.10.0/kn-quickstart-linux-amd64 --output kn-quickstart

# Install kn-quickstart binary using the command
RUN chmod +x ./kn-quickstart
RUN mv ./kn-quickstart /usr/local/bin/kn-quickstart

# # Run knative quickstart
# RUN kn quickstart kind
