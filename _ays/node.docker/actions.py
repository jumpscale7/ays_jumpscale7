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
        cmd = cmd or ""
        cmd = "bash -c \"%s\"" % (cmd.replace('"', '\"'))
        j.tools.docker.run("$(instance.param.name)", cmd)

    def upload(self, serviceObj,source,dest):
        j.tools.docker.copy("$(instance.param.name)", source, dest)

    def download(self, serviceObj,source,dest):
        raise NotImplemented("Download is not implemented")
