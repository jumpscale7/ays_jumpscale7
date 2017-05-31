from JumpScale import j
ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def install(self, serviceObj):
        caddy_url = 'https://caddyserver.com/download/linux/amd64'
        dest = '/opt/caddy/caddy_linux_amd64.tar.gz'
        j.do.createDir('/opt/caddy')
        j.do.execute('wget {} -O {}'.format(caddy_url, dest))
        j.do.execute('tar -xvf {}'.format(dest))
