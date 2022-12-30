import json
import os
from collections import defaultdict
from types import SimpleNamespace

from dask_gateway_server.options import Options, String


def get_cluster_config():
    cluster_config_path = os.environ.get('PCLUSTER_CONFIG_PATH', '/opt/parallelcluster/configs/cluster_config.json')
    with open(cluster_config_path) as f_pcluster_config:
        cluster_config = json.loads(f_pcluster_config.read(), object_hook=lambda d: SimpleNamespace(**d))
    instance_types = defaultdict()
    # TODO: fix a problem when one instance type belongs different SLURM queues;
    for queue, queue_config in cluster_config.cluster.queue_settings.__dict__.items():
        for cpu, cpu_config in queue_config.compute_resource_settings.__dict__.items():
            instance_types[cpu_config.instance_type] = {
                'queue': queue,
                'cpu': cpu,
                'vcpu': cpu_config.vcpus,
                'gpus': cpu_config.gpus,
            }
    return instance_types


# Configure the gateway to use SLURM
c.DaskGateway.backend_class = (
    "dask_gateway_server.backends.jobqueue.slurm.SlurmBackend"
)


def options_handler(options):

    # always use python_env as a default
    setup = "source %s/bin/activate " % options.python_env

    if options.conda_env:
        setup = "source /shared/bundle/anaconda3/etc/profile.d/conda.sh && conda activate %s" % options.conda_env

    cluster_config = get_cluster_config()
    worker_instance_type_options = cluster_config[options.worker_instance_type]
    scheduler_instance_type_options = cluster_config[options.scheduler_instance_type]

    partition = worker_instance_type_options['queue']
    scheduler_partition = scheduler_instance_type_options['queue']

    return {
        "partition": partition,
        "scheduler_partition": scheduler_partition,
        "constraint": options.worker_instance_type,
        "scheduler_constraint": options.scheduler_instance_type,
        "worker_cores": worker_instance_type_options['vcpu'],
        "scheduler_cores": scheduler_instance_type_options['vcpu'],
        "worker_setup": setup,
        "scheduler_setup": setup,
        "worker_memory": str(worker_instance_type_options['vcpu']*2)+" G"
    }

c.Backend.cluster_options = Options(

    String("conda_env", label="Conda Environment"),
    String("python_env", default="/shared/bundle/dask", label="Python Virtual Environment"),
    String("worker_instance_type", label="Worker Instance Type", default="c5.large"),
    String("scheduler_instance_type", label="Scheduler Instance Type", default="c5.large"),
    #String("partition", label="Worker Partition", default="compute"),
    #String("scheduler_partition", label="Scheduler Partition", default="compute"),
    handler=options_handler,
)

c.SlurmBackend.cluster_start_timeout = 600
c.SlurmBackend.worker_start_timeout = 600

# Configure the paths to the dask-scheduler/dask-worker CLIs
c.JobQueueClusterConfig.scheduler_cmd = "dask-scheduler"
c.JobQueueClusterConfig.worker_cmd = "dask-worker"
