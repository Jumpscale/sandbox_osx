fiber = require('fiber')

function dog1(animal,channel)
    -- print(animal["name"])
    function animal:pprint()
        print(animal)
    end
    function animal:isalive()
        return "yes"
    end
    function animal:returnName()
        print(animal["name"])
        return animal["name"]
    end

    while true do
        local task = channel:get(10)
        if task == "crash" then
            -- q=q/0
            error("an error")
        end
        if task  then
            print("task")
            print(task)
            -- require('tdb').start()        
            loadstring(task)()
        end
        
    end

end


fibers = {}
for i=1,1000 do 
    animal = {}
    animal["name"]="something"..i
    animal["name3"]="something"
    animal["name4"]="something"
    -- animal["name5"]="something"
    animal["nr"]=i
    channel= fiber.channel(5)
    fibers[i] = {fiber.create(dog1,animal,channel),channel}
end


--call channel
-- fibers[1][2]:put("sometask") 

fibers[9][2]:put("crash") 

w=fibers[1][2]:put("animal:returnName()") 
w=fibers[1][2]:put("animal:pprint()") 

