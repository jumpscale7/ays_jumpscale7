from JumpScale import j
from StringIO import StringIO
import signal

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
    def configure(self,serviceObj):
        """
        this gets executed when files are installed
        this step is used to do configuration steps to the platform
        after this step the system will try to start the jpackage if anything needs to be started
        """
        base = j.application.config.get('system.paths.base')
        base = base + '/apps/samba4'

        domain = serviceObj.hrd.get('instance.param.smb.domain')

        # Building config files
        j.system.fs.copyFile(base + '/smb.standalone.conf', '/etc/samba/smb.conf')

        data = {
            'workgroup': domain.upper(),
        }

        hrd = j.core.hrd.getHRDFromDict(data)
        hrd.applyOnFile('/etc/samba/smb.conf')
