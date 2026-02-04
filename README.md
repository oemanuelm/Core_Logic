# 🌡️ CoreSense: Sistema de Telemetria Térmica Integrado

![Status](https://img.shields.io/badge/Status-Finalizado-success)
![Hardware](https://img.shields.io/badge/ESP32-Serial-blue)
![Backend](https://img.shields.io/badge/Python-3.x-yellow)
![Cloud](https://img.shields.io/badge/IoT-ThingsBoard-orange)

> **Resumo:** Sistema IoT para correlação de temperatura interna (CPU) e externa (Ambiente) voltado para manutenção preditiva em Data Centers.

---

## 📖 Sobre o Projeto
O **CoreSense** resolve o problema da "cegueira de diagnóstico" em computadores de alto desempenho. Ele cruza dados de sensores físicos e lógicos para determinar se um superaquecimento é causado por falha no hardware (ex: pasta térmica seca) ou por saturação do ar-condicionado da sala.

### ✨ Principais Funcionalidades
* **Monitoramento Híbrido:** Leitura simultânea do sensor DHT22 (Ambiente) e Kernel do Sistema Operacional (CPU).
* **Arquitetura Serial Gateway:** Elimina a instabilidade do Wi-Fi no microcontrolador, usando conexão USB robusta para dados e energia.
* **Feedback Físico Reativo:** O ESP32 acende um **LED de Alerta** automaticamente se a CPU do PC ultrapassar **80°C**.
* **Dashboard em Nuvem:** Visualização em tempo real via ThingsBoard com gráficos de correlação.

---

## 🛠️ Hardware e Pinagem

### Lista de Componentes
* Microcontrolador **ESP32 DevKit V1**
* Sensor de Temperatura/Umidade **DHT22** (AM2302)
* LED Vermelho (Indicador de Alerta)
* Resistor 220Ω ou 300
* Cabo Micro-USB de dados

### Esquema de Ligação (Wiring)

| Componente | Pino do Componente | Pino do ESP32 | Função |
| :--- | :--- | :--- | :--- |
| **DHT22** | VCC | 3V3 / VIN | Alimentação |
| **DHT22** | DATA | **GPIO 4** | Leitura de Dados |
| **DHT22** | GND | GND | Terra |
| **LED** | Anodo (+) | **GPIO 13** | Sinal de Alerta |
| **LED** | Catodo (-) | GND | Terra (via Resistor) |

---

## 📂 Estrutura do Projeto

```text
/CoreSense_Final
│
├── /Hardware      # Código C++ do Microcontrolador
│   └── esp32-port.ino         # Lógica de leitura e controle do LED via Serial
│
├── /Software      # Agente rodando no PC (Host)
│   ├── gateway_final.py  # Script principal (Serial <-> MQTT)
│   └── requirements.txt # Dependências (pyserial, paho-mqtt, psutil)
│
└── README.md            # Documentação do projeto
````
----
## 🚀 Instalação e Execução
## 1. Preparação do Hardware (ESP32)

* Instale a Arduino IDE.
* Adicione a biblioteca "DHT sensor library" (por Adafruit).
* Carregue o código da pasta /Firmware_ESP32 para a placa.

        Nota: Não é necessário configurar Wi-Fi no código.

## 2. Preparação do Gateway (Computador)
Certifique-se de ter o Python instalado. No terminal:

```bash
cd Gateway_Python
pip install -r requirements.txt
```
## 3. Configuração da Nuvem (ThingsBoard)
   1. Crie um dispositivo no ThingsBoard Cloud
   2. Copie o Access Token.
   3. Edite o arquivo gateway_real.py:

```python
THINGSBOARD_HOST = "thingsboard.cloud"
ACCESS_TOKEN = "SEU_TOKEN_AQUI"  # <--- Cole seu token
SERIAL_PORT = "COM3"             # <--- Ajuste sua porta USB
```
## 4. Rodando o Projeto

Com o ESP32 conectado à USB, execute:

```
python gateway_final.py
```
Você verá o log no terminal:

    Enviado: CPU 45.0°C | Amb 24.5°C | NORMAL (LED OFF)
    
## 📊 Visualização

O Dashboard no ThingsBoard foi configurado com:

    Gráfico TimeSeries: Eixo esquerdo (Temp °C) e Eixo direito (Umidade %).

    Neon Gauges: Indicadores visuais de alto contraste para ambientes escuros (NOCs).

## 👨‍💻 Autores
* Gabriel Santos - Engenharia da Computação (UFPA)
* Emanoel Monteiro - Engenharia da Computação (UFPA)
