
box.schema.space.create('service',{if_not_exists= true, engine="memtx"})

box.space.service:create_index('primary',{ type = 'tree', parts = {1, 'string'}, if_not_exists= true})

--create 2nd index for e.g. name
-- box.space.service:create_index('secondary', {type = 'tree', parts = {2, 'string'}, if_not_exists= true})

box.schema.user.create('user', {password = 'secret', if_not_exists= true})



function model_service_get(name, id, ....)
    return box.space.service:get(key)
    -- if type(key) == 'number' then
    --     return box.space.service:get(key)
    -- end
    -- return box.space.service.index.secondary:get(key)
end

box.schema.func.create('model_service_get', {if_not_exists = true})
box.schema.user.grant('user', 'execute', 'function', 'model_service_get',{ if_not_exists= true})



function model_service_get_json(key)
    local res = model_service_get(key)
    if res == nil then
        return nil
    else
        return model_capnp_service.Service.parse(res[3])
    end
end

box.schema.func.create('model_service_get_json', {if_not_exists = true})
box.schema.user.grant('user', 'execute', 'function', 'model_service_get_json',{ if_not_exists= true})



function model_service_set(data)
    local obj = model_capnp_service.Service.parse(data) --deserialze capnp
    local name = obj["name"]
    res0 = model_service_get(name)
    -- if res0 == nil then
    --     res = box.space.service:auto_increment({obj['name'],data}) -- indexes the name
    --     id = res[1]
    -- else
    --     id = res0[1]
    -- end
    -- obj["id"] = id
    -- data = model_capnp_service.Service.serialize(obj) --reserialze with id inside
    box.space.service:put{key, data}
    return
end

box.schema.func.create('model_service_set', {if_not_exists = true})
box.schema.user.grant('user', 'execute', 'function','model_service_set',{ if_not_exists= true})



function model_service_delete(key)
    box.space.service:delete(key)
end
box.schema.func.create('model_service_delete', {if_not_exists = true})
box.schema.user.grant('user', 'execute', 'function', 'model_service_delete',{ if_not_exists= true})



function model_service_find(query)
    local obj = model_capnp_service.Service.parse(data) --deserialze capnp
    res={}
    return res
end

box.schema.func.create('model_service_find', {if_not_exists = true})
box.schema.user.grant('user', 'execute', 'function', 'model_service_find',{ if_not_exists= true})



function model_service_exists(key)
    local count = box.space.service:count(key)
    return count ~= 0
end

box.schema.func.create('model_service_exists', {if_not_exists = true})
box.schema.user.grant('user', 'execute', 'function', 'model_service_exists',{ if_not_exists= true})



function model_service_destroy()
    box.space.service:truncate()
end
box.schema.func.create('model_service_destroy', {if_not_exists = true})
box.schema.user.grant('user', 'execute', 'function', 'model_service_destroy',{ if_not_exists= true})



function model_service_list()
    local space = box.space['service']
    local keys = {}
    for _, v in space:pairs() do
        table.insert(keys, v[1])
    end

    return keys
end

box.schema.func.create('model_service_list', {if_not_exists = true})
box.schema.user.grant('user', 'execute', 'function', 'model_service_list',{ if_not_exists= true})

