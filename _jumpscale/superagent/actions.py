import os

from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):
    def build(self, service_obj):
        bashrc = os.environ['HOME'] + "/" + ".bashrc"

        root = '/opt/build/github.com/Jumpscale/jsagent'

        # src = '{root}/src'.format(root=root)
        src = '/opt/build/src'

        if not os.path.exists(src):
            j.do.execute(
                'mkdir %s' % src
            )

        cmd = (
            '. {bashrc} && GOPATH=$GOPATH:/opt/build/ && cp -r {root} ' +
            '{src}/ && cd {src}/jsagent && godep get ' +
            '&& go build superagent.go && ' +
            'cp {src}/jsagent/superagent {src}/jsagent/agent.toml ' +
            '/opt/code/git/binary/superagent'
        ).format(bashrc=bashrc, root=root, src=src)

        j.do.execute(cmd)
        j.do.pushGitRepos(
            message='superagent new build',
            name='superagent',
            account='binary'
        )
