# Build guide: Slurm REST API

Slurm is a workload manager which is used by SciP users in AWS. The AWS ParallelCluster
provides some Slurm binaries but it's not provided REST API for SLURM out of the box.
For this reason, we are building the binaries on our side to add the REST API for SciP
clusters.

As a result, we expect to have an RPM package with REST API, dependent libraries as well
as configuration files to run it as a system process (systemd daemon).


## How to build

Need to run the commands below on a parallel cluster node: 

    docker build --rm --tag slurm/build/amazon:2 --file Dockerfile.amazon2 ./


## How to install


    yum install -y https://scip-quantori-staging-landing-zone-us-east-1.s3.amazonaws.com/RPM/scip-release-1.1.0-2.noarch.rpm
    yum install -y scip-slurmrestd


## How to verify

Here you can find basic commands to verify that SLURM REST API is working well. Please,
see more details about using SLURM API in official documentation:

 * [Slurm REST API](https://slurm.schedmd.com/rest.html)
 * [JWT Authentication](https://slurm.schedmd.com/jwt.html)

Here is verification commands below:

    systemctl status slurmrestd
    eval $(sudo /opt/slurm/bin/scontrol token username=jupyterhub lifespan=300)
    curl -H "X-SLURM-USER-NAME: jupyterhub" -H "X-SLURM-USER-TOKEN: ${SLURM_JWT}" http://localhost:6800/slurm/v0.0.36/ping

The output of the last command must be JSON and the errors field is an empty list.
