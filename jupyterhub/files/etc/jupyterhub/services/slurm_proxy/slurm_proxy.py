import json
import os
import secrets

from functools import wraps

from flask import Flask, request, Response, abort, redirect, make_response, session

from jupyterhub.services.auth import HubOAuth
from models import JobsResponse
from services import SlurmAPI

prefix = os.environ.get('JUPYTERHUB_SERVICE_PREFIX', '/')

auth = HubOAuth(api_token=os.environ['JUPYTERHUB_API_TOKEN'], cache_max_age=60)

app = Flask('slurm_proxy')
app.secret_key = secrets.token_bytes(32)

def authenticated(f):
    """Decorator for authenticating with the Hub"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = session.get("token")
        if token:
            user = auth.user_for_token(token)
        else:
            user = None
        if user:
            return f(user, *args, **kwargs)
        else:
            state = auth.generate_state(next_url=request.host_url)
            response = make_response(redirect(auth.login_url + '&state=%s' % state))
            response.set_cookie(auth.state_cookie_name, state)
            return response
    return decorated


@app.route(prefix)
@authenticated
def home(user):
    return Response(
        json.dumps(user, indent=1, sort_keys=True), mimetype='application/json')

@app.route(prefix + 'oauth_callback')
def oauth_callback():
    code = request.args.get('code', None)
    if code is None:
        return 403
    # validate state field
    arg_state = request.args.get('state', None)
    cookie_state = request.cookies.get(auth.state_cookie_name)
    if arg_state is None or arg_state != cookie_state:
        # state doesn't match
        return 403

    token = auth.token_for_code(code)
    # store token in session cookie
    session["token"] = token
    next_url = auth.get_next_url(cookie_state) or prefix
    response = make_response(redirect(next_url))
    return response

@app.route(prefix + '/api/jobs/')
@authenticated
def get_jobs(user):
    slurm_api = SlurmAPI(user)
    jobs = slurm_api.get_slurm_jobs_list()
    response = JobsResponse(jobs=jobs)
    return response.dict()


@app.route(prefix + '/api/jobs/<job_id>/log/')
@authenticated
def get_job_logs(user, job_id):
    slurm_api = SlurmAPI(user)
    job = slurm_api.get_job_stdout_log(job_id)
    return job


@app.route(prefix + '/api/jobs/<job_id>/', methods=['GET', 'DELETE'])
@authenticated
def get_job(user, job_id):
    slurm_api = SlurmAPI(user)
    if request.method == 'DELETE':
        return slurm_api.delete_job(job_id)
    job = slurm_api.get_job_or_404(job_id)
    return job.dict()


if __name__ == '__main__':
    print('Starting SlurmProxy service..........')
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
