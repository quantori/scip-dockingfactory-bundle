import datetime
from typing import List

from pydantic import BaseModel, validator

from batchspawner.utils import get_cost, get_instance_types_options


class Job(BaseModel):
    job_id: str
    user_id: int
    name: str
    job_state: str
    standard_output: str
    features: str  # instance_type
    partition: str  # compute or compute-gpu
    start_time: int
    end_time: int = None
    instance_type: str = ''
    nodes: str
    total_time: str = None
    cost: str = ''

    @validator('standard_output')
    def format_standard_output(cls, v, values):
        # need to format with job id
        v = v.replace('%j', values['job_id'])
        return v

    @validator('instance_type', always=True)
    def get_instance_type(cls, v, values):
        options = get_instance_types_options()[values["features"]]
        return options.get('instance_type', '')

    @validator('total_time', always=True)
    def get_total_time(cls, v, values):
        state = values['job_state']
        start = datetime.datetime.fromtimestamp(values['start_time'])
        if state in ['RUNNING', 'CONFIGURING']:
            end = datetime.datetime.now()
        else:
            end = datetime.datetime.fromtimestamp(values['end_time'])
        return str(end - start).split('.', 2)[0]

    @validator('cost', always=True)
    def calculate_cost(cls, v, values):
        """
        Updates cost of jobs
        """
        instance_type = values['features']
        state = values['job_state']
        start = datetime.datetime.fromtimestamp(values['start_time'])
        if state in ['RUNNING', 'CONFIGURING']:
            end = datetime.datetime.now()
        else:
            end = datetime.datetime.fromtimestamp(values['end_time'])
        cost = get_cost(instance_type, start, end)
        return cost


class JobsResponse(BaseModel):
    jobs: List[Job]




