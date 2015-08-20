from JumpScale import j
import JumpScale.baselib.remote.cuisine
from JumpScale.baselib.atyourservice.ActionsBaseNode import ActionsBaseNode

class Actions(ActionsBaseNode):

    def configure(self, serviceObj):
        """
        will install a node over ssh
        """

        cl = self.getSSHClient(serviceObj)

        def pushkey():
            """
            will install the key on the node if not already present
            """
            priv, pub = self.getSSHKey(serviceObj)

            if pub:
                login = serviceObj.hrd.get('instance.login', 'root')
                cl.ssh_authorize(login, pub)
        j.actions.start(name="pushkey", description='pushkey',
                        action=pushkey, stdOutput=True, serviceObj=serviceObj)

        # only do the rest if we want to install jumpscale
        if serviceObj.hrd.getBool('instance.param.jumpscale'):
            self.isntallJumpscale(serviceObj)

        return True