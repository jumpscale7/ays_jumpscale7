from JumpScale import j
import os

ActionsBase=j.atyourservice.getActionsBaseClass()

class Actions(ActionsBase):
	def prepare(self,serviceObj):
		"""
		this gets executed before the files are downloaded & installed on approprate spots
		"""
		print 'START PROGRAM ............................................\n'
		folders = ['bin', 'include', 'lib', 'share']
		for folder in folders:
			if not j.do.exists('/opt/jumpscale7/%s' % folder):
				j.do.createDir('/opt/jumpscale7/%s' %folder)
				print '[Create] /opt/jumpscale7/%s)' % folder
			else:
				print '[Found] /opt/jumpscale7/%s)' % folder
		return True

#	def configure(self,serviceObj):

#    def stop(self, serviceObj):
#        if not j.system.process.getPidsByPort(5672):
#            return
#        j.system.process.execute('cd /opt/jumpscale7/sbin && ./rabbitmqctl stop')	
