# DockingFactory Bundle

Copyright (c) 2022 Quantori.

Docking Factory is a tool to automate molecular docking runs on an HPC cluster using the Dask framework. 

This is the head repo that contains all scripts and references required to build DockingFactory bundle.

DockingFactory provides unified way of running molecular docking with different software backends: AutoDock Vina, Smina, Qvina2, and rDock.

DockingFactory provides the automation of the whole process of molecular docking-based virtual screening of large databases. It allows scientists to work exclusively within their research environments with AWS ParrallelCluster and Jupyter Notebooks. 

Key advantages:

- Parallelization - DF allows users to easily configure and run docking for millions of compounds with different docking protocols.
- Scalability - DF can scale from small runs with a few thousand ligands up to millions without reconfiguration.
- Customization - Interface libraries are implemented in Python. Advanced users can design their docking protocols and pipelines by themselves.
- Open-source - Parallelization and cluster interaction are handled by an open-source Dask framework, which allows focusing on integration and improvement of the interface rather than on solving infrastructure tasks.

Tech stack includes AWS ParallelCluster, Python, Dask, Slurm, and docking backends written in C++.

## Bundle

The bundle consists of this head project and the following other projects:

- [DockingFactory](https://github.com/quantori/scip-dockingfactory)
- [DockingInterface](https://github.com/quantori/scip-dockinginterface)
- [Vina](https://github.com/quantori/scip-vina)
- [Smina](https://github.com/quantori/scip-smina)
- [QVina 2](https://github.com/quantori/scip-qvina)
- [rDock](https://github.com/quantori/scip-rdock)

## Installation

### Prerequisities

On a Debian-based system. run:

```
sudo apt install wget curl libffi-dev libssl-dev libbz2-dev g++ make
```

On a Redhat-based system, run:

```
sudo yum install wget curl libffi-devel libssl-devel libbz2-devel g++ make
```


### Getting submodules

```
git submodule init && git submodule update
cd dockinginterface
git submodule init && git submodule update
cd ..
```

### Building bundle

Example build command:

```
BUNDLE_PATH=/path/to/desired/bundle PARALLEL=8 make all
```

Upon completion of `make`, the self-contained bundle will appear in `/path/to/desired/bundle`. All the necessary binary libraries, Python modules, and the Python environment will be there.

**Note:** The bundle is not allowed to be moved to another directory after creation. You will have to re-run the installation in order to build the bundle in a different directory.

## Running DockingFactory

### Locally

```
. /path/to/desired/bundle/dask/bin/activate
dockingfactory.py [arguments] --local yes
```

### Via AWS ParallelCluster

```
. /path/to/desired/bundle/dask/bin/activate
srun python -u /path/to/desired/bundle/dask/bin/dockingfactory.py [arguments] 
```

See the [DockingFactory](https://github.com/quantori/scip-dockingfactory) page for command line arguments and examples.


## License

Quantori DockingFactory is released under [Apache License, Version 2.0](LICENSE.md)
