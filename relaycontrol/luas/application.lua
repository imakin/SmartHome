led = 5
driverIN1 = 1
driverIN2 = 2
driverIN3 = 3
driverIN4 = 4

function relay_init()
  gpio.mode(driverIN1, gpio.OUTPUT)
  gpio.mode(driverIN2, gpio.OUTPUT)
  gpio.mode(driverIN3, gpio.OUTPUT)
  gpio.mode(driverIN4, gpio.OUTPUT)
  gpio.mode(led, gpio.OUTPUT)
  gpio.write(driverIN1, 1)
  gpio.write(driverIN2, 1)
  gpio.write(driverIN3, 1)
  gpio.write(driverIN4, 1)
  gpio.write(led, 1)
  

  return "init"
end

relay_init()
h = dofile("httpupload.lua")
h.connect("recording_your_data", "ldks297599_--", h.init)

-- when nodemcu powered, i want to switch on and off the relay, to trigger my PC to always on (bios doesnt have built in always on feature)
-- but do this only after 10 seconds of startup


pc_timer = tmr.create()
pc_timer:register(1000, tmr.ALARM_SINGLE,
  function (timerobject)
    gpio.write(driverIN1, 0)
    tmr.delay(800000)
    gpio.write(driverIN1, 1)
  end
)
pc_timer:start()
