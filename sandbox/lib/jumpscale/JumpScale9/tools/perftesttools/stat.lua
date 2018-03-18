
--key,measurement,value,str(now),type,tags

local key=KEYS[1]
local measurement=ARGV[1] --remove ?
local value = tonumber(ARGV[2])
local now = tonumber(ARGV[3])
local type=ARGV[4]
local tags=ARGV[5]
local node=ARGV[6]

local hsetkey =string.format("stats:%s",node)
local v= {}
local c=""
local m
local prev = redis.call('HGET',hsetkey,key)

-- TODO: per 5 min in stead of per 1 min

if prev then
    -- get previous value, it exists in a hkey
    v = cjson.decode(prev)
    local diff
    local difftime

    -- calculate the dif when absolute nrs are logged e.g. byte counter for network
    if type=="D" then
        -- diff
        diff = tonumber(value)-v["val"]
        difftime = now-v["epoch"]
        m=math.floor((diff/difftime)+0.5)
    else
        m=tonumber(value)
    end

    -- the next section makes sure we start recounting
    if v["m_epoch"]< (now-60) then
        v["m_total"]=0
        v["m_nr"]=0
        v["m_epoch"] = now
    end
    if v["h_epoch"]< (now-(60*60)) then
        v["h_total"]=0
        v["h_nr"]=0
        v["h_epoch"] = now
    end

    --remember current measurement, and calculate the avg/max for minute value
    v["m_epoch"]= now
    v["m_last"]=m
    v["m_total"]=v["m_total"]+m
    v["m_nr"]=v["m_nr"]+1
    v["m_avg"]= v["m_total"]/v["m_nr"]
    if m>v["m_max"] then
        v["m_max"]=m
    end

    -- remember the current value
    v['val'] = value
    v["epoch"]= now

    -- work for the hour period
    v["h_epoch"]= now
    --h_last is not required would not provide additional info
    v["h_total"]=v["h_total"]+m
    v["h_nr"]=v["h_nr"]+1
    v["h_avg"]= v["h_total"]/v["h_nr"]
    if m>v["h_max"] then
        v["h_max"]=m
    end

    -- remember in redis
    data=cjson.encode(v)
    redis.call('HSET',hsetkey,KEYS[1],data)

    -- epoch in seconds
    local nowshort=math.floor(now/1000+0.5)

    -- TODO: only put to queue if last one longer than 5 min ago

    c=string.format("%s|%u|%u|%u|%u|%u|%u",key,nowshort,m,v["m_avg"],v["m_max"],v["h_avg"],v["h_max"])

    if redis.call("LLEN", "queues:stats") > 200000 then
        redis.call("LPOP", "queues:stats")
    end
    redis.call("RPUSH", "queues:stats",c)
    return data
else
    v["m_avg"]= 0
    v["m_last"]= 0
    v["m_epoch"]= now
    v["m_total"]= value
    v["m_max"]= 0
    v["m_nr"]= 0
    v["h_avg"]= 0
    v["h_epoch"]= now
    v["h_total"]= 0
    v["h_nr"]= 0
    v["h_max"]= 0
    v["epoch"]= now
    v["val"]= value
    v["key"]=key
    v["tags"]=tags
    v["measurement"]=measurement
    redis.call('HSET',hsetkey,KEYS[1],cjson.encode(v))
    return 0
end
