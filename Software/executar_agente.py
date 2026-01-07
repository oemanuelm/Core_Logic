import time
import json
import threading
import serial 
import serial.tools.list_ports
import psutil
import paho.mqtt.client as mqtt
from datetime import datetime

# --- CONFIGURAÇÕES ---
BROKER = "broker.hivemq.com"
TOPIC_CPU = "UFPA/Core-Logic/cpu"
TOPIC_AMB = "UFPA/Core-Logic/ambiente"

# Tenta detectar a porta do ESP32 automaticamente
def encontrar_porta_esp32():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "USB" in port.description:
            return port.device
    return None

# --- THREAD DE LEITURA USB (ESP32) ---
def ler_sensor_usb(client_mqtt):
    porta = encontrar_porta_esp32()
    if not porta:
        print("[!] ESP32 não detectado no USB. Verifique a conexão.")
        return

    print(f"[*] ESP32 detectado na porta: {porta}")
    
    try:
        # Conecta no Serial (Mesma velocidade do código C++: 115200)
        ser = serial.Serial(porta, 115200, timeout=1)
        time.sleep(2) # Espera conexão estabilizar

        while True:
            if ser.in_waiting > 0:
                try:
                    # Lê a linha enviada pelo ESP32
                    linha = ser.readline().decode('utf-8').strip()
                    
                    # Tenta converter o texto em JSON
                    dados = json.loads(linha)
                    
                    # Se deu certo, publica no MQTT
                    client_mqtt.publish(TOPIC_AMB, json.dumps(dados))
                    print(f"[USB->MQTT] Ambiente: {dados}")
                    
                except json.JSONDecodeError:
                    pass # Ignora linhas incompletas
            time.sleep(0.1)
            
    except Exception as e:
        print(f"[!] Erro na conexão USB: {e}")

# --- LOOP PRINCIPAL (CPU) ---
def main():
    # 1. Configura MQTT
    client = mqtt.Client()
    client.connect(BROKER, 1883, 60)
    
    # 2. Inicia a leitura do USB em paralelo (Thread)
    thread_usb = threading.Thread(target=ler_sensor_usb, args=(client,))
    thread_usb.daemon = True # Morre se o programa principal fechar
    thread_usb.start()

    print(f"[*] Gateway Core-Logic Iniciado.")

    # 3. Loop da CPU
    while True:
        try:
            # Lê CPU (Simples via psutil)
            temps = psutil.sensors_temperatures()
            temp_cpu = 0
            if 'coretemp' in temps:
                temp_cpu = temps['coretemp'][0].current
            # (Adicione aqui a lógica de WMI do Windows se necessário, igual ao anterior)
            
            payload = {
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "cpu_temp": round(temp_cpu, 1)
            }
            
            client.publish(TOPIC_CPU, json.dumps(payload))
            print(f"[PC->MQTT] CPU: {payload['cpu_temp']}°C")
            
            time.sleep(5)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Erro CPU: {e}")

if __name__ == "__main__":
    main()