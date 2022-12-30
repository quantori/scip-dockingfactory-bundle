import os
import time

import requests
from flask import abort
from jwt import JWT
from jwt.jwk import jwk_from_dict
from jwt.utils import b64encode
from loguru import logger

from models import Job
from cachetools.func import ttl_cache
from batchspawner.utils import get_username

LOCAL_ENV = os.environ.get('ENVIRONMENT', 'production') == 'local'


class SlurmAPI:
    API_URL = os.environ.get('SLURM_API_URL', 'http://localhost:6800/slurm/v0.0.36/')
    SLURM_KEY = os.environ.get('SLURM_KEY', '/opt/slurm/etc/jwt_hs256.key')

    def __init__(self, user):
        self.session = requests.Session()
        self.user = user

    @ttl_cache(maxsize=1, ttl=60*60)
    def get_token(self):
        with open(self.SLURM_KEY, "rb") as f:
            private_key = f.read()
        signing_key = jwk_from_dict({
            'kty': 'oct',
            'k': b64encode(private_key)
        })

        message = {
            "exp": int(time.time() + 60*60),
            "iat": int(time.time()),
            "sun": self.user['name']
        }
        a = JWT()
        compact_jws = a.encode(message, signing_key, alg='HS256')
        return compact_jws

    def get_request_headers(self):
        headers = {
            'X-SLURM-USER-NAME': self.user['name'],
            'X-SLURM-USER-TOKEN': self.get_token()
        }
        return headers

    def get_slurm_jobs_list(self):
        r = self.session.get(self.API_URL + 'jobs', headers=self.get_request_headers())
        jobs = r.json()['jobs']
        jobs = [Job(**j) for j in jobs]
        result = []
        for job in jobs:
            # TODO now all api calls are performed by root, so for now we filter jobs in python
            job_user_name = get_username(job.user_id)
            if self.user['name'] != job_user_name:  # filter jobs by current JH user
                continue
            result.append(job)
        return result

    def get_job_by_id(self, job_id: str):
        r = self.session.get(self.API_URL + f'job/{job_id}', headers=self.get_request_headers())
        result = r.json()
        if result['jobs']:
            job = Job(**result['jobs'][0])
            # filter by current user
            job_user_name = get_username(job.user_id)
            if job_user_name != self.user['name']:
                return None
            return job
        return None

    def get_job_or_404(self, job_id: str):
        job = self.get_job_by_id(job_id)
        if not job:
            abort(404)
        return job

    def get_job_stdout_log(self, job_id: str):
        job = self.get_job_or_404(job_id)
        try:
            with open(job.standard_output, 'r') as f:
                return f'<pre>{f.read()}</pre>'
        except FileNotFoundError:
            logger.info(f'File not found {job.standard_output}')
            abort(404)

    def delete_job(self, job_id: str):
        r = self.session.delete(self.API_URL + f'job/{job_id}', headers=self.get_request_headers())
        if r.status_code == 200:
            return {'job_id': job_id, 'status': 'deleted'}
        abort(404)
