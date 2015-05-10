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
        # TO BE PACKAGED SERPERATELY
        j.system.process.execute('apt-get install rabbitmq-server -y')
        j.system.process.execute('apt-get install vsftpd -y')
        j.system.process.execute('apt-get install nginx -y')
        j.system.process.execute('apt-get install vsftpd -y')


    def configure(self, serviceObj):
        j.system.process.execute('useradd postgres', dieOnNonZeroExitCode=False)
        j.system.process.execute('su postgres -c "createdb store2"', dieOnNonZeroExitCode=False)
        j.system.process.execute('su postgres -c "createuser dcpm"', dieOnNonZeroExitCode=False)
        j.system.process.execute('su postgres -c "createdb dcpm -O dcpm"', dieOnNonZeroExitCode=False)
        j.system.process.execute('su postgres -c "createdb ui -O dcpm"', dieOnNonZeroExitCode=False)
        j.system.process.execute('su postgres -c "createdb core -O dcpm"', dieOnNonZeroExitCode=False)

        j.system.fs.createDir('/etc/postgresql/8.4/main')
        for config in j.system.fs.listFilesInDir('/opt/postgresql/pgha/doc/masterDB/', filter='.conf'):
            j.system.fs.copyFile(config, '/etc/postgresql/8.4/main')

        j.system.fs.createDir('/usr/lib/postgresql/8.4/bin/')
        cmd = 'ln -s /opt/postgresql/bin/* /usr/lib/postgresql/8.4/bin/'
        j.system.process.execute(cmd, dieOnNonZeroExitCode=False)

        j.system.process.execute('useradd ftp', dieOnNonZeroExitCode=False)


        j.system.process.execute("sed -i 's/\/etc\/init.d\/rsyslog restart/restart rsyslog/g' /opt/qbase5/pyapps/dcpm/impl/init/store_logger/9_store_logger.py")