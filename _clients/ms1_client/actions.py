from JumpScale import j

ActionsBase=j.packages.getActionsBaseClass()

class Actions(ActionsBase):

    """
    """


    def configure(self,serviceObj):
        """
        configure ms1
        """
        import JumpScale.lib.ms1

        secret=j.tools.ms1.getCloudspaceSecret("$(param.login)","$(param.passwd)","$(param.cloudspace)","$(param.location)")

        #this remembers the secret required to use ms1
        serviceObj.hrd.set("param.secret",secret)

        return True

