import serial
import time
import json
import psutil
import paho.mqtt.client as mqtt

# --- CONFIGURAÇÕES ---
THINGSBOARD_HOST = "thingsboard.cloud" 
ACCESS_TOKEN = "o3qyqdPdKAn3wEMaw2u5" # <--- INSIRA SEU TOKEN DE DISPOSITIVO DO THINGSBOARD
SERIAL_PORT = "COM5"   # <--- CONFIRA SUA PORTA CONECTADA AO ESP32 (No Linux: /dev/ttyUSB0)         
BAUD_RATE = 115200

# Limite de Alerta (Se CPU passar disso, acende o LED no ESP32)
LIMITE_ALERTA_CPU = 80.0 

# --- CONEXÃO MQTT ---
client = mqtt.Client()
client.username_pw_set(ACCESS_TOKEN)
client.connect(THINGSBOARD_HOST, 1883, 60)
client.loop_start()

def get_cpu_temp():
    try:
        # Tenta pegar a temperatura 
        temps = psutil.sensors_temperatures()
        if not temps: return 0.0
        # Pega a primeira temperatura disponível do core
        for name, entries in temps.items():
            if entries: return entries[0].current
        return 0.0
    except:
        # Fallback para Windows (onde psutil as vezes não pega temp)
        # Se estiver no Windows e der 0, considere usar bibliotecas como OpenHardwareMonitor
        return 0.0 

print(f"Conectando ao CoreSense na porta {SERIAL_PORT}...")

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2) # Espera o ESP32 reiniciar
    print("Iniciado! Pressione Ctrl+C para parar.")

    while True:
        if ser.in_waiting > 0:
            try:
                # 1. LER DADOS DO ESP32
                linha = ser.readline().decode('utf-8').strip()
                dados_esp = json.loads(linha)
                
                # 2. LER DADOS DO PC
                temp_cpu = get_cpu_temp()
                
                # Se psutil retornar 0, simulamos para teste
                if temp_cpu == 0: temp_cpu = 45.0 

                # 3. LÓGICA DE FEEDBACK 
                # Se a CPU estiver fritando, manda ligar o LED no ESP32
                if temp_cpu > LIMITE_ALERTA_CPU:
                    ser.write(b'R') # Envia comando 'R' (Red/Risk)
                    status_led = "ALERTA (LED ON)"
                else:
                    ser.write(b'N') # Envia comando 'N' (Normal)
                    status_led = "NORMAL (LED OFF)"

                # 4. MONTAR PACOTE FINAL
                payload = {
                    "temp_amb": dados_esp['temp_amb'],
                    "umidade": dados_esp['umidade'],
                    "temp_cpu": temp_cpu
                }

                # 5. ENVIAR PARA THINGSBOARD
                client.publish("v1/devices/me/telemetry", json.dumps(payload))
                
                print(f"Enviado: CPU {temp_cpu}°C | Amb {dados_esp['temp_amb']}°C | {status_led}")

            except json.JSONDecodeError:
                pass # Ignora linhas incompletas
            except Exception as e:
                print(f"Erro: {e}")
                
except KeyboardInterrupt:
    print("\nDesligando...")
    ser.close()
    client.loop_stop()