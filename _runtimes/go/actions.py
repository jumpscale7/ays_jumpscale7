from JumpScale import j
from urllib2 import urlparse
import os

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
    step7c: do monitor_remote to see if package healthy installed & running, but this time test is done from central location
    """

    def prepare(self, serviceObj):
        j.system.platform.ubuntu.install("gcc")

    def configure(self, serviceObj):
        """
        this gets executed when files are installed
        this step is used to do configuration steps to the platform
        after this step the system will try to start the ays if anything needs to be started
        """

        serviceObj.hrd.set('instance.goroot', serviceObj.hrd.getStr('service.base', '/opt/go'))

        def createGOPATH():
            # create GOPATH
            if not j.system.fs.exists('$(instance.gopath)'):
                j.system.fs.createDir('$(instance.gopath)')
                j.system.fs.createDir(j.system.fs.joinPaths('$(instance.gopath)', "pkg"))
                j.system.fs.createDir(j.system.fs.joinPaths('$(instance.gopath)', "src"))
                j.system.fs.createDir(j.system.fs.joinPaths('$(instance.gopath)', "bin"))

        j.actions.start(name="create GOPATH", description='create GOPATH', action=createGOPATH,  die=True, stdOutput=True, serviceObj=serviceObj)

    def buildProject(self, serviceObj, package=None):
        """
        you can call this method from another service action.py file to build a go project
        """
        if package is None:
            j.events.inputerror_critical(msg="package can't be none", category="go build", msgpub='')

        gopath = serviceObj.hrd.get('instance.gopath')
        goroot = serviceObj.hrd.get('instance.goroot')
        gobin = j.system.fs.joinPaths(goroot, 'bin/go')
        env = os.environ
        env.update({
            'GOPATH': gopath,
            'GOROOT': goroot
        })
        getcmd = '%s get -a -u -v %s' % (gobin, package)
        re, out, err = 0, '', ''
        try:
            print "start : %s" % getcmd
            re, out, err = j.system.process.run(getcmd, env=env, maxSeconds=60,  showOutput=True, captureOutput=False)
            print "go get succeed" if re == 0 else "error during go get"
        except Exception as e:
            print e.msg

    def buildProjectGodep(self, serviceObj, package=None, build_dir=None):
        """
        you can call this method from another service action.py file to build a go project
        :param package: URL to package to build (https://github.com/...)
        """
        if package is None:
            j.events.inputerror_critical(msg="package can't be none", category="go build", msgpub='')

        url = urlparse.urlparse(package)

        gopath = serviceObj.hrd.get('instance.gopath')
        goroot = serviceObj.hrd.get('instance.goroot')
        gobin = j.system.fs.joinPaths(goroot, 'bin/go')
        godepbin = j.system.fs.joinPaths(gopath, 'bin/godep')

        dest = '%s/src/%s' % (gopath, url.hostname + url.path)
        j.system.fs.removeDirTree(dest)

        env = os.environ
        env.update({
            'GOPATH': gopath,
            'GOROOT': goroot,
            'PATH': '%s:%s/bin' % (env['PATH'], goroot)
        })

        build_dest = dest
        if build_dir is not None:
            build_dest = j.system.fs.joinPaths(dest, build_dir)

        cmds = [
            '%s get github.com/tools/godep' % gobin,
            'git clone %s %s' % (package, dest),
            'cd %s && %s restore' % (build_dest, godepbin),
            'cd %s && %s install' % (build_dest, gobin),
        ]

        for cmd in cmds:
            try:
                print "%s: start" % cmd
                re, out, err = j.system.process.run(cmd, env=env, maxSeconds=60, showOutput=True, captureOutput=False)
                print "%s: succeed" % cmd if re == 0 else "%s: error" % cmd
            except Exception as e:
                print out, err
                print e.msg

    def removedata(self, serviceObj):
        j.system.fs.removeDirTree("/opt/go")
