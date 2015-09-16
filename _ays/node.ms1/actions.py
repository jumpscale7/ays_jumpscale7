from JumpScale import j

ActionsBase=j.atyourservice.getActionsBaseClass()

import JumpScale.lib.ms1
import JumpScale.baselib.remote.cuisine
from JumpScale.baselib.atyourservice.ActionsBaseNode import ActionsBaseNode

class Actions(ActionsBaseNode):

    def _getSpaceSecret(self, serviceObj):
        ms1client_hrd = j.application.getAppInstanceHRD("ms1_client","$(instance.ms1.connection)")
        spacesecret = ms1client_hrd.get("instance.param.secret", '')
        if True or spacesecret == '':
            ms1Service = j.atyourservice.get(name='ms1_client', instance="$(instance.ms1.connection)")
            ms1Service.configure()
            spacesecret = ms1Service.hrd.get("instance.param.secret")
            if spacesecret == '':
                j.events.opserror_critical('impossible to retreive ms1 space secret', category='atyourservice')
        return spacesecret

    def getCoudClient(self):
        ms1client_hrd = j.application.getAppInstanceHRD("ms1_client","$(instance.ms1.connection)")
        return j.tools.ms1.get(ms1client_hrd.get('instance.param.apiurl'))

    def configure(self, serviceObj):
        """
        create a vm on ms1
        """
        def createmachine():
            cloudCl = self.getCoudClient()
            spacesecret = self._getSpaceSecret(serviceObj)
            _, sshkey = self.getSSHKey(serviceObj)

            machineid, ip, port = cloudCl.createMachine(spacesecret, "$(instance.name)", memsize="$(instance.memsize)", \
                ssdsize=$(instance.ssdsize), vsansize=0, description='',imagename="$(instance.imagename)",delete=False, sshkey=sshkey)

            serviceObj.hrd.set("instance.machine.id",machineid)
            serviceObj.hrd.set("instance.ip",ip)
            serviceObj.hrd.set("instance.ssh.port",port)

        j.actions.start(retry=1, name="createmachine", description='createmachine', cmds='', action=createmachine, \
                        actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, serviceObj=serviceObj)

        # only do the rest if we want to install jumpscale
        if serviceObj.hrd.getBool('instance.jumpscale'):
            self.installJumpscale(serviceObj)

    def removedata(self, serviceObj):
        """
        delete vmachine
        """
        ms1client_hrd = j.application.getAppInstanceHRD("ms1_client","$(instance.ms1.connection)")
        spacesecret = ms1client_hrd.get("instance.param.secret")
        cloudCl = self.getCoudClient()
        cloudCl.deleteMachine(spacesecret, "$(instance.name)")

        return True

    def start(self, serviceObj):
        if serviceObj.hrd.get('instance.machine.id', '') != '':
            cloudCl = self.getCoudClient()
            spacesecret = self._getSpaceSecret(serviceObj)
            cloudCl.startMachine(spacesecret, serviceObj.hrd.getStr('instance.name'))

    def stop(self, serviceObj):
        if serviceObj.hrd.get('instance.machine.id') != '':
            cloudCl = self.getCoudClient()
            spacesecret = self._getSpaceSecret(serviceObj)
            cloudCl.stopMachine(spacesecret, serviceObj.hrd.getStr('instance.name'))