from JumpScale import j
ActionsBase=j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def configure(self,serviceObj):
        """
        will install create a docker container
        """

        def createContainer():
            j.tools.docker.create(name="$(instance.param.name)",base="$(instance.param.image)", ports="$(instance.param.portsforwards)", vols="$(instance.param.volumes)")

        j.actions.start(name="create container", description='create a docker container', action=createContainer, stdOutput=True, serviceObj=serviceObj)

        def installJumpscale():
            self.execute(self, "curl https://raw.githubusercontent.com/Jumpscale/jumpscale_core7/master/install/install_python_web.sh > /tmp/js7.sh && bash /tmp/js7.sh")
        j.actions.start(name="install jumpscale", description='install Jumpscale', action=installJumpscale, stdOutput=True, serviceObj=serviceObj)

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

    def start(self,serviceObj):
        j.tools.docker.restart('$(instance.param.name)')

    def stop(self,serviceObj):
        j.tools.docker.stop('$(instance.param.name)')

    def download(self, serviceObj,source,dest):
        raise NotImplemented("Download is not implemented")
