import contoml

from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):
    def build(self, service_obj):
        j.system.platform.ubuntu.install('mercurial')

        package = 'github.com/Jumpscale/agent2'

        syncthing = '/opt/build/git.aydo.com/binary/syncthing/syncthing/syncthing'

        # build package
        go = j.atyourservice.get(name='go', parent=None)
        go.actions.buildProjectGodep(go, package='https://%s' % package, branch='production')

        # path to bin and config
        gopath = go.hrd.getStr('instance.gopath')
        bin_path = j.system.fs.joinPaths(gopath, 'bin', 'agent2')
        cfg_path = j.system.fs.joinPaths(gopath, 'src', package, 'agent.toml')
        ext_path = j.system.fs.joinPaths(gopath, 'src', package, 'extensions')
        ext_conf_path = j.system.fs.joinPaths(gopath, 'src', package, 'conf')

        # move bin to the binary repo
        bin_repo = '/opt/code/git/binary/agent2/'
        for f in j.system.fs.listFilesAndDirsInDir(bin_repo):
            if f.endswith('/.git'):
                continue
            j.system.fs.removeDirTree(f)

        j.system.fs.copyFile(bin_path, bin_repo)
        j.system.fs.copyFile(cfg_path, j.system.fs.joinPaths(bin_repo, 'agent2.toml'))
        j.system.fs.copyDirTree(ext_path, j.system.fs.joinPaths(bin_repo, 'extensions'))
        j.system.fs.copyDirTree(ext_conf_path, j.system.fs.joinPaths(bin_repo, 'conf'))

        # bundle syncthing.
        j.system.fs.createDir(j.system.fs.joinPaths(bin_repo, 'extensions', 'syncthing'))
        j.system.fs.copyFile(syncthing, j.system.fs.joinPaths(bin_repo, 'extensions', 'syncthing'))

        # upload bin to gitlab
        j.do.pushGitRepos(
            message='agent2 new build',
            name='agent2',
            account='binary'
        )

    def configure(self, service_obj):
        agentcontroller = service_obj.hrd.get('instance.agentcontroller')
        cfg_path = j.system.fs.joinPaths(j.dirs.baseDir, 'apps/agent2/agent2.toml')
        cfg = contoml.load(cfg_path)
        cfg['controllers']['main']['url'] = agentcontroller
        cfg['main']['gid'] = int(service_obj.hrd.get('instance.gid'))
        cfg['main']['nid'] = int(service_obj.hrd.get('instance.nid'))
        cfg['main']['roles'] = service_obj.hrd.getList('instance.roles')
        cfg.dump(cfg_path)
