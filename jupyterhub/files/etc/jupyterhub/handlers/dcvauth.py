import socket
import uuid

from collections import namedtuple
from datetime import datetime, timedelta
from jupyterhub.handlers import BaseHandler
from tornado import web


DcvSession = namedtuple('DcvSession', ['uid', 'owner', 'token'])


DcvToken = namedtuple('DcvToken', ['id', 'username', 'expired'])


DCV_SESSIONS=dict()

class DcvSessionHandler(BaseHandler):
    """Handle stop server while it's pending

    POST handles form submission.
    """


    def initialize(self, sessions=DCV_SESSIONS):
            self._dcv_cache = sessions

    @web.authenticated
    async def get(self, prefix, username, notebook):
        session_id = self.get_argument('sessionId', str(uuid.uuid4().hex))
        life_time = self.get_argument('tokenLifeTime', 180)

        owner = self.current_user
        spawner = owner.spawners.get(notebook)
        dcv_url = 'dcv-server:8443'
        if spawner:
            dcv_url = '{}:8443'.format(socket.gethostbyname(spawner.server.ip))
        session = self._dcv_cache.get(
            session_id,
            DcvSession(session_id, owner.name, None)
        )

        if session.token is None or session.token.expired < datetime.now():
            session = DcvSession(
                session.uid,
                session.owner,
                DcvToken(
                    str(uuid.uuid4().hex),
                    username = self.current_user.name,
                    expired = datetime.now() + timedelta(seconds=life_time)
                )
            )
        self._dcv_cache[session.uid] = session
        self.finish('https://{}/?authToken={}#{}'.format(dcv_url, session.token.id, session.uid))



class DcvAuthHandler(BaseHandler):
    """
    Implement external authenicator for NiceDCV server

    POST handles form submission.
    """

    NO_AUTH_BODY='<auth result="no"/>'

    def initialize(self, sessions=DCV_SESSIONS):
            self._dcv_cache = sessions

    async def post(self):
        """POST determines whether the given token is valid"""
        token_id = self.get_argument('authenticationToken', '')
        session_id = self.get_argument('sessionId', '')
        client_addr = self.get_argument('clientAddress', '')
        try:
            session = self._dcv_cache[session_id]
            if session.token.id == token_id and session.token.expired > datetime.now():
                self.finish('<auth result="yes"><username>{}</username></auth>'.format(session.owner))
            else:
              self.finish(self.NO_AUTH_BODY)
        except KeyError:
            self.finish(self.NO_AUTH_BODY)
