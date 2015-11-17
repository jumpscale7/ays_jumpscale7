from JumpScale import j

ActionsBase=j.atyourservice.getActionsBaseClass()

class Actions(ActionsBase):
    """
    """
    def configure(self, serviceObj):
        # do not use framework to install python-pip
        # PYTHONPATH environment need to be cleared otherwise setup
        # will fail
        j.do.execute('PYTHONPATH="" apt-get install python-pip')
        j.do.execute('pip install raven')
