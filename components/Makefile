#!/usr/bin/env make -f
# -*- makefile -*-

# Root directory for this project
SOURCEROOT := $(shell git rev-parse --show-toplevel)
include $(SOURCEROOT)/ops-tools/Makefile

# Get AWS account id to use as a part of container registry name
AWS_ACCOUNT_ID := $(shell $(AWSCMD) sts get-caller-identity --query 'Account' --output text)

# Command line tool for container management: podman or docker
DOCKER := $(shell command -v podman docker | head -1)

SCIP_COMPONENT ?= scip-bundle

# Short name of the repository for specific component in container registry
# TODO: the target platform name and architecure must be added here
# https://aws.amazon.com/ru/blogs/containers/introducing-multi-architecture-container-images-for-amazon-ecr/
SCIP_ECR_NAME=$(subst :,/,$(SCIP_NAMESPACE):$(SCIP_COMPONENT):ci:$(*))

# URI of the component repository
SCIP_ECR_URI=$(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(SCIP_ECR_NAME)


.PHONY: aws-ecr/%
aws-ecr/%:
	$(AWSCMD) ecr describe-repositories --repository-names '$*' 2>/dev/null || \
	$(AWSCMD) ecr create-repository \
	          --image-tag-mutability IMMUTABLE \
	          --repository-name $* > /dev/null

.PHONY: aws-ecr-authentication/%
aws-ecr-authentication/%: aws-ecr/%
	$(AWSCMD) ecr get-login-password | \
	$(DOCKER) login --username AWS --password-stdin $(SCIP_ECR_URI)

.PHONY: local-ci-image/%
local-ci-image/%: $(SOURCEROOT)/components/$(SCIP_COMPONENT)/Dockerfile.%
	$(DOCKER) build --rm --tag $(SCIP_ECR_NAME):$* --file $< .

.PHONY: remote-ci-image/%
remote-ci-image/%: aws-ecr-authentication/$(SCIP_ECR_NAME)
	$(DOCKER) tag $(SCIP_ECR_NAME):$* $(SCIP_ECR_URI):$(SCIP_VERSION)
	$(DOCKER) push $(SCIP_ECR_URI):$(SCIP_VERSION)

.PHONY: ci-image/%
ci-image/%:
	$(MAKE) -C $(CONTEXTDIR) local-ci-image/$*
	$(MAKE) -C $(CONTEXTDIR) remote-ci-image/$*

platform/%: ECR = $(SCIP_ECR_NAME)
platform/%:
	echo $(SCIP_ECR_NAME)