from JumpScale import j
import time
import os

ActionsBase=j.atyourservice.getActionsBaseClass()

class Actions(ActionsBase):

    def prepare(self,serviceObj):
        """
        this gets executed before the files are downloaded & installed on approprate spots
        """
        j.do.execute('sudo locale-gen && sudo dpkg-reconfigure locales && export LC_ALL=$LANG && export LANGUAGE=$LANG')
        j.do.execute('DEBIAN_FRONTEND=noninteractive apt-get install -y postfix')
   # Add git user
        try:
            j.do.execute('adduser --disabled-login --gecos \'GitLab\' git')
        except Exception:
            print 'user already here'
            pass

        j.do.execute('usermod -aG root git')
        j.do.createDir('/home/git/gitlab')
        j.do.createDir('/home/git/gitlab-shell')
        j.do.copyFile('/etc/login.defs', '/etc/login.defs.org')
        j.do.execute("cd /etc/ && sed 's/ENV_PATH\tPATH=.*/ENV_PATH\tPATH=\/opt\/jumpscale7\/bin:\/opt\/postgresql\/bin:\/opt\/jumpscale7\/apps\/redis:\/usr\/local\/sbin:\/usr\/local\/bin:\/usr\/sbin:\/usr\/bin:\/sbin:\/bin:\/usr\/games:\/usr\/local\/games:\/opt\/ruby\/bin/' login.defs.org | tee login.defs")
        j.do.execute('chmod +w /etc/sudoers')
        j.do.copyFile('/etc/sudoers', '/etc/sudoers.org')
        j.do.execute("cd /etc/ && sed 's/Defaults\tsecure_path=.*/Defaults\tsecure_path=\/opt\/jumpscale7\/bin:\/opt\/postgresql\/bin:\/opt\/jumpscale7\/apps\/redis:\/usr\/local\/sbin:\/usr\/local\/bin:\/usr\/sbin:\/usr\/bin:\/sbin:\/bin:\/usr\/games:\/usr\/local\/games:\/opt\/ruby\/bin/' /etc/sudoers.org | tee /etc/sudoers")
   # Install Redis
        try:
            x = j.atyourservice.findTemplates('jumpscale', 'redis')[0]
            x.install(instance="gitlab",start=True,deps=True, reinstall=False, args={'param.disk':0, 'param.mem': 100, 'param.passwd': '', 'param.port': 0, 'param.unixsocket': 1}, parent=None, noremote=False)
            time.sleep(5)
        except Exception:
            print ' **** FAIL IN REDIS INSTALLATION PACKAGE :( :( :('
            time.sleep(5)
            pass
   # Install Postgresql
        try:
            x = j.atyourservice.findTemplates('jumpscale', 'postgresql')[0]
            x.install(instance="main",start=True,deps=True, reinstall=False, args={'param.rootpasswd':'rooter', 'param.port': 5432}, parent=None, noremote=False)
            time.sleep(5)
        except Exception:
            print ' **** FAIL IN Postgresql INSTALLATION PACKAGE :( :( :('
            pass
   # Install nginx
        try:
            x = j.atyourservice.findTemplates('jumpscale', 'nginx')[0]
            x.install(instance="main",start=True,deps=True, reinstall=False, args={}, parent=None, noremote=False)
        except Exception:
            print ' **** FAIL IN REDIS INSTALLATION PACKAGE :( :( :('
            pass
   # Install Ruby
        try:
            x = j.atyourservice.findTemplates('jumpscale', 'ruby')[0]
            x.install(instance="main",start=False,deps=True, reinstall=False, args={}, parent=None, noremote=False)
        except Exception:
            print ' **** FAIL IN REDIS INSTALLATION PACKAGE :( :( :('
            pass
        
        return True
        
    def configure(self,serviceObj):
#        os.system('export PATH=$PATH:/opt/ruby/bin')
     ###   j.do.execute('cd /home/git/gitlab && gem install execjs')
     ###   j.do.execute('ln -s /home/git/gitlab/.gitlab_shell_secret /home/git/gitlab-shell/.gitlab_shell_secret')
   # Postgresql partation
        j.do.execute('cd /opt/postgresql/bin; sudo -u postgres /opt/postgresql/bin/psql -d template1 -c \'CREATE USER git CREATEDB\'')
        j.do.execute('cd /opt/postgresql/bin; sudo -u postgres /opt/postgresql/bin/psql -d template1 -c \'CREATE DATABASE gitlabhq_production OWNER git\'')
   # Install gitlab
        j.do.execute('sudo -u git -H mkdir /home/git/repositories')
        j.do.execute('sudo -u git -H mkdir -m 2770 /home/git/gitlab-satellites')
        j.do.copyFile('/home/git/gitlab/lib/support/init.d/gitlab.default.example', '/etc/default/gitlab')
        j.do.copyFile('/home/git/gitlab/lib/support/logrotate/gitlab', '/etc/logrotate.d/gitlab')
        j.do.execute('chown git:git -R /home/git')
        j.do.execute('usermod -a -G root git')
   # Configure Enginx
        if not j.do.isFile('/opt/nginx/cfg/sites-available/gitlab'):
            j.do.copyFile('/home/git/gitlab/lib/support/nginx/gitlab', '/opt/nginx/cfg/sites-available/gitlab')
        if not j.do.isFile('/opt/nginx/cfg/sites-enabled'):
            j.do.createDir('/opt/nginx/cfg/sites-enabled')
        if not j.do.isLink('/opt/nginx/cfg/sites-enabled/gitlab'):
            j.do.execute('ln -s /opt/nginx/cfg/sites-available/gitlab /opt/nginx/cfg/sites-enabled/gitlab')
            j.do.delete('/opt/nginx/cfg/sites-enabled/default')

        ##j.do.execute("sed 's/production:\ unix:.*/production:\ unix:\/opt\/jumpscale7\/var\/redis\/gitlab\/redis.sock/' /home/git/gitlab/config/resque.yml.org | tee /home/git/gitlab/config/resque.yml")
        j.do.execute('chmod 755 /opt/jumpscale7/var/redis/gitlab/redis.sock')
        os.system("cd /home/git/gitlab && sudo -u git -H bundle exec rake gitlab:setup RAILS_ENV=production")
        nginx = j.packages.get(name='nginx', instance='main')
        nginx.restart()
        print('userName: root\npassword: 5iveL!fe')
        return True
