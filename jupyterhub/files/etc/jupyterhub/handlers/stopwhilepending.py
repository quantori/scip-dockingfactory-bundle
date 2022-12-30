from jupyterhub.handlers import BaseHandler
from tornado import web


class StopServerHandler(BaseHandler):
    """Handle stop server while it's pending

    POST handles form submission.
    """

    @web.authenticated
    async def post(self):
        """POST takes info about user and server we want to stop"""
        user = self.current_user
        server_name = str(self.get_body_argument("server_name"))
        for_user = str(self.get_body_argument("for_user"))
        if for_user is not None and for_user != user.name:
            if not user.admin:
                raise web.HTTPError(
                    403, "Only admins can spawn on behalf of other users"
                )
            user = self.find_user(for_user)
            if user is None:
                raise web.HTTPError(404, "No such user: %s" % for_user)

        spawner = user.spawners[server_name]
        spawner._spawn_pending = False

