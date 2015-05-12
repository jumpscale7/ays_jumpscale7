from JumpScale import j
import os

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

    
    def prepare(self,serviceObj):
        j.system.process.execute('apt-get install gcc -y', outputToStdout=True)

    def configure(self,serviceObj):
        """
        this gets executed when files are installed
        this step is used to do configuration steps to the platform
        after this step the system will try to start the jpackage if anything needs to be started
        """
        gopath = serviceObj.hrd.get("instance.gopath")

        def createENV():
            bashrc = os.environ['HOME'] + "/" + ".bashrc"
            # create GOPATH
            if not j.system.fs.exists(gopath):
                j.system.fs.createDir(gopath)
                j.system.fs.createDir(j.system.fs.joinPaths(gopath,"pkg"))
                j.system.fs.createDir(j.system.fs.joinPaths(gopath,"src"))
                j.system.fs.createDir(j.system.fs.joinPaths(gopath,"bin"))

            j.do.execute(command="sed -i '/$GOPATH/d' %s" % bashrc)
            j.do.execute(command="sed -i '/GOPATH/d'  %s" % bashrc)
            j.do.execute(command="sed -i '/GOROOT/d'  %s" % bashrc)

            j.do.execute(command="echo 'export GOPATH=%s' >> %s"%(gopath, bashrc))
            j.do.execute(command="echo 'export GOROOT=/opt/go' >>  %s" % bashrc)
            j.do.execute(command="echo 'export PATH=$PATH:$GOROOT/bin:$GOPATH/bin' >>  %s" % bashrc)

        j.actions.start(name="create GOPATH", description='create GOPATH', action=createENV,  die=True, stdOutput=True, serviceObj=serviceObj)

        def installGodep():
            bashrc = os.environ['HOME'] + "/" + ".bashrc"
            j.do.execute(". %s && /opt/go/bin/go get -u github.com/tools/godep" % bashrc)
        j.actions.start(name="install godep", description='install godep (can take a while)', action=installGodep,  die=True, stdOutput=True, serviceObj=serviceObj)
        return True

    def removedata(self,serviceObj):
        j.system.fs.removeDirTree("/opt/go")
        j.do.execute(command="sed -i '/GOPATH/d' /root/.bashrc")
        j.do.execute(command="sed -i '/GOROOT/d' /root/.bashrc")