from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()
import os.path

_VERSION = "2.0.0"  # Todo: Make this value non-hardcoded


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

	j.system.fs.createDir('/etc/postgresql/8.4/main')
        for config in j.system.fs.listFilesInDir('/opt/postgresql/pgha/doc/masterDB/', filter='*.conf'):
            j.system.fs.copyFile(config, '/etc/postgresql/8.4/main')
	j.system.fs.symlink('/opt/postgresql/bin', '/usr/lib/postgresql/8.4/bin', overwriteTarget=True)

        j.system.fs.symlink('/etc/init.d/ays', '/etc/init.d/nginx', overwriteTarget=True)

        j.system.unix.addSystemUser('ftp')

        j.system.process.execute("pkill nginx", dieOnNonZeroExitCode=False)
        j.system.process.execute("/etc/init.d/rabbitmq-server restart")

        cmd = """
export LANGUAGE=en_US.UTF-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
locale-gen en_US.UTF-8
dpkg-reconfigure locales
        """
        j.system.process.execute(cmd)

	DCPM_NOAUTH_CONFIG_PATH = '/opt/code/git/binary/dcpm-nooauthconfig'
	OSIS_DB_PATH = '/opt/qbase5/cfg/osisdb.cfg'
	STORELIB_PATH = '/opt/qbase5/cfg/qconfig/storelib2.cfg'

	j.system.fs.copyFile(os.path.join(DCPM_NOAUTH_CONFIG_PATH, 'osisdb.cfg'), OSIS_DB_PATH)
	osis_db_ini = j.tools.inifile.open(OSIS_DB_PATH)
	osis_db_ini.setParam('dcpm', 'type', serviceObj.hrd.get('instance.param.dcpm.db.main.type').lower())
	osis_db_ini.setParam('dcpm', 'ip', serviceObj.hrd.get('instance.param.dcpm.db.main.host'))
	osis_db_ini.setParam('dcpm', 'port', serviceObj.hrd.get('instance.param.dcpm.db.main.port'))
	osis_db_ini.setParam('dcpm', 'database', serviceObj.hrd.get('instance.param.dcpm.db.main.name'))
	osis_db_ini.setParam('dcpm', 'login', serviceObj.hrd.get('instance.param.dcpm.db.main.username'))
	osis_db_ini.setParam('dcpm', 'passwd', serviceObj.hrd.get('instance.param.dcpm.db.main.password'))
	osis_db_ini.write()

	j.system.fs.copyFile(os.path.join(DCPM_NOAUTH_CONFIG_PATH, 'storelib2.cfg'), STORELIB_PATH)
	db_type = serviceObj.hrd.get('instance.param.dcpm.db.monitor.type').lower()
	storelib_ini = j.tools.inifile.open(STORELIB_PATH)
	storelib_ini.setParam('main', 'store', db_type)
	storelib_ini.addSection(db_type)
	storelib_ini.setParam(db_type, 'dbtype', db_type)
	storelib_ini.setParam(db_type, 'hostname', serviceObj.hrd.get('instance.param.dcpm.db.monitor.host'))
	storelib_ini.setParam(db_type, 'port', serviceObj.hrd.get('instance.param.dcpm.db.monitor.port'))
	storelib_ini.setParam(db_type, 'dbname', serviceObj.hrd.get('instance.param.dcpm.db.monitor.name'))
	storelib_ini.setParam(db_type, 'username', serviceObj.hrd.get('instance.param.dcpm.db.monitor.username'))
	storelib_ini.setParam(db_type, 'password', serviceObj.hrd.get('instance.param.dcpm.db.monitor.password'))
	storelib_ini.write()

        cmds = ['rm -rf /opt/qbase5/lib/python/site-packages/pytz*',
                'apt-get install python-pip -y',
                'mkdir -p /root/.pip/.cache',
                'pip install --target=/opt/qbase5/lib/python/site-packages/ --find-links=/root/.pip/.cache pytz',
                '/opt/qbase5/qshell -c "p.application.install(\'dcpm\')"',
                'chown -R syslog:adm /opt/qbase5/var/log/dcpm/']

        for cmd in cmds:
            j.system.process.execute(cmd)

	j.system.fs.copyFile(os.path.join(DCPM_NOAUTH_CONFIG_PATH, 'oauth.js'), '/opt/qbase5/pyapps/dcpm/portal/static/js/oauth.js')
	j.system.process.execute('/opt/qbase5/qshell -c "from racktivity import settings; settings.setValue(\'software.version\', \'' + _VERSION + '\')"')
        j.system.process.execute('/opt/qbase5/qshell -c "p.application.restart(\'dcpm\')"')
	j.system.process.execute('/opt/qbase5/qshell -c "from racktivity import generator; generator.generateSettings()"')

        # print "Please install DCPM app in qbase by executing:\n/opt/qbase5/qshell -c \"p.application.install('dcpm')\""

    def start(self, serviceObj):
	try:
	    j.system.process.execute('/opt/qbase5/qshell -c "p.application.start(\'dcpm\')"')
	except Exception, e:
	    print "Could not start DCPM - %s" % e

    def stop(self, serviceObj):
	try:
	    j.system.process.execute('/opt/qbase5/qshell -c "p.application.stop(\'dcpm\')"')
	except Exception, e:
	    print "Could not stop DCPM - %s" % e
