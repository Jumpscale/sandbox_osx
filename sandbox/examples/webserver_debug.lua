package.path = package.path .. ';lib/?.lua'
 
-- model=require("model")
json=require('json')


box.cfg{}



box.schema.space.create('firstdb', {if_not_exists= true, engine="memtx"})
box.space.firstdb:drop()
box.schema.space.create('firstdb', {if_not_exists= true, engine="memtx"})

box.space.firstdb:create_index('primary', { type = 'hash',parts = {1, 'unsigned'}, if_not_exists= true})
box.space.firstdb:create_index('secondary',{ parts = {3, 'string'}, if_not_exists= true })



http_client = require('http.client').new()

httpCallResults = http_client:request('GET','https://jsonplaceholder.typicode.com/users')

decodedData = json.decode(httpCallResults.body)

for i=1,10,1 do
    box.space.firstdb:insert({
    i, decodedData[i].name, decodedData[i].address.city })
end

print(box.space.firstdb:select())

function debugtest(self)
    local dbg = require("debugger")
    dbg()
end

function debugtest2(self)
    --install see https://github.com/Sulverus/tdb
    require('tdb').start()
end



function handler(self)

    return self:render({ json = box.space.firstdb:select() })
end

function files(self)
    return self:render({ json = box.space.firstdb:select() })
end

function hello(self)
    -- http://localhost:8080/Gwenborough
    local id = self:stash('id')
    local name = box.space.firstdb.index.secondary:select(id) 
    if name[0] == nil then
        return self:render({ user = "ERROR:COULD NOT FIND" })
    end
    local distill = name[1][2]
    return self:render({ user = distill })
    -- return self:render({ user = id })
end

local server = require('http.server').new(nil, 8080) 

server:route({ path = '/:id', template = 'Hello, <%= user %>' }, hello) 
-- server:route({ path = '/files/:path', files) 
server:route({ path = '/'}, handler)
server:route({ path = '/debug1'}, debugtest)
server:route({ path = '/debug2'}, debugtest2)


fiber = require('fiber')


server:start()




function function_name()
    print("fiber start")
    fiber.sleep(1)
    print(fiber.self())
    require('tdb').start()

end

-- fiber_object = fiber.create(function_name)

