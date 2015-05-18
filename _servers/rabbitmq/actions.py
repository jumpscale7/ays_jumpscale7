from JumpScale import j
import os

ActionsBase=j.atyourservice.getActionsBaseClass()

class Actions(ActionsBase):
	def prepare(self,serviceObj):
		"""
		this gets executed before the files are downloaded & installed on approprate spots
		"""
		print 'START PROGRAM ............................................\n'
		if not j.do.exists('/opt/jumpscale7/apps/'):
			j.do.createDir('/opt/jumpscale7/apps')
			print '[Create] /opt/jumpscale7/apps'
		else:
			print '[Found] /opt/jumpscale7/apps'
		if not j.do.exists('/opt/jumpscale7/etc/'):
			j.do.createDir('/opt/jumpscale7/etc')
			print '[Create] /opt/jumpscale7/etc'
		else:
			print '[Found] /opt/jumpscale7/etc'
		if not j.do.exists('/opt/jumpscale7/include'):
			j.do.createDir('/opt/jumpscale7/include')
			print '[Create] /opt/jumpscale7/include'
		else:
			print '[Found] /opt/jumpscale7/include'
		if not j.do.exists('/opt/jumpscale7/plugins'):
			j.do.createDir('/opt/jumpscale7/plugins')
			print '[Create] /opt/jumpscale7/plugins'
		else:
			print '[Found] /opt/jumpscale7/plugins'
		if not j.do.exists('/opt/jumpscale7/bin'):
			j.do.createDir('/opt/jumpscale7/bin')
			print '[Create] /opt/jumpscale7/bin'
		else:
			print '[Found] /opt/jumpscale7/bin'
		if not j.do.exists('/opt/jumpscale7/var'):
			j.do.createDir('/opt/jumpscale7/var')
			print '[Create] /opt/jumpscale7/var'
		else:
			print '[Found] /opt/jumpscale7/var'
		if not j.do.exists('/opt/jumpscale7/lib/'):
			j.do.createDir('/opt/jumpscale7/lib')
			print '[Create] /opt/jumpscale7/lib'
		else:
			print '[Found] /opt/jumpscale7/lib'
		return True

	def configure(self,serviceObj):
		tolink = ['ct_run', ' dialyzer', ' epmd', ' erl', ' erlc', ' escript', ' run_erl', ' to_erl', ' typer']
		for link in tolink:
			j.system.fs.symlink('/opt/jumpscale7/lib/bin/%s' % link, '/opt/jumpscale7/bin/%s' % link, overwriteTarget=True)

#    def stop(self, serviceObj):
#        if not j.system.process.getPidsByPort(5672):
#            return
#        j.system.process.execute('cd /opt/jumpscale7/sbin && ./rabbitmqctl stop')	