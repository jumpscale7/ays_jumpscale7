from JumpScale import j

ActionsBase=j.atyourservice.getActionsBaseClass()

class Actions(ActionsBase):

    def configure(self,serviceObj):
        """
        will create a new virtual machine
        """
        def createVM():
            j.system.platform.kvm.create("$(instance.param.name)","$(instance.param.baseimage)")

        j.actions.start(retry=2, name="create vm",description='create a virtual machine ($(instance.param.baseimage))', action=createVM, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, serviceObj=serviceObj)

        def getconfig():
            config = j.system.platform.kvm.getConfig("$(instance.param.name)")
            serviceObj.hrd.set("instance.machine.ssh.ip",config.get("bootstrap.ip"))
            serviceObj.hrd.set("instance.machine.ssh.login",config.get("bootstrap.login"))
            serviceObj.hrd.set("instance.machine.ssh.passwd",config.get("bootstrap.passwd"))

        j.actions.start(retry=2, name="get config",description='retreive information about the vm', action=getconfig, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, serviceObj=serviceObj)
        return True


    def removedata(self,serviceObj):
        """
        delete vmachine
        """
        def destroyvm():
            j.system.platform.kvm.destroy("$(instance.param.name)")

        j.actions.start(retry=2, name="destroy vm",description='destroy the virtual machine', action=destroyvm, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, serviceObj=serviceObj)

        return True

    def execute(self,serviceObj,cmd):
        """
        execute over ssh something onto the machine
        """
        j.system.platform.kvm.execute(name="$(instance.param.name)", cmd=cmd)
        return True

    def start(self,serviceObj):
        j.system.platform.kvm.start("$(instance.param.name)")
        return True

    def stop(self,serviceObj):
        j.system.platform.kvm.stop("$(instance.param.name)")
        return True