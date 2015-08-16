from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def build(self, service_obj):
        root = '/opt/build/github.com/Jumpscale/jsagentcontroller'

        j.system.fs.copyDirTree(
            j.system.fs.joinPaths(root, 'client'),
            '/opt/code/git/binary/jsagentcontroller2_client'
        )

        j.do.pushGitRepos(
            message='agentcontroller2 client new build',
            name='jsagentcontroller2_client',
            account='binary'
        )
