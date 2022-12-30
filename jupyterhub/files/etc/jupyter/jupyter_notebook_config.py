c.ServerProxy.https = True
c.ServerProxy.servers = {
  'Desktop': {
    'command': ['/shared/bundle/extras/launch_dcv_session.sh','{port}'],
    'absolute_url': False,
    'timeout' : 15,
    'launcher_entry': {
      'title' : 'Desktop ( Nice DCV )',
      'icon_path' : '/shared/bundle/extras/desktop-computer.svg' 
    }
  }
}

c.LauncherShortcuts.shortcuts = {
    'nicedcv-webui': {
        'title': 'NiceDCV Desktop',
        'target': '/dcv/sessions{base_url}?redirects=1',
        'icon_path': '/shared/bundle/extras/dcv-desktop.svg'
    }
}
