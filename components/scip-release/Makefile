#!/usr/bin/env make -f
# -*- makefile -*-

RPM_SPEC := $(dir $(lastword $(MAKEFILE_LIST)))/scip-release.spec

include $(dir $(RPM_SPEC))/../../ops-tools/Makefile

all: rpm deploy clean

.PHONY: rpm
rpm: $(RPM_SPEC)
	@mkdir -p $(BUILDDIR)/rpmbuild/{BUILD,RPMS,SRPMS}
	rpmbuild -D "_topdir $(BUILDDIR)/rpmbuild" \
	         -D "_sourcedir $(abspath $(dir $(RPM_SPEC)))" \
	         -D "scip_deployment_bucket $(SCIP_DEPLOYMENT_BUCKET)" \
	         -D "scip_environment $(SCIP_ENVIRONMENT)" \
	         -D "scip_owner $(SCIP_OWNER)" \
	         -bb "$<"

.PHONY: deploy
deploy:
	find $(BUILDDIR)/rpmbuild/RPMS/noarch -name *.rpm -type f -exec \
	     $(AWSCMD) s3 cp {} s3://$(SCIP_DEPLOYMENT_BUCKET)/RPM/ \;

clean:
	rm -rf $(BUILDDIR)/rpmbuild
