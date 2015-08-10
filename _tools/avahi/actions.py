from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def configure(self, serviceObj):
        j.remote.avahi.registerService(servicename='$(instance.name)',
                                       port='$(instance.port)',
                                       type='$(instance.type)')

    def removedata(self, serviceObj):
        j.remote.avahi.removeService(servicename='$(instance.name)')
