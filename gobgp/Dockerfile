FROM alpine:latest
ENV GOBGP_VERSION=2.33.0
ADD https://github.com/osrg/gobgp/releases/download/v${GOBGP_VERSION}/gobgp_${GOBGP_VERSION}_linux_amd64.tar.gz /
RUN tar zxvf /gobgp_${GOBGP_VERSION}_linux_amd64.tar.gz

# BGP
EXPOSE 179
# gRPC
EXPOSE 50051

RUN apk add --no-cache bash
ADD gobgp.conf.yml /gobgp.conf.yml
CMD ["./gobgpd", "-f", "/gobgp.conf.yml", "-t", "yaml", "$*"]