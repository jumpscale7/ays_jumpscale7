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
        package = 'github.com/Jumpscale/jsagentcontroller'
        # build package
        go = j.atyourservice.get(name='go')
        go.actions.buildProjet(go, package=package)

        # path to bin and config
        gopath = go.hrd.getStr('instance.gopath')
        bin_path = j.system.fs.joinPaths(gopath, 'bin', 'jsagentcontroller')
        cfg_path = j.system.fs.joinPaths(gopath, 'src', package, 'agentcontroller.toml')
        handlers_path = j.system.fs.joinPaths(gopath, 'src', package, 'handlers')
        client_path = j.system.fs.joinPaths(gopath, 'src', package, 'client')

        # move bin to the binary repo
        bin_repo = '/opt/code/git/binary/jsagentcontroller_go/'
        for f in j.system.fs.listFilesInDir(bin_repo):
            j.system.fs.remove(f)

        j.system.fs.copyFile(bin_path, bin_repo)
        j.system.fs.copyFile(cfg_path, bin_repo)
        j.system.fs.copyDirTree(handlers_path, j.system.fs.joinPaths(bin_repo, 'handlers'))
        j.system.fs.copyDirTree(client_path, j.system.fs.joinPaths(bin_repo, 'client'))

        # upload bin to gitlab
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

        toml = '/opt/jumpscale7/apps/jsagentcontroller_go/agentcontroller.toml'
        cfg = contoml.load(toml)
        cfg['main']['listen'] = service_obj.hrd.get('instance.param.webservice.host')
        cfg['main']['redis_host'] = service_obj.hrd.get('instance.param.redis.host')
        cfg['main']['redis_password'] = service_obj.hrd.get('instance.param.redis.password')

        cfg.dump(toml)
