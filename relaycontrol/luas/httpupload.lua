--upload a file, use uploader.py, that can remove comment automatically (but multiline comment is not supported)
--http server is also serve html with form that can be used to upload file
--overwritten file on the nodemcu will be backed up in name.bak
--if filename is run.lua, it will be executed upon upload after 3 seconds, but must be short and fit in one part (multipart upload handled automatically)
led = 5
cs = "coapserver"
udpSocket = "udpsocket"
tcpsocket = "tcpsocket"

httpupload_bt = 8
gpio.mode(httpupload_bt, gpio.INPUT, gpio.PULLUP)
--gpio.write(httpupload_bt, 0)

clients_connected = 0

local hex_to_char = function(x)
  return string.char(tonumber(x, 16))
end

local unescape = function(url)
  url = url:gsub("%+", " ")
  return url:gsub("%%(%x%x)", hex_to_char)
end

last_written_time = 0
last_written_filename = ""
srv =nil
function init()
  if (src~=nil) then--redundant thuogh, the only way to trigger this getting stopped/unregistered before triggering this (httpupload_bt_check_looper)
    print("net init http triggered, but it's already running")
    return
  end
  srv = net.createServer(net.TCP)
  print("listening to http - v:2020-01-10-16:07")
  srv:listen(80, function(server)
    server:on("receive", function(sck, payload)
      sck:send("HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n <form method='post' action='/'><input type='file' name='file'/><button>ok</button></form>")
      print("http payload: ")
      print(payload)
      local target_file = payload:match("filename=%\"(.+%.lua)%\"\r\n")
      print("getting filename:")
      print(target_file)
      print("that's the filename")
      --lua regex escape sequence use %, %\" means "
      if (target_file==nil) then
        --following payload might not have the header
        if (tmr.now()-last_written_time)<1000000 then
          --less than 1sec, probably was continuing payload
          target_file = last_written_filename
          print("continue write append at "..target_file)
          local f = file.open(target_file, "a")
          f:write(payload)
          f:close()
          print("----this line is for shell mark and not included----")
          --print(payload)
          print("----this line is for shell mark and not included----")
          return true
        end
        print('payload ignored')
        return false
      end
      --not caught there it means the first part of post multipart
      --make a first line in a file
      local file_exist = file.exists(target_file)
      print("exist? ")
      print(file_exist)
      if (file_exist) then
        print("backing up into [name].lua.bak")
        file.remove(target_file..".bak")--remove old bak
        file.rename(target_file, target_file..".bak")
        
      end
      print("writing to file")
      --we cut the first line which is hash for multipart-post id
      --and 2nd line which is the header of the post. both line go like this
      -- --8d8c152e9f83308ab87c8e6032ae6cab
      -- Content-Disposition: form-data; name="file"; filename="test.lua"
      local filenamelength = target_file:len()
      local prepos = payload:find('filename')
      -- filename="" --this len is 11
      print(node.heap())
      tosave = payload:sub(prepos+11+filenamelength)
      print(node.heap())
      local f = file.open(target_file, "w")
      f:write(tosave)
      f:close()
      last_written_filename = target_file
      last_written_time = tmr.now()
      print("----this line is for shell mark and not included----")
      --print(payload)
      print("----this line is for shell mark and not included----")
      if (target_file=="run.lua") then
        t = tmr.create()
        t:register(3000, tmr.ALARM_SINGLE,
          function (timerobject)
            dofile("run.lua")
          end
        )
        t:start()

      end
      return true

    end)
    server:on("sent", function(sck) sck:close() end)
  end)
end

function when_wifi_ready()
  init()
end

function connect(ssid_name,password,on_connect_callback)
    wifi.setmode(wifi.STATION)
    --~ wifi.setphymode(wifi.PHYMODE_B)
    ssid = {}
    ssid.ssid = ssid_name
    ssid.pwd = password
    ssid.auto = false
    ssid.save = false
    ssid.stadisconnected_cb = function(ssid,bssid,channel)
        print("disconnected wifi")
    end
    wifi.sta.config(ssid)
    wifi.sta.connect(on_connect_callback)
end

api = {}
api.init = init
api.connect = connect
return api

