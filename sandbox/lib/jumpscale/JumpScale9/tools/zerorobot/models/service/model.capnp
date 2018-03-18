@0x8ff7b25a18614028;

struct Service {
  guid @0: Text; #unique guid delivered by the zrotbot tarantool server

  template_unc
  template_version 
  template_version_active

  instance @2 :Text;  #to identify this service instance, is unique in this repo
  

  parent @5 :Text;

  producers @6 :List(Text); #has guids of services which deliver service to this service
  
  serviceState @7 :State;
  enum State {
    new @0;
    installing @1;
    ok @2;
    error @3;
    disabled @4;
    changed @5;
  }

  data @8 :Data;
  # bytes version capnp data used to hold all info to do with this service

  monitorStates @9: List(MonitorState);
  struct MonitorState {
    name @0 :Text; #network.internal.tcp.80
    state @1: State1; 
    enum State1 {
        ok @0;
        error @1;
    }
  }

  actionStates @10: List(ActionState);
  struct ActionState {
    name @0 :Text; 
    state @1: State2;
    enum State2 {
        new @0;
        ok @1;
        error @2;
    }
    type @2: ActionType;
    enum ActionType {
        service @0;
        reality @1;
    }    
    moddate @3: UInt32; #last mod to this actionstate e.g. action was ok on ...
  }

  zrobot @11: Text; #unique dns name of the zrobot if service not running in this zrobot

  moddate @12: UInt32; #last modification time (epoch)

  @13: List(Task);
  struct Task {
    taskGuid @0 :Text;
    serviceGuid @ :Text;  #if empty then myself, can be a remote one
    actionName @1 :Text; 
    timeoutPolicyName @2: Text;
    timeoutPolicyStep @3: UInt16;  #step in the timeout policy: 9999 means error, timeout achieved, cannot continue
    originator @4: Text; #dns name of robot who asked for this task, empty if self, this allows to report back on status of the action
    state @5: State3;
    enum State3 {
        new @0;
        ok @1;
        error @2;
        feedback @3; #waiting to deliver feedback to the originator !
    }    
  }

}
