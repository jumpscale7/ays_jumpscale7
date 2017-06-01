from JumpScale import j
ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def prepare(self, serviceObj):
        caddy_url = 'https://caddyserver.com/download/linux/amd64'
        dest = '/tmp/caddy_linux_amd64.tar.gz'
        j.do.createDir('/opt/caddy')
        j.system.net.downloadIfNonExistent(caddy_url, dest)
        j.do.createDir('/tmp/caddy')
        j.system.fs.targzUncompress(dest, '/tmp/caddy')
        j.system.fs.copyFile('/tmp/caddy/caddy', '/opt/caddy')
        j.system.fs.writeFile('/opt/caddy/Caddyfile', '''localhost:80 {
    proxy / localhost:82
}''')
