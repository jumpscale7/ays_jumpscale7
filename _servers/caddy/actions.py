from JumpScale import j
ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def prepare(self, serviceObj):
        caddy_url = 'https://caddyserver.com/download/linux/amd64'
        dest = '/tmp/caddy_linux_amd64.tar.gz'
        j.do.createDir('/opt/caddy')
        j.system.net.downloadIfNonExistent(caddy_url, dest)
        j.system.fs.targzUncompress(dest, '/opt/caddy')
