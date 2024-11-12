import network
import machine
import time
from BlynkLib import Blynk

WIFI_SSID = "SSID"
WIFI_PASSWORD = "Password"

AUTH_TOKEN = "Write_Your_Authenticatio_token"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
   
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
       
        timeout = 0
        while not wlan.isconnected() and timeout < 10:
            time.sleep(1)
            timeout += 1
           
    if wlan.isconnected():
        print("WiFi connected")
        print("Network config:", wlan.ifconfig())
        return True
    else:
        print("WiFi connection failed")
        return False

def main():
    if not connect_wifi():
        print("Could not connect to WiFi. Exiting...")
        return

    blynk = Blynk(AUTH_TOKEN, server="blynk.cloud", port=80, insecure=True)
   
    adc_pin = machine.Pin(34)
    adc = machine.ADC(adc_pin)
    adc.width(machine.ADC.WIDTH_12BIT)
    adc.atten(machine.ADC.ATTN_0DB)

    @blynk.on("connected")
    def blynk_connected(ping):
        print('Blynk ready. Ping:', ping, 'ms')

    @blynk.on("disconnected")
    def blynk_disconnected():
        print('Blynk disconnected')
   
    @blynk.on("v1")
    def v2_write_handler(value):
        print('V2 value update:', value)

    last_read = 0
    READ_INTERVAL = 500  

    while True:
        try:
            blynk.run()

            current_time = time.ticks_ms()
            if time.ticks_diff(current_time, last_read) >= READ_INTERVAL:
                sound_value = adc.read()
                scaled_value = (sound_value * 100) // 4095

                print("Sound Level:", scaled_value)
               
                try:
                    blynk.virtual_write(0, scaled_value)

                except Exception as e:
                    print("Failed to send data to Blynk:", e)
               
                last_read = current_time

        except KeyboardInterrupt:
            print("Program terminated by user")
            break
        except Exception as e:
            print("Main loop error:", e)
            time.sleep(5)

if __name__ == "__main__":
    main()
