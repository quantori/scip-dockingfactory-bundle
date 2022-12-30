# SCIP release package

The release package deliver YUM/DNF configuration for repositories that are provided by SCIP team.

## How to build

Please run the command below to build RPM package and upload the package to environment-specific storage:

    make all AWS_PROFILE=scip SCIP_ENVIRONMENT=staging
