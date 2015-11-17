from JumpScale import j

ActionsBase=j.atyourservice.getActionsBaseClass()

class Actions(ActionsBase):
    """
    """
    def configure(self, serviceObj):
        j.do.execute('pip install raven')
