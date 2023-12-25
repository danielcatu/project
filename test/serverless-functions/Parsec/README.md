# Commands
# Build the docker image
docker build -t ferret ./test/serverless-functions/ferret
# Upload the docker image to the registry
docker tag ferret:latest localhost:5001/ferret:latest

# Push the docker image to the registry
docker push localhost:5001/ferret:latest

# Create the namespace
kubectl create namespace serverless-functions
# Create the service
kn service create -f ./test/serverless-functions/function.yaml --force
# Get resources by nodes
kubectl describe nodes

# Configure replica
kubectl scale deployment deploymentname --replicas=0 -n namespacename

# Modify the deployment to use the image from the registry
kubectl edit deployment deploymentname -n namespacename

# Conncect to the pod
kubectl exec -it podname -- /bin/bash
# Test the service


# If you want to remove the docker image from the registry
- docker rmi localhost:5001/ferret:latest
- docker container stop registry && docker container rm -v registry

# config crictl
- cd /etc/containerd
- nano config.toml
- add the following lines
```
    [plugins."io.containerd.grpc.v1.cri".registry]
      [plugins."io.containerd.grpc.v1.cri".registry.mirrors]
        [plugins."io.containerd.grpc.v1.cri".registry.mirrors."kind-registry:5000"]
          endpoint = ["http://kind-registry:5000"]

      [plugins."io.containerd.grpc.v1.cri".registry.configs]
        [plugins."io.containerd.grpc.v1.cri".registry.configs."kind-registry:5000".tls]
          insecure_skip_verify = true
```
- systemctl restart containerd
- crictl config runtime-endpoint /run/containerd/containerd.sock
- crictl pull localhost:5001/ferret:latest
