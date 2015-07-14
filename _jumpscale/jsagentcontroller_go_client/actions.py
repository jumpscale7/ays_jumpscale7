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
        root = '/opt/build/github.com/Jumpscale/jsagentcontroller'

        j.system.fs.copyDirTree(
            j.system.fs.joinPaths(root, 'client'),
            '/opt/code/git/binary/jsagentcontroller_go_client'
        )

        j.do.pushGitRepos(
            message='agentcontroller client new build',
            name='jsagentcontroller_go_client',
            account='binary'
        )
