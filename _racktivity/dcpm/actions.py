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
    step5b: if check uptime was true will do stop action and retry the check_uptime_local configureheck
    step5c: if check uptime was true even after stop will do halt action and retry the check_uptime_local check
    step6: use the info in the hrd to start the application
    step7: do check_uptime_local to see if process starts
    step7b: do monitor_local to see if package healthy installed & running
    step7c: do monitor_remote to see if package healthy installed & running, but this time test is done from central location
    """
    def prepare(self, serviceObj):
        j.system.platform.ubuntu.install('python-pygresql')

    def configure(self, serviceObj):
        j.system.fs.createDir('/etc/nginx/')
        j.system.fs.symlink('/etc/nginx/nginx.conf', '/opt/nginx/cfg/nginx.conf', overwriteTarget=True)
        j.system.fs.symlink('/etc/nginx/sites-available', '/opt/nginx/cfg/sites-available', overwriteTarget=True)
        j.system.fs.symlink('/etc/nginx/sites-enabled', '/opt/nginx/cfg/sites-enabled', overwriteTarget=True)
        j.system.fs.symlink('/opt/nginx/cfg/mime.types', '/etc/nginx/mime.types', overwriteTarget=True)

        j.system.unix.addSystemUser('postgres')
        j.system.unix.addSystemUser('ftp')

        j.system.fs.createDir('/etc/postgresql/8.4/main')
        for config in j.system.fs.listFilesInDir('/opt/postgresql/pgha/doc/masterDB/', filter='*.conf'):
            j.system.fs.copyFile(config, '/etc/postgresql/8.4/main')

        j.system.fs.createDir('/usr/lib/postgresql/8.4/bin/')
        cmd = 'ln -s /opt/postgresql/bin/* /usr/lib/postgresql/8.4/bin/'
        j.system.process.execute(cmd, dieOnNonZeroExitCode=False)

        j.system.process.execute("pkill nginx", dieOnNonZeroExitCode=False)
        j.system.process.execute("/etc/init.d/rabbitmq-server restart")

        print "Please install DCPM app in qbase by executing:\n/opt/qbase5/qshell -c \"p.application.install('dcpm')\""
