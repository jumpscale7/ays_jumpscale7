import contoml

from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):
    def build(self, service_obj):
        j.system.platform.ubuntu.install('mercurial')

        package = 'github.com/Jumpscale/jsagent'
        # build package
        go = j.atyourservice.get(name='go')
        go.actions.buildProjet(go, package=package)

        # path to bin and config
        gopath = go.hrd.getStr('instance.gopath')
        bin_path = j.system.fs.joinPaths(gopath, 'bin', 'jsagent')
        cfg_path = j.system.fs.joinPaths(gopath, 'src', package, 'agent.toml')
        ext_path = j.system.fs.joinPaths(gopath, 'src', package, 'extensions')

        # move bin to the binary repo
        bin_repo = '/opt/code/git/binary/superagent/'
        for f in j.system.fs.listFilesInDir(bin_repo):
            j.system.fs.remove(f)
        j.system.fs.copyFile(bin_path, j.system.fs.joinPaths(bin_repo, 'superagent'))
        j.system.fs.copyFile(cfg_path, bin_repo)
        j.system.fs.copyDirTree(ext_path, j.system.fs.joinPaths(bin_repo, 'extensions'))

        # upload bin to gitlab
        j.do.pushGitRepos(
            message='superagent new build',
            name='superagent',
            account='binary'
        )

    def configure(self, service_obj):
        agentcontroller = service_obj.hrd.get('instance.agentcontroller')
        cfg_path = j.system.fs.joinPaths(j.dirs.baseDir, 'apps/superagent/superagent.toml')
        cfg = contoml.load(cfg_path)
        cfg['controllers']['main']['url'] = agentcontroller
        cfg['main']['gid'] = int(service_obj.hrd.get('instance.gid'))
        cfg['main']['nid'] = int(service_obj.hrd.get('instance.nid'))

        cfg.dump(cfg_path)
