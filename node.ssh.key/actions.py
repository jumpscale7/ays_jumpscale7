from JumpScale import j
ActionsBase=j.atyourservice.getActionsBaseClass()


import JumpScale.baselib.remote.cuisine

class Actions(ActionsBase):

    def configure(self,serviceObj):
        """
        will install a node over ssh
        """
        cl = self._getSSHClient(serviceObj)
        def update():
            cl.run("apt-get update")
            # j.do.execute("apt-get update")
        j.actions.start(name="update",description='update', action=update, stdOutput=True, serviceObj=serviceObj)

        def upgrade():
            cl.run("apt-get upgrade -y")
            # j.do.execute("apt-get upgrade -y")
        j.actions.start( name="upgrade",description='upgrade', action=upgrade, stdOutput=True, serviceObj=serviceObj)
        def extra():
            cl.run("apt-get install byobu curl -y")
            # j.do.execute("apt-get install byobu curl -y")
        j.actions.start(name="extra",description='extra', action=extra, stdOutput=True, serviceObj=serviceObj)

        def jumpscale():
            cl.run("curl https://raw.githubusercontent.com/Jumpscale/jumpscale_core7/master/install/install_python_web.sh > /tmp/installjs.sh")
            cl.run("sh /tmp/installjs.sh")
            # j.do.execute("curl https://raw.githubusercontent.com/Jumpscale/jumpscale_core7/master/install/install_python_web.sh > /tmp/installjs.sh")
            # j.do.execute("sh /tmp/installjs.sh")
        j.actions.start(name="jumpscale",description='install jumpscale', action=jumpscale, stdOutput=True, serviceObj=serviceObj)

        return True


    def removedata(self,serviceObj):
        """
        delete vmachine
        """
        j.do.execute("killall tmux;killall python;echo")
        # j.do.execute("rm -rf /opt")
        return True

    def execute(self,serviceObj,cmd):
        cl = self._getSSHClient(serviceObj)
        cl.run(cmd)


    def upload(self, serviceObj,source,dest):
        sshkey = self._getSSHKey(serviceObj)

        ip = serviceObj.hrd.get("instance.ip")
        port = serviceObj.hrd.get("instance.ssh.port")
        dest = "%s:%s" % (ip,dest)
        self._rsync(source,dest,sshkey,port)

    def download(self, serviceObj,source,dest):
        sshkey = self._getSSHKey(serviceObj)

        ip = serviceObj.hrd.get("instance.ip")
        port = serviceObj.hrd.get("instance.ssh.port")
        source = "%s:%s" % (ip,source)
        self._rsync(source,dest,sshkey,port)

    def _getSSHKey(self,serviceObj):
        keyname = serviceObj.hrd.get("instance.sshkey")
        sshkeyHRD = j.application.getAppInstanceHRD("sshkey",keyname)
        return sshkeyHRD.get("instance.key.priv")

    def _getSSHClient(self,serviceObj):
        ip = serviceObj.hrd.get('instance.ip')
        port = serviceObj.hrd.get('instance.ssh.port')
        sshkey = self._getSSHKey(serviceObj)
        c = j.remote.cuisine
        c.fabric.env["key"] = sshkey
        return c.connect(ip,port)
