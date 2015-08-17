from JumpScale import j
import time

ActionsBase=j.atyourservice.getActionsBaseClass()

class Actions(ActionsBase):
    def prepare(self, serviceobj):
        print "Installing nodejs & npm"
        print "To run nodejs, run /opt/nodejs/bin/node"
        print "To run npm, run /opt/nodejs/bin/npm"
        
    def configure(self, serviceobj):
        j.system.fs.symlink('/opt/nodejs/lib/node_modules/npm/bin/npm-cli.js','/opt/nodejs/bin/npm',True)
        j.system.fs.symlink('/opt/nodejs/bin/node','/usr/local/bin/node',True)
        j.system.fs.symlink('/opt/nodejs/lib/node_modules/npm/bin/npm-cli.js','/usr/local/bin/npm',True)


