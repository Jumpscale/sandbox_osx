
box.schema.space.create('template',{if_not_exists= true, engine="memtx"})

box.space.template:create_index('primary',{ type = 'tree', parts = {1, 'string'}, if_not_exists= true})   --md5hash of the full unc path (is without version)

box.space.template:create_index('secondary', {type = 'tree', parts = {2, 'string'}, if_not_exists= true}) --githost
box.space.template:create_index('secondary', {type = 'tree', parts = {3, 'string'}, if_not_exists= true}) --account
box.space.template:create_index('secondary', {type = 'tree', parts = {4, 'string'}, if_not_exists= true}) --repo
box.space.template:create_index('secondary', {type = 'tree', parts = {5, 'string'}, if_not_exists= true}) --brach
box.space.template:create_index('secondary', {type = 'tree', parts = {6, 'string'}, if_not_exists= true}) --name
box.space.template:create_index('secondary', {type = 'tree', parts = {7, 'unsigned'}, if_not_exists= true}) --version

box.schema.user.create('user', {password = 'secret', if_not_exists= true})

emptyModel = {
    ["guid"] = "",
    [""] = "",
    [""] = "",
    [""] = "",
    [""] = "",
    [""] = "",
}

function model_template_get(key)
    return box.space.template:get(key)
    -- if type(key) == 'number' then
    --     return box.space.template:get(key)
    -- end
    -- return box.space.template.index.secondary:get(key)
end

box.schema.func.create('model_template_get', {if_not_exists = true})
box.schema.user.grant('user', 'execute', 'function', 'model_template_get',{ if_not_exists= true})



function model_template_get_json(key)
    if key==nil then


    end
    local res = model_template_get(key)
    if res == nil then
        return nil
    else
        return model_capnp_template.Template.parse(res[3])
    end
end

box.schema.func.create('model_template_get_json', {if_not_exists = true})
box.schema.user.grant('user', 'execute', 'function', 'model_template_get_json',{ if_not_exists= true})



function model_template_set(key, data)
    local obj = model_capnp_template.Template.parse(data) --deserialze capnp
    -- local name = obj["name"]
    -- res0 = model_template_get(name)
    -- if res0 == nil then
    --     res = box.space.template:auto_increment({obj['name'],data}) -- indexes the name
    --     id = res[1]
    -- else
    --     id = res0[1]
    -- end
    -- obj["id"] = id
    -- data = model_capnp_template.Template.serialize(obj) --reserialze with id inside
    box.space.template:put{key, data}
    return
end

box.schema.func.create('model_template_set', {if_not_exists = true})
box.schema.user.grant('user', 'execute', 'function','model_template_set',{ if_not_exists= true})



function model_template_delete(key)
    box.space.template:delete(key)
end
box.schema.func.create('model_template_delete', {if_not_exists = true})
box.schema.user.grant('user', 'execute', 'function', 'model_template_delete',{ if_not_exists= true})



function model_template_find(query)
    local obj = model_capnp_template.Template.parse(data) --deserialze capnp
    res={}
    return res
end

box.schema.func.create('model_template_find', {if_not_exists = true})
box.schema.user.grant('user', 'execute', 'function', 'model_template_find',{ if_not_exists= true})



function model_template_exists(key)
    local count = box.space.template:count(key)
    return count ~= 0
end

box.schema.func.create('model_template_exists', {if_not_exists = true})
box.schema.user.grant('user', 'execute', 'function', 'model_template_exists',{ if_not_exists= true})



function model_template_destroy()
    box.space.template:truncate()
end
box.schema.func.create('model_template_destroy', {if_not_exists = true})
box.schema.user.grant('user', 'execute', 'function', 'model_template_destroy',{ if_not_exists= true})



function model_template_list()
    local space = box.space['template']
    local keys = {}
    for _, v in space:pairs() do
        table.insert(keys, v[1])
    end

    return keys
end

box.schema.func.create('model_template_list', {if_not_exists = true})
box.schema.user.grant('user', 'execute', 'function', 'model_template_list',{ if_not_exists= true})

