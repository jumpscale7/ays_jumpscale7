from JumpScale import j
import time
ActionsBase=j.atyourservice.getActionsBaseClass()

class Actions(ActionsBase):

    def prepare(self, serviceObj):
        j.do.execute('apt-get install -y libgd3')

        #hack for sandboxed nginx to start properly
        j.system.fs.createDir(j.system.fs.joinPaths('/var', 'lib', 'nginx'))
        # make sur required log directory exists
        logPath = j.system.fs.joinPaths('/var', 'log', 'nginx')
        if not j.system.fs.exists(logPath):
            j.system.fs.createDir(logPath)

    def stop(self, serviceObj):
        if not j.system.fs.isDir('/opt/nginx'):
            return
        j.system.process.execute('cd /opt/nginx && ./nginx -c /opt/nginx/cfg/nginx.conf -s quit')
