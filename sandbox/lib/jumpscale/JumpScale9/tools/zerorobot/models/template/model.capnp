@0xe626dcd0e0867f02;

struct Template {

  guid @0: Text; #unique guid delivered by the zrotbot tarantool server

  unc @1: Text; # $repo_host/$repo_account/$repo_name/$name
  name #name of the service e.g. node.kvm, unique in this repo
  version

  repo_host
  repo_account
  repo_name
  repo_branch

  parent @3 :TemplateRolePointer; 

  actions @5 :List(Action);
  struct Action {
    name @0 :Text;
    code @1 :Text;
    period @2 :UInt32;  #use j.data.time.getSecondsInHR( to show HR is in seconds
    log @3 :Bool;       #should we create log of this action?
    isJob @4 :Bool;
    timeoutPolicyName @5: Text; #is template with name system.timeoutpolicy
    type @6: ActionType; 
    enum ActionType {
        service @0;
        reality @1;
    } 
  }


  flist @7 :List(Flist);
  struct Flist {
    os @0: OSType;
    enum OSType {
        ubuntu @0;
    }
    mountpoint @0 :Text; #default = /
    paths @1 :List(FPath);    
    struct FPath {
      path @0 :Text; #relative to mountpoint
      hash @1 :Text;      
      mode @2 :Mode;
      enum Mode {
        ro @0;
        rw @1;
        ol @2;
      }
    }
  }

  templateDataSchema @8 :Text;
  templateData @9 :Data; #is capnp data structure

  serviceDataSchema @10 :Text;

}
