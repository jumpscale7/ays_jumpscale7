from JumpScale import j
ActionsBase=j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def configure(self,serviceObj):
        """
        will install create a docker container
        """

        def createContainer():
            j.tools.docker.create(name="$(instance.param.name)",base="$(instance.param.image)", ports="$(instance.param.portsforwards)", vols="$(instance.param.volumes)")

        j.actions.start(name="create container",description='create a docker container', action=createContainer, stdOutput=True, serviceObj=serviceObj)


    def removedata(self,serviceObj):
        """
        delete docker container
        """
        j.tools.docker.destroy("$(instance.param.name)")
        return True

    def execute(self,serviceObj,cmd):
        cl = j.tools.docker.getSSH("$(instance.param.name)")
        cl.run(cmd)


    def upload(self, serviceObj,source,dest):
        sshkey,_ = self._getSSHKey(serviceObj)

        ip = serviceObj.hrd.get("instance.ip")
        port = serviceObj.hrd.get("instance.ssh.port")
        dest = "%s:%s" % (ip,dest)
        self._rsync(source,dest,sshkey,port)

    def download(self, serviceObj,source,dest):
        sshkey,_ = self._getSSHKey(serviceObj)

        ip = serviceObj.hrd.get("instance.ip")
        port = serviceObj.hrd.get("instance.ssh.port")
        source = "%s:%s" % (ip,source)
        self._rsync(source,dest,sshkey,port)

    def _getSSHKey(self,serviceObj):
        keyname = serviceObj.hrd.get("instance.sshkey")
        if keyname != "":
            sshkeyHRD = j.application.getAppInstanceHRD("sshkey",keyname)
            return (sshkeyHRD.get("instance.key.priv"),sshkeyHRD.get("instance.key.pub"))
        else:
            return (None,None)

    def _getSSHClient(self,serviceObj):
        c = j.remote.cuisine

        ip = serviceObj.hrd.get('instance.ip')
        port = serviceObj.hrd.get('instance.ssh.port')
        login = serviceObj.hrd.get('instance.login', default='')
        password = serviceObj.hrd.get('instance.password', default='')
        priv,_ = self._getSSHKey(serviceObj)
        if priv:
            c.fabric.env["key"] = priv

        if password == "" and priv == None:
            raise RuntimeError("can't connect to the node, should provide or password or a key to connect")
        return c.connect(ip,port,passwd=password)
