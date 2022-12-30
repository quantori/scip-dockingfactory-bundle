# Build environment with Docker


## Build docker image with SCIP build dependencies

For Amazon Linux 2:

    docker build --rm --tag build/scip/amazon:2 --file Dockerfile.amazon2 .

For CentOS 7:

    docker build --rm --tag build/scip/centos:7 --file Dockerfile.centos7 .


## Build SCIP bundle with docker

For Amazon Linux 2

    docker run -t -v $(pwd)/scip:/shared/src -v $(pwd)/bundle:/shared/bundle --name build-bundle build/scip/amazon:2 make -f /shared/src/Makefile bundle

For CentOS 7:

    docker run -t -v $(pwd)/scip:/shared/src -v $(pwd)/bundle:/shared/bundle --name build-bundle build/scip/centos:7 make -f /shared/src/Makefile bundle

## Push docker image into S3

For Amazon Linux 2 

    docker save scip/build/amazon:2 | gzip | aws --profile scip s3 mv - s3://scip-quantori-staging-landing-zone-us-east-1/docker/build-images/amazon2/0.3.0/image.tgz

For CentOS 7:

    docker save scip/build/centos:7 | gzip | aws --profile scip s3 mv - s3://scip-quantori-staging-landing-zone-us-east-1/docker/build-images/centos7/0.3.0/image.tgz
