# Asyncworker with metrics on Docker Compose

Para montar o ambiente, rode `docker-compose up`. Pode levar um
tempo para baixar e construir as imagens. Ao final, alguns serviços
serão expostos:

- http://localhost:8080 - Asyncworker
- http://localhost:9000 - Prometheus
- http://localhost:3000 - Grafana. Acessível através do usuário `admin` e senha `admin`

