import os
import contoml

from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):
    def build(self, service_obj):
        bashrc = os.environ['HOME'] + "/" + ".bashrc"

        root = '/opt/build/github.com/Jumpscale/jsagent'

        # src = '{root}/src'.format(root=root)
        src = '/opt/go_workspace/src/github.com/Jumpscale/'
        j.system.fs.createDir(src)

        if not os.path.exists(src):
            j.do.execute(
                'mkdir %s' % src
            )

        cmd = (
            '. {bashrc} &&  cp -r {root} ' +
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

    def configure(self, service_obj):
        agentcontroller = service_obj.hrd.get('instance.agentcontroller')
        cfg = contoml.load('/opt/jumpscale7/cfg/superagent.toml')
        cfg['main']['AgentControllers'] = [agentcontroller]
        cfg['main']['Gid'] = int(service_obj.hrd.get('instance.gid'))
        cfg['main']['Nid'] = int(service_obj.hrd.get('instance.nid'))

        cfg.dump('/opt/jumpscale7/cfg/superagent.toml')
