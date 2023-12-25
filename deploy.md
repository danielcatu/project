# Update linux
sudo apt update -y
sudo apt upgrade -y

# Install dependencies
sudo apt install build-essential
sudo apt install -y libssl-dev libffi-dev libncurses5-dev zlib1g zlib1g-dev libreadline-dev libbz2-dev libsqlite3-dev make gcc

# Install python
sudo apt-get install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt-get update
sudo apt install python3.10 python3-pip python3.10-venv -y

# add alias
alias python3='/usr/bin/python3.10'
alias k=kubectl

# pip upgrade
python3 -m pip install --upgrade pip
pip install --upgrade pip

# Create venv
python3 -m venv env
source env/bin/activate

# Install requirements
pip3 install -r requirements.txt

# Install Kind
# For AMD64 / x86_64
[ $(uname -m) = x86_64 ] && curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
# For ARM64
[ $(uname -m) = aarch64 ] && curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-arm64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# Install kn
wget https://github.com/knative/client/releases/download/knative-v1.11.2/kn-linux-amd64

sudo mv kn-linux-amd64 kn
chmod +x kn
sudo mv kn /usr/local/bin

kn version

# Install Knative quickstart
wget https://github.com/knative-extensions/kn-plugin-quickstart/releases/download/knative-v1.12.1/kn-quickstart-linux-amd64
mv kn-quickstart-linux-amd64 kn-quickstart
chmod +x kn-quickstart
sudo mv kn-quickstart /usr/local/bin

# Install Kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin

# Install Docker
sudo apt install docker.io -y
sudo groupadd docker
sudo usermod -aG docker ${USER}

# Create cluster
kind create cluster --name knative

# quickstart
kn quickstart kind

# Install Helm
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh

# Prometheus
cd test/serverless-functions/
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/kube-prometheus-stack -n default -f values.yaml

kubectl apply -f https://raw.githubusercontent.com/knative-extensions/monitoring/main/servicemonitor.yaml

# Install function
cd Parsec
kubectl delete namespace blackscholes
kubectl create namespace blackscholes
kn service apply -f ./function.yaml  -n=blackscholes

# Port forward
nohup kubectl port-forward -n default svc/prometheus-operated 9090 &

# Python
source ./env/bin/activate
nohup python /home/azureuser/tesis/project/test/init.py &

