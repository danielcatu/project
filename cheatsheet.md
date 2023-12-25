## Knative Cheatsheet
# To create a new namespace
- kubectl create namespace serverless-functions
# To create a new service
- kn service create -f ./test/serverless-functions/function.yaml --force
# To update a service
- kn service apply -f ./test/serverless-functions/function.yaml
# To delete a service
- kn service delete ferret
# To list all services
- kn service list
# To list all pods
- kubectl get pods -n serverless-functions
# To get the logs of a pod
- kubectl logs -n serverless-functions -f ferret-00001-deployment-5b4b4b4b4b-5b4b4
# To get the yaml of a pod
- kubectl get pods -n serverless-functions ferret-00001-deployment-5b4b4b4b4b-5b4b4 -oyaml


## Docker Cheatsheet
# To build the docker image
- docker build -t ferret ./test/serverless-functions/ferret
# To upload the docker image to the registry
- docker tag ferret:latest localhost:5001/ferret:latest
# To push the docker image to the registry
- docker push localhost:5001/ferret:latest
# To remove the docker image from the registry
- docker rmi localhost:5001/ferret:latest
# To build the docker image and push it to docker hub
- docker buildx build  -t "danielcatu/ferret" --push .
