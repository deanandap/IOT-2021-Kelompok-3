import dht
import network
import ntptime
import ujson
import utime


from machine import RTC
from machine import Pin
from time import sleep
from third_party import rd_jwt

from umqtt.simple import MQTTClient


# Konstanta-konstanta aplikasi

# WiFi AP Information
AP_SSID = "iphone11"
AP_PASSWORD = "advang5pro"

# Decoded Private Key
PRIVATE_KEY = (28084409744293750599934214201095295718103736536486395463194392826137235451022068114898939406295559533670574357652059334667058983101319599103169504953782718951820582828041951752720125946899573138111220964429820745779528908855572015851044554672289186992875219003778792107304722881523208237155146538388309390640219652169160331717868526274274697060404129634915806827466024427270966290194235012420106724223788537762961798986320229996521349703417351795167000220869932467034413596647328384505916318970439262179341400221451197572371543598372478951019142563724190244580409933338324095623679647271150735727131933080123568708339, 65537, 15780098332604072082823099985369076544905198501908464326055057775450166444122200226788509463317327376411572549036108350088954025874284647105835083241803787824920901812103343627907379310444937687684935239546572457429930764906809648163615433743570456716444711607109727948477792932072121398980745474001115476767674618601598343447796929296455535121843551889340269536823102762751786894467500310980459069685615926776817018062213883128701264824386072177221954717994802922558873921989207156996200442677440059090261882563026426912366217902584913945428504886669119506342402104213091233629118923908706346362674367331872839149121, 175983614917947664550824525000836435231775457968614933470295516491809758455669275327361784508979427745332620649887733936056251571064919276854893750450037647345877516617044672873826501180629166316065603020836882378027234741925160289707085169236748041094532540085811927987959481013195032753011753835504949140823, 159585366838771340460126382616072082910219151645941496570797187922762394688908777481449424562022585110713663651897647629938952336246903182047842774101586131448776134738988104200523762723782799735791194834411215570301705590052915412301957330463053623017649968100074622058065188085978519029665747031145062666693)

#Project ID of IoT Core
PROJECT_ID = "iot-2021-tim-03"
# Location of server
REGION_ID = "asia-east1"
# ID of IoT registry
REGISTRY_ID = "kelompok3"
# ID of this device
DEVICE_ID = "coba_coba"

# MQTT Information
MQTT_BRIDGE_HOSTNAME = "mqtt.googleapis.com"
MQTT_BRIDGE_PORT = 8883


dht22_obj = dht.DHT22(Pin(4))
led_obj = Pin(21, Pin.OUT)
def suhu():
    # Read temperature from DHT 22
    #
    # Return
    #    * List (temperature, humidity)
    #    * None if failed to read from sensor
    while True:
        try:
            dht22_obj.measure()
            return dht22_obj.temperature()
            sleep(3)
            break
        except:
            return None
def connect():
    # Connect to WiFi
    print("Connecting to WiFi...")
    
    # Activate WiFi Radio
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    # If not connected, try tp connect
    if not wlan.isconnected():
        # Connect to AP_SSID using AP_PASSWORD
        wlan.connect(AP_SSID, AP_PASSWORD)
        # Loop until connected
        while not wlan.isconnected():
            pass
    
    # Connected
    print("  Connected:", wlan.ifconfig())


def set_time():
    # Update machine with NTP server
    print("Updating machine time...")

    # Loop until connected to NTP Server
    while True:
        try:
            # Connect to NTP server and set machine time
            ntptime.settime()
            # Success, break out off loop
            break
        except OSError as err:
            # Fail to connect to NTP Server
            print("  Fail to connect to NTP server, retrying (Error: {})....".format(err))
            # Wait before reattempting. Note: Better approach exponential instead of fix wiat time
            utime.sleep(0.5)
    
    # Succeeded in updating machine time
    print("  Time set to:", RTC().datetime())


def on_message(topic, message):
    print((topic,message))


def get_client(jwt):
    #Create our MQTT client.
    #
    # The client_id is a unique string that identifies this device.
    # For Google Cloud IoT Core, it must be in the format below.
    #
    client_id = 'projects/{}/locations/{}/registries/{}/devices/{}'.format(PROJECT_ID, REGION_ID, REGISTRY_ID, DEVICE_ID)
    client = MQTTClient(client_id.encode('utf-8'),
                        server=MQTT_BRIDGE_HOSTNAME,
                        port=MQTT_BRIDGE_PORT,
                        user=b'ignored',
                        password=jwt.encode('utf-8'),
                        ssl=True)
    client.set_callback(on_message)

    try:
        client.connect()
    except Exception as err:
        print(err)
        raise(err)

    return client


def publish(client, payload):
    # Publish an event
    
    # Where to send
    mqtt_topic = '/devices/{}/{}'.format(DEVICE_ID, 'events')
    
    # What to send
    payload = ujson.dumps(payload).encode('utf-8')
    
    # Send    
    client.publish(mqtt_topic.encode('utf-8'),
                   payload,
                   qos=1)
    
    
def subscribe_command2():
    print("Sending command to device")
    client_id = 'projects/{}/locations/{}/registries/{}/devices/{}'.format(PROJECT_ID, REGION_ID, REGISTRY_ID, DEVICE_ID)
    command = 'suhu_sekarang'
    data = command.encode("utf-8")
    while True:
        dht22_obj.measure()
        suhu = dht22_obj.temperature()
        print(suhu)
        break
           
   
# Connect to Wifi
connect()
# Set machine time to now
set_time()

# Create JWT Token
print("Creating JWT token.")
start_time = utime.time()
jwt = rd_jwt.create_jwt(PRIVATE_KEY, PROJECT_ID)
end_time = utime.time()
print("  Created token in", end_time - start_time, "seconds.")

# Connect to MQTT Server
print("Connecting to MQTT broker...")
start_time = utime.time()
client = get_client(jwt)
end_time = utime.time()
print("  Connected in", end_time - start_time, "seconds.")

# Read from DHT22
#print("Reading from DHT22")
#result1 = suhu()
#print("Suhu", result1)
# Publish a message
#print("Publishing message...")
#if result1 == None:
 # result1 = "Fail to read sensor...."


#publish(client, result1)
# Need to wait because command not blocking
utime.sleep(1)

# Disconnect from client
client.disconnect()
#publish_events()
#publish_state()
#subscribe_config()
#subscribe_command()
#subscribe_command1()
subscribe_command2()
#subscribe_command3()
