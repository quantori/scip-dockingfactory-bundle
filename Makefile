BUNDLE_TARBALL ?= bundle.tgz
# Build directory
BUNDLE_PATH ?= /shared/bundle
BOOST_VERSION=1_67_0
OPENBABEL_VERSION=3-1-1
PYTHON_VERSION=3.7.10
PYTHON_SHORTVER=3.7
PARALLEL?=16
PYTHONPATH=${BUNDLE_PATH}/Python-${PYTHON_VERSION}
PYTHON=${PYTHONPATH}/bin/python3
BOOST_URL_PATH=$(subst _,.,$(BOOST_VERSION))
CMAKE_VERSION=3.21.3
CMAKEPATH=${BUNDLE_PATH}/cmake-${CMAKE_VERSION}
CMAKE3 = ${CMAKEPATH}/bin/cmake

export ARCH := $(shell uname -m)


${BUNDLE_PATH}/tmp/cmake-${CMAKE_VERSION}.tar.gz:
	mkdir -p ${BUNDLE_PATH}/tmp/ &&\
	curl -L -o ${BUNDLE_PATH}/tmp/cmake-${CMAKE_VERSION}.tar.gz https://github.com/Kitware/CMake/releases/download/v${CMAKE_VERSION}/cmake-${CMAKE_VERSION}.tar.gz

${BUNDLE_PATH}/.cmake-${CMAKE_VERSION}: ${BUNDLE_PATH}/tmp/cmake-${CMAKE_VERSION}.tar.gz
	cd ${BUNDLE_PATH}/tmp &&\
	tar -xzf cmake-${CMAKE_VERSION}.tar.gz &&\
	cd cmake-${CMAKE_VERSION} &&\
	./configure --prefix=${CMAKEPATH} &&\
	make -j${PARALLEL} &&\
	make install &&\
	touch ${BUNDLE_PATH}/.cmake-${CMAKE_VERSION}

${BUNDLE_PATH}/tmp/Python-${PYTHON_VERSION}.tgz :
	@mkdir -p $(@D)
	curl -L -o ${BUNDLE_PATH}/tmp/Python-${PYTHON_VERSION}.tgz https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz

${BUNDLE_PATH}/.python-${PYTHON_VERSION} : ${BUNDLE_PATH}/tmp/Python-${PYTHON_VERSION}.tgz
	tar -xzf ${BUNDLE_PATH}/tmp/Python-${PYTHON_VERSION}.tgz &&\
	cd Python-${PYTHON_VERSION} &&\
	./configure --enable-optimizations --prefix ${PYTHONPATH} &&\
	make PROFILE_TASK="-m test.regrtest --pgo -j${PARALLEL}" -j ${PARALLEL} && make install &&\
	ln -s ${PYTHONPATH}/include/python${PYTHON_SHORTVER}m ${PYTHONPATH}/include/python${PYTHON_SHORTVER} &&\
	touch ${BUNDLE_PATH}/.python-${PYTHON_VERSION}

.PHONY: python
python: ${BUNDLE_PATH}/.python-${PYTHON_VERSION}
.PHONY: cmake
cmake: ${BUNDLE_PATH}/.cmake-${CMAKE_VERSION}

${BUNDLE_PATH}/tmp/boost_${BOOST_VERSION}.tar.gz:
	@mkdir -p $(@D)
	curl -L -o ${BUNDLE_PATH}/tmp/boost_${BOOST_VERSION}.tar.gz https://downloads.sourceforge.net/project/boost/boost/${BOOST_URL_PATH}/boost_${BOOST_VERSION}.tar.gz

${BUNDLE_PATH}/.popt : 
	rm -rf ${BUNDLE_PATH}/popt &&\
	rm -rf ${BUNDLE_PATH}/src/popt-1.18.tar.gz &&\
	wget http://ftp.rpm.org/popt/releases/popt-1.x/popt-1.18.tar.gz -P ${BUNDLE_PATH}/src/ &&\
	tar -xzf ${BUNDLE_PATH}/src/popt-1.18.tar.gz &&\
	cd popt-1.18 &&\
	./configure --prefix ${BUNDLE_PATH}/popt-1.18 &&\
	make && make install &&\
	touch ${BUNDLE_PATH}/.popt

popt : ${BUNDLE_PATH}/.popt

$(BUNDLE_PATH)/.boost_$(BOOST_VERSION) : ${BUNDLE_PATH}/.python-${PYTHON_VERSION} ${BUNDLE_PATH}/tmp/boost_${BOOST_VERSION}.tar.gz
	rm -rf $(BUNDLE_PATH)/.boost_$(BOOST_VERSION) &&\
	tar -xzf $(BUNDLE_PATH)/tmp/boost_$(BOOST_VERSION).tar.gz &&\
	cd boost_${BOOST_VERSION} &&\
	./bootstrap.sh --with-python=${PYTHON} --prefix=${BUNDLE_PATH}/boost_${BOOST_VERSION} &&\
	./bjam -j${PARALLEL} &&\
	./bjam install --prefix=${BUNDLE_PATH}/boost_${BOOST_VERSION} &&\
	touch $(BUNDLE_PATH)/.boost_$(BOOST_VERSION)

boost : ${BUNDLE_PATH}/.boost_${BOOST_VERSION}


$(BUNDLE_PATH)/openbabel/v$(OPENBABEL_VERSION): $(BUNDLE_PATH)/.boost_$(BOOST_VERSION)
	mkdir -p ${BUNDLE_PATH}/openbabel/lib
	ln -sf ${BUNDLE_PATH}/openbabel/lib ${BUNDLE_PATH}/openbabel/lib64
	echo CMAKE3=${CMAKE3} $(MAKE) -C components/openbabel build \
	        BOOSTROOT=$(BUNDLE_PATH)/boost_$(BOOST_VERSION) \
	        OPENBABEL_INSTALL_PREFIX=$(BUNDLE_PATH)/openbabel \
	        OPENBABEL_VERSION=$(OPENBABEL_VERSION) \

	CMAKE3=${CMAKE3} $(MAKE) -C components/openbabel build \
	        BOOSTROOT=$(BUNDLE_PATH)/boost_$(BOOST_VERSION) \
	        OPENBABEL_INSTALL_PREFIX=$(BUNDLE_PATH)/openbabel \
	        OPENBABEL_VERSION=$(OPENBABEL_VERSION) \
		PYTHOROOT=$(PYTHONPATH) &&\
	CMAKE3=${CMAKE3} $(MAKE) -C components/openbabel install \
	        OPENBABEL_INSTALL_PREFIX=$(BUNDLE_PATH)/openbabel &&\
	touch $(BUNDLE_PATH)/openbabel/v$(OPENBABEL_VERSION)

openbabel: $(BUNDLE_PATH)/openbabel/v$(OPENBABEL_VERSION)

# Install golang as a build dependency for dask-gateway-server
$(BUNDLE_PATH)/tmp/golang/bin/go: GOLANG_ARCH := $(shell test "${ARCH}" = "aarch64" && echo arm64 || echo $(GOLANG_ARCH))
$(BUNDLE_PATH)/tmp/golang/bin/go: GOLANG_ARCH := $(shell test "${ARCH}" = "x86_64" && echo amd64 || echo $(GOLANG_ARCH))
$(BUNDLE_PATH)/tmp/golang/bin/go:
	@mkdir -p $(@D)
	@mkdir -p $(BUNDLE_PATH)/tmp/golang/.cache
	curl -Ls https://dl.google.com/go/go1.17.1.linux-$(GOLANG_ARCH).tar.gz | tar -xz -C $(BUNDLE_PATH)/tmp/golang --strip-components 1

.PHONY: golang
golang: $(BUNDLE_PATH)/tmp/golang/bin/go

uname_s := $(shell uname -s)

ifeq (${ARCH},aarch64)
	ARCH = arm64
endif

$(BUNDLE_PATH)/.dockinginterface: export GOCACHE=$(BUNDLE_PATH)/tmp/golang/.cache
$(BUNDLE_PATH)/.dockinginterface: export GO111MODULE=auto
$(BUNDLE_PATH)/.dockinginterface: export PATH := $(BUNDLE_PATH)/tmp/golang/bin:$(PATH)
$(BUNDLE_PATH)/.dockinginterface: VENV_PATH := $(BUNDLE_PATH)/dask
$(BUNDLE_PATH)/.dockinginterface: $(BUNDLE_PATH)/.python-$(PYTHON_VERSION) $(BUNDLE_PATH)/.popt $(BUNDLE_PATH)/.boost_$(BOOST_VERSION) $(BUNDLE_PATH)/tmp/golang/bin/go $(BUNDLE_PATH)/openbabel/v$(OPENBABEL_VERSION)
	rm -rf $(VENV_PATH) &&\
	$(PYTHON) -m venv $(VENV_PATH) &&\
	$(VENV_PATH)/bin/pip3 install --upgrade pip wheel &&\
	$(VENV_PATH)/bin/pip3 install ipykernel wheel dask distributed boto3 dask-gateway \
          dask-jobqueue dask-gateway-server bokeh jupyter-server-proxy \
          sqlalchemy pandas numpy scipy matplotlib seaborn plotly scikit-learn \
          statsmodels gensim nltk &&\
        cd dockinginterface/handlers/rdock/build && \
        export POPT_DIR=${BUNDLE_PATH}/popt-1.18 && \
        make linux-g++-64 &&\
        mkdir -p ../../../DockingInterface/DockingInterface/C_Dynamic_Libs/${uname_s}/${ARCH}/ &&\
        cp linux-g++-64/release/lib/libRbt.so ../../../DockingInterface/DockingInterface/C_Dynamic_Libs/${uname_s}/${ARCH}/ &&\
		cd ../../../ && mkdir -p lib && cd lib &&\
		${CMAKE3} .. -DBOOST_ROOT=${BUNDLE_PATH}/boost_${BOOST_VERSION} -DOPENBABEL3_ROOT=$(BUNDLE_PATH)/openbabel &&\
        make -j${PARALLEL} && cd ../DockingInterface && \
        $(VENV_PATH)/bin/pip3 install . && cd ../.. &&\
	patch -d $(BUNDLE_PATH) -p0 < dask-gateway/dask.patch/slurm.py.patch &&\
	rm -rf $(BUNDLE_PATH)/dask-gateway && mkdir $(BUNDLE_PATH)/dask-gateway &&\
	cp -r dask-gateway/files/* $(BUNDLE_PATH)/dask-gateway/ &&\
	touch $(BUNDLE_PATH)/.dockinginterface

.PHONY: dockinginterface
dockinginterface: cmake $(BUNDLE_PATH)/.dockinginterface

.PHONY: docs
docs :
	$(MAKE) -C documentation BUNDLE_PATH=$(BUNDLE_PATH)

.PHONY: all
all: dockinginterface dockingfactory

dockingfactory: dockinginterface $(BUNDLE_PATH)/dockingfactory

$(BUNDLE_PATH)/dockingfactory:
	cd dockingfactory && . $(BUNDLE_PATH)/dask/bin/activate && python setup.py install

.PHONY: clean-python
clean-python: clean-boost clean-docking
	rm -f ${BUNDLE_PATH}/tmp/Python-${PYTHON_VERSION}.tgz
	rm -f ${BUNDLE_PATH}/.python_${PYTHON_VERSION}

.PHONY: clean-boost
clean-boost: clean-openbabel
	rm -f ${BUNDLE_PATH}/.boost_${BOOST_VERSION}
	rm -f ${BUNDLE_PATH}/tmp/boost_${BOOST_VERSION}.tar.gz

.PHONY: clean-openbabel
clean-openbabel: clean-docking
	rm -f $(BUNDLE_PATH)/openbabel/v$(OPENBABEL_VERSION)
	$(MAKE) -C components/openbabel clean-installed clean

.PHONY: clean-docking
clean-docking: clean-dockinginterface
	rm -rf $(BUNDLE_PATH)/tmp/docking-interface

.PHONY: clean-dockinginterface
clean-dockinginterface:
	rm -f $(BUNDLE_PATH)/.dockinginterface
	rm -rf $(BUNDLE_PATH)/dask
	rm -rf $(BUNDLE_PATH)/dask-gateway

clean: clean-python

$(BUNDLE_TARBALL): all
	tar --exclude=tmp -czf $(BUNDLE_TARBALL) -C $(BUNDLE_PATH) ./

.PHONY: bundle
bundle: $(BUNDLE_TARBALL)
