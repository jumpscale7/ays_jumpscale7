from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def configure(self, serviceObj):
        prefix = "whoami.git.%s" % "$(instance.git.client.host)"
        data = {
            'host': '$(instance.git.client.host)',
            'login': '$(instance.git.client.login)',
            'passwd': '$(instance.git.client.passwd)'
        }
        hrd = j.core.hrd.get('/opt/jumpscale7/hrd/system/whoami.hrd')
        hrd.set(prefix, data)
        hrd.save()
