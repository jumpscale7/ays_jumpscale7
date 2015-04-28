create a node which will be configured using a pregenerated key (ays: sshkey)
you should know login/passwd or your system should already be configured to automatically login over ssh to the destination node

example how to be used

'''
# creation of a nodes inside the location
data={}
data["instance.ip"]="172.17.0.3"
data["instance.ssh.port"]=22
data['instance.password']='coucou'
data['instance.login']='root'
data['instance.sshkey']=keyInstance.instance
node_pushkey = j.atyourservice.new(name='node.pushkey',parent=locInstance,args=data)
node_pushkey.init()
node_pushkey.execute() #push the key to the node
'''

now look at node.ssh how to use this

as command line
'''
ays install -n sshkey -i mykey
'''

if you use interactively just enter an empty string (type '.' and enter) to generate a key.

