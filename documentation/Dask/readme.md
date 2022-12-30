
## Connecting to Dask Gateway and creating Dask cluster 

Dask provides a way to parallelize your python code and run it on multiple nodes/CPUs across the cluster. This way it is possible to process huge datasets much faster, but still work in a context of your python code right from JH notebook for instance.

This is an example of how to create your Dask cluster and run a simple computation there.

First of all you should run your notebook with “Dask“ kernel. The kernel contains all of the essential packages for Dask. If you want to use your own kernel, the following packages have to be installed there:

```
1.dask distributed dask-gateway dask-jobqueue dask-gateway-server bokeh jupyter-server-proxy sqlalchemy
```
After you have your notebook opened, you may start with creating your very first dask cluster. For your convenience, we have a couple of very basic example notebooks that spin up a cluster with different scaling modes. You may find those files in /shared/dask-gateway/examples/ folder. 

**Cluster options**

When you create a cluster you may choose a number of parameters for the cluster. Currently the following options are exposed:

- ```worker_instance_type``` - optional. Instance type of the worker ( list - depends on your cluster configuration ), by the default it is the smallest instance available.

- python_env - optional. This controls Python environment for worker and scheduler. By the default it is set to: “/shared/bundle/dask“. Please specify the path to your python environment if you want to use it. Both worker and Scheduler will have environment activated with the command:

```
1.source /path/to/python_env/bin/activate
```
- conda_env - optional. Same as python_env but for conda environments ( if conda is installed on the cluster ). Will be activated with:
```
1.source /shared/bundle/anaconda3/etc/profile.d/conda.sh && conda activate conda_env
```
Please make sure that you have the following packages installed into your custom environment 

```
1.dask distributed dask-gateway dask-jobqueue dask-gateway-server bokeh jupyter-server-proxy sqlalchemy
```
**Scaling**

Scaling is an option for the cluster after it is created. It defines how the cluster scales up/down when it needs to process something. There are two scaling options:

- fixed scaling - you define how many workers you want
- adaptive scaling - you define max and min of workers you want. cluster scales up/down depends on the workload.

With adaptive scaling workers that are not in use are shut down automatically (please note that if worker keeps some objects in memory, it will not be shut down).

**Cluster dashboard**

When the cluster is created you can access the dashboard of the cluster and look in real time how tasks are processed, as well you can see workers statistics and many other useful info for debugging. Dashboard URL is a parameter of the cluster object and it will be printed if you print cluster object within the notebook context. You can just access it from the same browser.

Please note that if you shutdown the cluster and then create a new one, the URL will change.

**Cluster logs**

Sometimes you need to look on a scheduler/worker log files if you see some errors. You may access them via dashboard. Also they are on the filesystem, in your ```~/.dask-gateway``` folder. If the cluster is crashed/shutdown, the log files are deleted automatically.

**Costs associated**

AWS charges for instance time. If you have just a Dask scheduler with no workers running - it costs $0.085/hr for X86 and $0.034/hr for ARM. Workers in test partition are the same price each. Workers in compute partition are much more expensive, so it is a rule of thumb to keep them down if you don’t process anything. After you finished your work - please shut down the cluster, not to have the Dask scheduler running. 

To make sure, you don’t have anything running when you finish your work, you can open the terminal and run the following command:
```
1.squeue -u $UID
```
The result will be something like:

![image](https://user-images.githubusercontent.com/90186820/132676846-7c646da6-547c-4fc3-bdda-e7ee051197a0.png)

In the screenshot above you see that there are two jobs running on the cluster, first one is your jupyterhub session, and the second one is dask scheduler. You may also see other jobs, like in ‘test' or ‘compute’ partitions - those are dask workers. You can cancel them by executing ```scancel <job_id>```. Please note that if you cancel your jupyterhub job, the access to the JH server will be terminated immediately.  

 

**Additional docs about DaskGateway and Dask**

There are a lot of documentation for Dask and Dask Gateway here: https://docs.dask.org/en/latest/
