## Working with Vina/smina/qvina in Dask and DockingFactory
**Preparing ligands and target**

Usual recommendations for preparation of ligands and target for Vina/smina/qvina apply. DockingFactory accepts ligands and target in PDBQT format. Ligands should be placed in a single folder. Some hierarchy is allowed (subfolders are searched automatically). Archives are not automatically extracted at the moment.

**Configuring handler**

Handler can be vina, smina, or qvina. Configuration file must be present with either choice. Full set of settings that are allowed in the handler configuration file is outside the scope of this manual. Reader is referred to the documentation of the respective handler.

Simplest configuration file for smina will look like the following:
```
1. exhaustiveness = 3
2. scoring = vinardo
3. autobox_ligand = /home/user/path/to/crystal_ligand.pdbqt
```
**Configuring DockingFactory**

You can have a YAML configuration file, or specify parameters as the script’s command line arguments, or both. Command line arguments take precedence over configuration file.

 **Parameter name**| **Meaning** | **Notes**
 ----------------- | ----------- | ---------
 ```config```      |Path to YAML configuration file  |Optional; only as a command line parameter
 ```handler```     |Handler (engine)|```smina```, ```vina```, or ```qvina```
 ```handler_config```|Path to handler’s configuration file|
 ```input_path```  |Path to folder with .pdbqt ligands (subfolders are searched automatically)|
 ```receptor```    |Path to .pdbqt receptor|             
 ```output_folder```| Path to output folder for docked .pdbqt ligands| Must exist beforehand         
 ```csv_out``` |Path to output .csv file containing paths to input ligand files that have been successfully processed and their affinities|             
 ```failed_ligand_out```|Path to output .csv file containing paths to input ligand files whose processing has failed|             
 ```error_msg_out```|Path to output text file containing error messages for failed ligands|   
 ```server_mode```|Keep running after all ligands have been processed | False by default
          
  .|   **Dask cluster parameters**  | .
----------------- | -------------- | -------------------
 ```name```   |Name|
 ```address```   |Address|Please use IP address of the head node and port 8000
 ```maximum_scale```   |Maximum scale|
 ```partition```   |Partition|Should be “compute-cpu” in most cases
 ```worker_instance_type```   |Type of worker instance|c6g.16xlarge - recommended for production runs c6g.medium - recommended for test runs
 ```scheduler_instance_type```  |Type of scheduler_instance|c6g.medium - recommended

**Preparing shell environment**
```
source /shared/bundle/dask/bin/activate
```
**Running the script**
```
dockingfactory.py --config my_config.yml
```
or
```
1. dockingfactory.py --config my_config.yml --handler qvina --handler_config /path/to/qvina/config.txt --input_path /path/to/ligands ...
```
**Waiting for the script to finish**

It takes about 7 minutes until the cluster instances are started.

The script prints lines, one line per second, with the current statistics.
```
1. 12040/1913/12223 clusters:1 workers:4 CPUs:192 Time:2837s MinScore:-14.463799 MinLigand:/home/dpavlov/docking/DUDE_ppard/decoys/ZINC16487959.pdbqt
```
Here, 12040 is the number of processed ligands (both successes and failures), 1913 is the number of failures, and 12223 is the total number of ligands.

As soon as all ligands are processed, the script terminates (unless you specified --server_mode=true).

**Configuration file example**
```
1. address: http://10.2.34.23:8000
2. maximum_scale: 1
3. name: cluster-arm
4. partition: compute-cpu
5. worker_instance_type: c6g.16xlarge
6. scheduler_instance_type: c6g.medium
7.
8. handler: smina
9. handler_config: /home/serkov/docking/dockingfactory/ZINC/smina_zinc.txt
10.input_path: /home/serkov/docking/dockingfactory/ZINC/viva_VFVS_100
11.receptor: /home/serkov/docking/dockingfactory/ZINC/receptor/AR_5JJ_Bside_protonated.pdbqt
12.output_folder: /home/serkov/docking/dockingfactory/ZINC/zinc_out
13.csv_out: /home/serkov/docking/dockingfactory/ZINC/ZINC_out.csv
14.failed_ligand_out: /home/serkov/docking/dockingfactory/ZINC/ZINC_failed.csv
15.error_msg_out: /home/serkov/docking/dockingfactory/ZINC/ZINC_errors.txt
```
Please note that output_folder must exist and be empty and csv_out file must not exist. 

**Running non-interactively** 
If you have a big set of ligands to process and you expect it is going to take a long time to complete, you may run DockingFactory non-interactively as a batch job. In this case - you don’t have to keep terminal opened which is quite convenient for a long runs.

In order to submit a batch job please prepare the config files same way as for a usual run, then execute the following command:
```
1. sbatch --output Factory.log /shared/bundle/dask/share/dockingfactory/dockingfactory_job.sh --config /absolute/path/to/config/file.yml
```
The command above will submit DockingFactory as a job to the cluster. 

You may see the status of the job by using “squeue“ command. Please note, that there is going to be multiple jobs in the output. This is normal, as dask will create separate jobs for the scheduler and each worker node. Output will be in Factory.log file ( or whatever you set it in command-line above ) that is going to be created automatically. It will be created in the folder you execute the command from.

In order to cancel the computation - please use 'scancel <job_id>' command.

Another advantage of this method is that you may submit multiple computations in parallel, just execute sbatch multiple times with different configurations or command line options.

Disadvantage of this method is an overhead on having additional c6g.medium running during the workflow computation. It costs $0.034/hr, which is roughly $0.8/day. 
