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

    def prepare(self,serviceobj):
        """
        this gets executed before the files are downloaded & installed on approprate spots
        """
        def addSource():
            cmd="""
    sh -c "echo deb https://get.docker.io/ubuntu docker main > /etc/apt/sources.list.d/docker.list"
    apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys
    """

            j.system.process.executeWithoutPipe(cmd)

            print ("update apt")
            j.system.process.executeWithoutPipe("apt-get update -y",dieOnNonZeroExitCode=False)
        j.actions.start(name="addSource",description='addSource', action=addSource, stdOutput=True, serviceObj=serviceobj)

        def install():
            print ("install lxc docker")
            j.system.platform.ubuntu.install("lxc-docker")

            j.system.process.executeWithoutPipe("sudo service docker restart")
        j.actions.start(name="install",description='install', action=install, stdOutput=True, serviceObj=serviceobj)
        return True

    def start(self, serviceobj):
        j.do.execute('service docker start', dieOnNonZeroExitCode=False)

    def stop(self, serviceobj):
        j.do.execute('service docker stop', dieOnNonZeroExitCode=False)