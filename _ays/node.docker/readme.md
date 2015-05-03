

```
# creation of a sshkey service, it will be use to access the node
data={}
data['instance.key.priv'] = '' #empty private key trigger auto generation
keyInstance = j.atyourservice.new(name='sshkey',instance="mykey",args=data)
keyInstance.install()

data={}
data["instance.ip"]="172.17.0.3"
data["instance.ssh.port"]=22
data['instance.sshkey']=keyInstance.instance
data['instance.login'] = 'root'
data['instance.password'] = 'supersecret'
node = j.atyourservice.new(name='node.ssh',args=data)
node.install()
```