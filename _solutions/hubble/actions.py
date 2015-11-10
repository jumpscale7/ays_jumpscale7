from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def build(self, service_obj):

        # move bin to the binary repo
        bin_repo = '/opt/code/git/binary/hubble/'

        j.do.pullGitRepo('https://git.aydo.com/binary/hubble.git')
        for f in j.system.fs.listFilesAndDirsInDir(bin_repo):
            if f.endswith('/.git'):
                continue
            j.system.fs.removeDirTree(f)

        package = 'github.com/Jumpscale/hubble'
        # build package
        go = j.atyourservice.get(name='go', parent=None)
        # path to bin and config
        gopath = go.hrd.getStr('instance.gopath')

        # building proxy
        go.actions.buildProjectGodep(go, package='https://%s' % package, build_dir='proxy/main', branch='production')

        bin_path = j.system.fs.joinPaths(gopath, 'bin', 'main')
        j.system.fs.copyFile(bin_path, j.system.fs.joinPaths(bin_repo, 'proxy'))

        # building agent
        go.actions.buildProjectGodep(go, package='https://%s' % package, build_dir='agent/main', branch='production')
        j.system.fs.copyFile(bin_path, j.system.fs.joinPaths(bin_repo, 'agent'))

        # upload bin to gitlab
        j.do.pushGitRepos(
            message='hubble new build',
            name='hubble',
            account='binary'
        )
