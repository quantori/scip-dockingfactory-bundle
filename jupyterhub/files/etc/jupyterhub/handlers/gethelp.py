from pathlib import Path
from jupyterhub.handlers import BaseHandler

class ScipHelpHandler(BaseHandler):
    '''
    This is a handler on user actions to show SciP help page with user guides
    '''

    async def get(self):
        '''
        Compose table of content for SciP user guides that are located in a specified
        directory and load content of these user guides to render HTML page.
        '''
        guides = []
        toc = []

        basedir = Path(
            self.config.Scip.get('user_guides', '/shared/bundle/docs')
        )
        for idx, path in enumerate(basedir.rglob('*.*')):
            title = path.relative_to(basedir).with_suffix('')
            toc.append((str(idx), title))
            guide_body = ''
            with path.open() as guide:
                guide_lines = guide.readlines()
                for i in guide_lines:
                    guide_body += i
            guides.append({'id': str(idx), 'title': title, 'body': guide_body})
        if len(guides) == 0:
            guides = [{'id': '0', 'title': '', 'body': 'There will be a user guide here'}]
        html = await self.render_template(
            'scip/guides.html',
            contents=toc,
            guides=guides
        )
        self.finish(html)
