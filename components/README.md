# SCIP: build recipes

This is a main folder for build rcipes of the SCIP components:


## How to update RPM metadata

1. Prerequiesites

    sudo yum install -y createrepo
    sudo mkdir -p /var/lib/repository

2. Update package metadata and sync data with S3:

    aws s3 sync s3://scip-quantori-develop-landing-zone-us-east-1/RPM /var/lib/repository
    find /var/lib/repository -maxdepth 3 -mindepth 3 -exec createrepo {} \;
    aws s3 sync /var/lib/repository s3://scip-quantori-develop-landing-zone-us-east-1/RPM
