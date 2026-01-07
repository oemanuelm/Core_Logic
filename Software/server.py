import json
import threading
from flask import Flask, render_template
import paho.mqtt.client as mqtt
import database_sqlite

app = Flask(__name__)

# Variáveis de Cache para exibição rápida
cache = {
    "cpu_temp": 0,
    "amb_temp": 0,
    "amb_umid": 0,
    "last_update": "Aguardando..."
}

# --- LÓGICA MQTT ---
def on_message(client, userdata, msg):
    topic = msg.topic
    try:
        payload = json.loads(msg.payload.decode())
        
        if topic == "UFPA/Core-Logic/cpu":
            temp = float(payload.get("cpu_temp", 0))
            cache["cpu_temp"] = temp
            cache["last_update"] = payload.get("timestamp", "")
            database_sqlite.salvar_cpu(temp)
            print(f"[PC] CPU: {temp}°C")

        elif topic == "UFPA/Core-Logic/ambiente":
            temp = float(payload.get("temp", 0))
            umid = float(payload.get("umid", 0))
            cache["amb_temp"] = temp
            cache["amb_umid"] = umid
            database_sqlite.salvar_ambiente(temp, umid)
            print(f"[ESP32] Amb: {temp}°C | Umid: {umid}%")

    except Exception as e:
        print(f"Erro no parse MQTT: {e}")

def iniciar_mqtt():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect("broker.hivemq.com", 1883, 60)
    # Assina os dois tópicos
    client.subscribe("UFPA/Core-Logic/cpu")
    client.subscribe("UFPA/Core-Logic/ambiente")
    client.loop_forever()

# --- ROTAS FLASK ---
@app.route("/")
def index():
    historico_cpu = database_sqlite.get_historico_cpu()
    labels = [row[0] for row in historico_cpu]
    values = [row[1] for row in historico_cpu]
    
    return render_template("index.html", 
                           data=cache, 
                           labels=labels, 
                           values=values)

if __name__ == "__main__":
    database_sqlite.init_db()
    
    # Thread para o MQTT não travar o site
    t = threading.Thread(target=iniciar_mqtt)
    t.daemon = True
    t.start()
    
    app.run(debug=True, port=5000)