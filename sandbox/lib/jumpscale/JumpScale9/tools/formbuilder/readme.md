# how to create forms to quickly collect information

```python
TEMPLATE = """
fullname = ""
email = ""
login_name = ""
sshkeyname = ""
mylist = [ ]
"""

BaseConfig=j.tools.formbuilder.baseclass_get()

class MyConfig(BaseConfig):

    def init(self):
        self.auto_disable.append("sshkeyname") #makes sure that this property is not auto populated, not needed when in form_add_items_pre

    def form_add_items_post(self):
        #SSHKEYS
        sshpath = "%s/.ssh" % (j.dirs.HOMEDIR)
        # keynames = [j.sal.fs.getBaseName(item) for item in j.clients.sshkey.list()] #load all ssh keys loaded in mem
        keynames = [j.sal.fs.getBaseName(item)[:-4] for item in j.sal.fs.listFilesInDir(sshpath, filter="*.pub")]
        if len(keynames)==0:
            raise RuntimeError("load ssh-agent")
        self.widget_add_multichoice("sshkeyname",keynames)

    def form_pre_save(self):
        result={}
        #can overrule some result, will not do here
        return result

#will create empty config file properly constructed starting from the template
config,errors=j.data.serializer.toml.merge(TEMPLATE,{})

#don't start from an empty config
config["email"]="someemail@rrr.com"
config["sshkeyname"] = [j.sal.fs.getBaseName(item) for item in j.clients.sshkey.list()][0]
for i in range(3):
    config["mylist"].append("this is an item in the list: %s"%i)

c=MyConfig(name="test",template=TEMPLATE,config=config)

assert c.config["email"]=="someemail@rrr.com" #don't change it during test

print (c.yaml)
```
