from JumpScale import j

ActionsBase=j.packages.getActionsBaseClass()

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
        """
        this gets executed before the files are downloaded & installed on approprate spots
        """
        # from IPython import embed
        # print "DEBUG NOW ooo"
        # embed()

        # cmd='cd /opt/postgresql/bin;./psql -U postgres template1 -c 'create database pydio;' -h localhost'

        # "php5-mcrypt","php5-pgsql"

        # j.do.execute("")
        # j.do.execute("php5enmod mcrypt")
        # j.do.chown("/usr/share/pydio/",user="www-data")
        
# apt-get install php5-mcrypt
# mv -i /etc/php5/conf.d/mcrypt.ini /etc/php5/mods-available/
# php5enmod mcrypt
        
        # j.do.execute('apt-get purge \'mongo*\' -y')
        # j.do.execute('apt-get autoremove -y')
        # j.system.fs.createDir("$(system.paths.var)/mongodb/$(jp.instance)")
        # j.system.platform.ubuntu.stopService("mongod")
        # j.system.platform.ubuntu.serviceDisableStartAtBoot("mongod")
        return True
        
    def configure(self,serviceObj):
        """
        this gets executed when files are installed
        this step is used to do configuration steps to the platform
        after this step the system will try to start the jpackage if anything needs to be started
        """
        # j.system.fs.chown(path="/opt/lemp", user="www-data") 
        return True

    # def stop(self,serviceObj):
    #     """
    #     if you want a gracefull shutdown implement this method
    #     a uptime check will be done afterwards (local)
    #     return True if stop was ok, if not this step will have failed & halt will be executed.
    #     """
    #     return True

    # def halt(self,serviceObj):
    #     """
    #     hard kill the app, std a linux kill is used, you can use this method to do something next to the std behaviour
    #     """
    #     return True

    # def check_uptime_local(self,serviceObj):
    #     """
    #     do checks to see if process(es) is (are) running.
    #     this happens on system where process is
    #     """
    #     return True

    # def check_requirements(self,serviceObj):
    #     """
    #     do checks if requirements are met to install this app
    #     e.g. can we connect to database, is this the right platform, ...
    #     """
    #     return True

    # def monitor_local(self,serviceObj):
    #     """
    #     do checks to see if all is ok locally to do with this package
    #     this happens on system where process is
    #     """
    #     return True

    # def monitor_remote(self,serviceObj):
    #     """
    #     do checks to see if all is ok from remote to do with this package
    #     this happens on system from which we install or monitor (unless if defined otherwise in hrd)
    #     """
    #     return True

    # def cleanup(self,serviceObj):
    #     """
    #     regular cleanup of env e.g. remove logfiles, ...
    #     is just to keep the system healthy
    #     """
    #     return True

    # def data_export(self,serviceObj):
    #     """
    #     export data of app to a central location (configured in hrd under whatever chosen params)
    #     return the location where to restore from (so that the restore action knows how to restore)
    #     we remember in $name.export the backed up events (epoch,$id,$state,$location)  $state is OK or ERROR
    #     """
    #     return False

    # def data_import(self,id,hrd,serviceObj):
    #     """
    #     import data of app to local location
    #     if specifies which retore to do, id corresponds with line item in the $name.export file
    #     """
    #     return False

    # def uninstall(self,serviceObj):
    #     """
    #     uninstall the apps, remove relevant files
    #     """
    #     pass


