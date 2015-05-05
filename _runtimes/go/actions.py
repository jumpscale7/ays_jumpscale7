from JumpScale import j

ActionsBase=j.atyourservice.getActionsBaseClass()

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

    # def prepare(self,serviceObj):
    #     """
    #     this gets executed before the files are downloaded & installed on appropriate spots
    #     """
    #     j.do.execute('apt-get purge \'nginx*\' -y')
    #     j.do.execute('apt-get autoremove -y')
    #     j.system.process.killProcessByPort(80)
    #     j.system.fs.createDir("/var/nginx/cache/fcgi")
    #     j.system.fs.createDir("/var/log/nginx")
    #     return True

    def configure(self,serviceObj):
        """
        this gets executed when files are installed
        this step is used to do configuration steps to the platform
        after this step the system will try to start the jpackage if anything needs to be started
        """
        gopath = serviceObj.hrd.get("instance.gopath")

        def createENV():
            # create GOPATH
            if not j.system.fs.exists(gopath):
                j.system.fs.createDir(gopath)
                j.system.fs.createDir(j.system.fs.joinPaths(gopath,"pkg"))
                j.system.fs.createDir(j.system.fs.joinPaths(gopath,"src"))
                j.system.fs.createDir(j.system.fs.joinPaths(gopath,"bin"))

            j.do.execute(command="sed -i '/$GOPATH/d' /root/.bashrc")
            j.do.execute(command="sed -i '/GOPATH/d' /root/.bashrc")
            j.do.execute(command="sed -i '/GOROOT/d' /root/.bashrc")

            j.do.execute(command="echo 'export GOPATH=%s' >> /root/.bashrc"%gopath)
            j.do.execute(command="echo 'export GOROOT=/opt/go' >> /root/.bashrc")
            j.do.execute(command="echo 'export PATH=$PATH:$GOROOT/bin:$GOPATH/bin' >> /root/.bashrc")
            j.do.execute(command=". /root/.bashrc")
        j.actions.start(name="create GOPATH", description='create GOPATH', action=createENV,  die=True, stdOutput=True, serviceObj=serviceObj)

        def installGodep():
            j.do.execute("/opt/go/bin/go get -u github.com/tools/godep")
        j.actions.start(name="install godep", description='install godep (can take a while)', action=installGodep,  die=True, stdOutput=True, serviceObj=serviceObj)
        return True

    def removedata(self,serviceObj):
        j.system.fs.removeDirTree("/opt/go")
        j.do.execute(command="sed -i '/GOPATH/d' /root/.bashrc")
        j.do.execute(command="sed -i '/GOROOT/d' /root/.bashrc")