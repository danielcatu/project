
First, you need to install Sysbox
```bash
wget https://downloads.nestybox.com/sysbox/releases/v0.6.1/sysbox-ce_0.6.1-0.linux_amd64.deb
```
```bash
docker rm $(docker ps -a -q) -f
```
```bash
  sudo apt-get install jq
  sudo apt-get install ./sysbox-ce_0.6.1-0.linux_amd64.deb
```

For building the docker image, run the following command:

```bash
docker build -t <image-name> .
```

For running the docker image, run the following command:

```bash
docker run -p 8080:8080 <image-name>
```

For attaching to the docker container, run the following command:

```bash
docker exec -it <container-id> /bin/bash
```

For development, you can use the following command to run the docker container:

```bash
docker run -p 80:80 -v $(pwd):/app <image-name>
docker run -p 80:80 --rm -it knative /bin/bash
```

With sysbox-runc:

```bash
docker run -p 80:80 --runtime=sysbox-runc --rm -it knative /bin/bash
```
