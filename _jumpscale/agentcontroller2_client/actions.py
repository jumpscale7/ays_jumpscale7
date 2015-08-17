from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def build(self, service_obj):
        root = '/opt/build/github.com/Jumpscale/agentcontroller2'

        j.system.fs.copyDirTree(
            j.system.fs.joinPaths(root, 'client'),
            '/opt/code/git/binary/agentcontroller2_client'
        )

        j.do.pushGitRepos(
            message='agentcontroller2 client new build',
            name='agentcontroller2_client',
            account='binary'
        )
