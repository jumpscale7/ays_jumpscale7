from JumpScale import j
ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def configure(self, service_obj):
        """
        will install create a docker container
        """

        def createContainer():
            j.tools.docker.create(name="$(instance.param.name)", base="$(instance.param.image)",
                                  ports="$(instance.param.portsforwards)", vols="$(instance.param.volumes)")

        j.actions.start(name="create container", description='create a docker container',
                        action=createContainer, stdOutput=True, serviceObj=service_obj)

        def installJumpscale():
            self.execute(
                self,
                ("cd /tmp;rm -f install.sh;curl " +
                 "-k https://raw.githubusercontent.com/Jumpscale/jumpscale_core7/master/install/install.sh > " +
                 "install.sh;bash install.sh")
            )
        j.actions.start(name="install jumpscale", description='install Jumpscale',
                        action=installJumpscale, stdOutput=True, serviceObj=service_obj)

    def removedata(self, service_obj):
        """
        delete docker container
        """
        j.tools.docker.destroy("$(instance.param.name)")
        return True

    def execute(self, service_obj, cmd):
        ssh = j.tools.docker.getSSH("$(instance.param.name)", stdout=True)
        return ssh.run(cmd)

    def upload(self, service_obj, source, dest):
        j.tools.docker.uploadFile("$(instance.param.name)", source, dest)

    def download(self, service_obj, source, dest):
        j.tools.docker.downloadFile('$(instance.param.name)', source, dest)

    def start(self, service_obj):
        j.tools.docker.restart('$(instance.param.name)')

    def stop(self, service_obj):
        j.tools.docker.stop('$(instance.param.name)')
