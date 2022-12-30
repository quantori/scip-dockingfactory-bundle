from jupyterhub.handlers import BaseHandler
from jupyterhub.utils import url_path_join, maybe_future
from tornado import web


class SaveSpawnerHandler(BaseHandler):
    """Handle spawner configuration saving without initializing spawn process

    POST handles form submission.
    """

    @web.authenticated
    async def post(self, for_user=None, server_name=''):
        """POST saves spawner user-specified options without starting server"""
        user = current_user = self.current_user
        if for_user is not None and for_user != user.name:
            if not user.admin:
                raise web.HTTPError(
                    403, "Only admins can spawn on behalf of other users"
                )
            user = self.find_user(for_user)
            if user is None:
                raise web.HTTPError(404, "No such user: %s" % for_user)

        spawner = user.spawners[server_name]

        if spawner.ready:
            raise web.HTTPError(400, "%s is already running" % (spawner._log_name))
        elif spawner.pending:
            raise web.HTTPError(
                400, "%s is pending %s" % (spawner._log_name, spawner.pending)
            )

        form_options = {}
        for key, byte_list in self.request.body_arguments.items():
            form_options[key] = [bs.decode('utf8') for bs in byte_list]
        for key, byte_list in self.request.files.items():
            form_options["%s_file" % key] = byte_list

        options = await maybe_future(spawner.options_from_form(form_options))
        spawner.orm_spawner.user_options = options
        spawner.orm_spawner.state = spawner.get_state()
        self.db.commit()

        if current_user is user:
            self.set_login_cookie(user)
        next_url = self.get_next_url(
            user,
            default=url_path_join(
                self.hub.base_url, "home"
            ),
        )
        self.redirect(next_url)
