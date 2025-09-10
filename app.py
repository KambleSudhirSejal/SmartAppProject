from sqlite3.dbapi2 import Timestamp
from flask import Flask, json, render_template ,request ,jsonify
import paho.mqtt.client  as mqtt
import random
import database


app = Flask(__name__)

# mqtt config
broker="broker.hivemq.com"
port=1883
topic="tubeF0BF01/control"
client=mqtt.Client()

# latest_state=({"toggle":0,"intensity":"50"})   #store last received value

def generate_random_device_data(intensity,device_status):
    device_id = "tubeF0BF0" + str(random.randint(1,5))
    temperature = round(random.uniform(25.6,45.5),1)
    auto_brightness_status = random.randint(0,1)
    auto_motion_status = random.randint(0,1)
    power = 48
    lux = random.randint(0,1500)

    return f"{device_id}:{intensity}:{device_status}:{temperature}:{auto_brightness_status}:{auto_motion_status}:{power}:{lux}"


latest_data={"toggle":0,"intensity_value":50}



def on_message(client , userdate, msg):
    global latest_data
    
    try:
        data=json.loads(msg.payload.decode())
        latest_data=data
        print("received from mqtt",latest_data)
        
        if "deviceData" in data:
            parts=data["deviceData"].split(':')
            database.insert_Data(
                    device_id=parts[0],
                    intensity=int(parts[1]),
                    device_status=int(parts[2]),
                    temperature=float(parts[3]),
                    auto_brightness_status=int(parts[4]),
                    auto_motion_status=int(parts[5]),
                    power=int(parts[6]),
                    lux=int(parts[7])
            )
            
            latest_data={
                "toggle":int(parts[2]),
                "intensity":int(parts[1])
            }
            
        
    except Exception as e:
        print("Error parsing",e)
        
client.on_message=on_message
client.connect(broker,port,60)
client.subscribe(topic)
client.loop_start()
        


@app.route('/')
def home():
    return render_template("index.html")   # serve the HTML page

@app.route('/publish', methods=['POST'])

def message_publish():
    data=request.get_json()
    toggle_value=data.get("toggle",0)
    intensity_value=data.get("intensity",0)
    
    try:
        toggle_value=(int)(toggle_value)
        intensity_value=(int)(intensity_value)
        if toggle_value not in[0,1]:
            raise ValueError
        if not 0<=intensity_value<=100:
            raise ValueError
        
    except:
        return jsonify({"error":"invalid value"}),400
            
    
    device_status = 1 if toggle_value == 1 else 0
    message = {
        "deviceData": generate_random_device_data(intensity_value,device_status)
        }
    client.publish(topic,json.dumps(message))
    print(f"published:{message}")
    return jsonify({"message":f"published{message}"}),200

#new endpoint to get the latest data
@app.route('/get_state',methods=['GET'])
def get_state():
    return jsonify(latest_data)


@app.route('/devices',methods=['GET'])
def show_data():
    data=database.get_all_data()
    return jsonify(data)

@app.route('/devices/hourly',methods=['GET'])
def all_devices_hourly():
    data = database.get_calculate_power()
    return jsonify(data)
    

if __name__ == '__main__':
    database.create_table()
    app.run(debug=True,use_reloader=False)