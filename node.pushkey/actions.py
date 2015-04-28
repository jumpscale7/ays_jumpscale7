from JumpScale import j
ActionsBase=j.atyourservice.getActionsBaseClass()


import JumpScale.baselib.remote.cuisine

class Actions(ActionsBase):

    def removedata(self,serviceObj):
        """
        delete sshkey from authorized_keys file one the remote node
        """
        sshkey = self._getSSHKey(serviceObj)
        cl = self._getSSHClient(serviceObj)
        cmd = "echo '%s' >> ~/.ssh/authorized_keys" % sshkey.get('instance.key.pub')
        cl.run(cmd)
        return True

    def execute(self,serviceObj,cmd):
        """
        add the public key to ~/.ssh/authorized_keys on the remote node
        """
        sshkey = self._getSSHKey(serviceObj)
        cl = self._getSSHClient(serviceObj)
        cmd = "echo '%s' >> ~/.ssh/authorized_keys" % sshkey.get('instance.key.pub')
        cl.run(cmd)

    def _getSSHClient(self,serviceObj):
        c = j.remote.cuisine
        ip = serviceObj.hrd.get('instance.ip')
        port = serviceObj.hrd.get('instance.ssh.port')
        password = serviceObj.hrd.get('instance.password')
        return c.connect(ip,port,password)

    def _getSSHKey(self,serviceObj):
        keyname = serviceObj.hrd.get("instance.sshkey")
        sshkeyHRD = j.application.getAppInstanceHRD("sshkey",keyname)
        return sshkeyHRD
        # sshkey = sshkeyHRD.get("instance.key.priv")
        # return sshkey