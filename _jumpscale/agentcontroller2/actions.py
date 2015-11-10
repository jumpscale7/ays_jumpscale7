import hashlib
from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def build(self, service_obj):
        package = 'github.com/Jumpscale/agentcontroller2'
        # build package
        go = j.atyourservice.get(name='go', parent=None)
        go.actions.buildProjectGodep(go, package='https://%s' % package)

        # path to bin and config
        gopath = go.hrd.getStr('instance.gopath')
        # @todo can't we change the binary to agentcontroller2
        bin_path = j.system.fs.joinPaths(gopath, 'bin', 'agentcontroller2')
        cfg_path = j.system.fs.joinPaths(gopath, 'src', package, 'agentcontroller.toml')
        handlers_path = j.system.fs.joinPaths(gopath, 'src', package, 'extensions')

        # move bin to the binary repo
        bin_repo = '/opt/code/git/binary/agentcontroller2/agentcontroller2/'

        j.do.pullGitRepo('https://git.aydo.com/binary/agentcontroller2.git')
        for f in j.system.fs.listFilesAndDirsInDir('/opt/code/git/binary/agentcontroller2'):
            if f.endswith('/.git'):
                continue
            j.system.fs.removeDirTree(f)

        j.system.fs.createDir(bin_repo)
        j.system.fs.copyFile(bin_path, bin_repo)
        j.system.fs.copyFile(
            cfg_path,
            j.system.fs.joinPaths(bin_repo, 'agentcontroller2.toml')
        )
        j.system.fs.copyDirTree(handlers_path, j.system.fs.joinPaths(bin_repo, 'extensions'))

        # upload bin to gitlab
        j.do.pushGitRepos(
            message='agentcontroller2 new build',
            name='agentcontroller2',
            account='binary'
        )

    def configure(self, service_obj):
        import contoml
        """
        this gets executed when files are installed
        this step is used to do configuration steps to the platform
        after this step the system will try to start the ays if anything needs to be started
        """

        # for backwards compatibility
        base = '/opt/jumpscale7/apps/agentcontroller2'
        try:
            j.system.fs.renameFile("/opt/jumpscale7/apps/agentcontroller2/jsagentcontroller",
                                   j.system.fs.joinPaths(base, 'agentcontroller2'))
        except:
            pass

        toml = '/opt/jumpscale7/apps/agentcontroller2/agentcontroller2.toml'
        cfg = contoml.load(toml)
        redis = service_obj.hrd.get('instance.param.redis.host')
        cfg['main']['redis_host'] = redis
        cfg['main']['redis_password'] = service_obj.hrd.get('instance.param.redis.password')

        # configure env var for handlers
        redis_host, _, redis_port = redis.partition(':')
        cfg['handlers']['env']['REDIS_ADDRESS'] = redis_host
        cfg['handlers']['env']['REDIS_PORT'] = redis_port
        cfg['handlers']['env']['REDIS_PASSWORD'] = service_obj.hrd.get('instance.param.redis.password')

        syncthing = j.atyourservice.get(name='syncthing', instance='controller')
        cfg['handlers']['env']['SYNCTHING_URL'] = 'http://localhost:%s/' % syncthing.hrd.get('instance.param.port')
        cfg.dump(toml)

        # Start script syncing (syncthing)
        jumpscripts = j.system.fs.joinPaths(base, 'jumpscripts')

        j.system.fs.createDir(jumpscripts)

        syncthing_id = syncthing.actions.get_syncthing_id(syncthing)
        folderid = 'jumpscripts-%s' % hashlib.md5(syncthing_id).hexdigest()
        syncthing.actions.add_folder(syncthing, folderid, jumpscripts)
