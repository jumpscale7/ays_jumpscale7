fptrom JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()

class Actions(ActionsBase):

    def prepare(self,serviceObj):
        """
        this gets executed before the files are downloaded & installed on approprate spots
        """

        if j.do.TYPE.lower().startswith("ubuntu64"):
            j.system.platform.ubuntu.downloadInstallDebPkg("http://apt-ovs.cloudfounders.com/alpha/arakoon_1.8.6_amd64.deb",minspeed=50)

        return True

