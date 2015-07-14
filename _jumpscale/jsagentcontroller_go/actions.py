import os
from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):
    """
    process for install
    -------------------
    step1: prepare actions
    step2: check_requirements action
    step3: download files & copy on right location (hrd info is used)
    step4: configure action
    step5: check_uptime_local to see if process stops  (uses timeout $process.stop.timeout)
    step5b: if check uptime was true will do stop action and retry the check_uptime_local check
    step5c: if check uptime was true even after stop will do halt action and retry the check_uptime_local check
    step6: use the info in the hrd to start the application
    step7: do check_uptime_local to see if process starts
    step7b: do monitor_local to see if package healthy installed & running
    step7c: do monitor_remote to see if package healthy installed & running,
        but this time test is done from central location
    """

    def build(self, service_obj):
        bashrc = os.environ['HOME'] + "/" + ".bashrc"

        root = '/opt/build/github.com/Jumpscale/jsagentcontroller'

        # src = '{root}/src'.format(root=root)
        src = '/opt/go_workspace/src/github.com/Jumpscale/'
        j.system.fs.createDir(src)

        if not os.path.exists(src):
            j.do.execute(
                'mkdir %s' % src
            )

        cmd = (
            '. {bashrc} &&  cp -r {root} ' +
            '{src}/ && cd {src}/jsagentcontroller && godep get ' +
            '&& go build main.go && ' +
            'cp {src}/jsagentcontroller/main /opt/code/git/binary/jsagentcontroller_go/jsagentcontroller && ' +
            'cp {src}/jsagentcontroller/agentcontroller.toml ' +
            '/opt/code/git/binary/jsagentcontroller_go'
        ).format(bashrc=bashrc, root=root, src=src)

        j.do.execute(cmd)
        j.do.pushGitRepos(
            message='agentcontroller new build',
            name='jsagentcontroller_go',
            account='binary'
        )

    def configure(self, service_obj):
        import contoml
        """
        this gets executed when files are installed
        this step is used to do configuration steps to the platform
        after this step the system will try to start the jpackage if anything needs to be started
        """
        hrd = j.application.getAppInstanceHRD('redis', service_obj.hrd.get('instance.param.redis.instance'))
        redis = hrd.get('instance.param.port')

        host = service_obj.hrd.get('instance.param.webservice.host')
        toml = '/opt/jumpscale7/apps/jsagentcontroller_go/agentcontroller.toml'
        cfg = contoml.load(toml)
        cfg['main']['Listen'] = host
        cfg['main']['Redis'] = ':' + str(redis)

        cfg.dump(toml)
