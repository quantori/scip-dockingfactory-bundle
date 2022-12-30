# R language

Here you can see instruction how to build and use latest version of R environment for HPC.

We are using original [RPM specification](https://src.fedoraproject.org/rpms/R) for Fedora project
as initial step of our automation. We slighlty modified this specification to build our packages.

## References

* [Virtual environment for R](https://rdrr.io/cran/renv/man/)

## How to build R packages with Docker

Let's make a docker image installing build dependencies for R.  

    ```
    RPM_BUILD_DEPS=( \
      cairo-devel \
      gcc-gfortran \
      java-headless \
      less \
      libcurl-devel \
      libicu-devel \
      libjpeg-devel \
      libtiff-devel \
      libtool \
      libXmu-devel \
      libXt-devel \
      openblas-devel \
      pango-devel \
      pcre2-devel \
      readline-devel \
      'tex(latex)' \
      texinfo-tex \
      tcl-devel \
      tk-devel \
      tre-devel \
      valgrind-devel)
    ```

For Amazon 2:

    ```
    docker build --rm --build-arg packages=$(printf '%s:' ${RPM_BUILD_DEPS[@]}) \
                 --tag build/r/amazon:2 --file Dockerfile.amazon2 ./
    ```

For CentOS 7:


Now we can build RPM packages properly:

    ```
    docker run -t -v $(pwd):/build/source --name rlang build/r/amazon:2 cat

    docker exec -it rlang /bin/bash 
    > R_VERSION=4.1.2
    > curl -sL -o ${RPM_TOPDIR}/SOURCES/R-${R_VERSION}.tar.gz  https://cran.r-project.org/src/base/R-4/R-${R_VERSION}.tar.gz
    > cp source/R-3.3.0-fix-java_path-in-javareconf.patch rpmbuild/SOURCES/
    > rpmbuild -D "_topdir ${RPM_TOPDIR}" -bb /build/source/R-${R_VERSION}.spec
    ```


# Installation steps

sudo yum install -y R-core-4.1.2 R-core-devel
sudo R -e 'install.packages("renv",repos="http://cran.us.r-project.org")'
export RENV=/shared/R-lang
R -e 'renv::init(project=Sys.getenv("RENV"));renv::install("IRkernel");renv::isolate(project=Sys.getenv("RENV"))'
tar -czf R-lang.tar.gz $RENV


## Build:
# Create R env
export RENV_DIR="renv"
mkdir  ${RENV_DIR} && cd ${RENV_DIR}
/opt/R/4.0.5/bin/R -e 'renv::init();install.packages("IRkernel",repos="http://cran.us.r-project.org")'
echo "$(echo -ne 'setwd("~/'${RENV_DIR}'")\n'; cat .Rprofile)" > .Rprofile
cd ..
tar -zcvf $RENV_DIR.tar.gz $RENV_DIR
#(put tar file in a bundle dir)


## Deploy:
# Install R and renv package
export R_VERSION=4.0.5
export CENTOS_VERSION=7
curl -O https://cdn.rstudio.com/r/centos-${CENTOS_VERSION}/pkgs/R-${R_VERSION}-1-1.x86_64.rpm
sudo yum install R-${R_VERSION}-1-1.x86_64.rpm -y
sudo yum install compat-gcc-48-gfortran.x86_64 -y
sudo /opt/R/${R_VERSION}/bin/R -e 'install.packages("renv",repos="http://cran.us.r-project.org")'
# configure R
#(copy tar file from bundle to users and root homedir)
#Install with root
tar -xvf renv.tar.gz
cp -rf renv/.Rprofile /root
export PATH="/shared/bundle/jupyterhub/bin/:$PATH"
/opt/R/4.0.5/bin/R -e 'IRkernel::installspec(user = FALSE)'
# for users 
tar -xvf renv.tar.gz
cp -rf renv/.Rprofile ~/
