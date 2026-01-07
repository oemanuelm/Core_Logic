import sqlite3
from datetime import datetime

DB_NAME = "monitor_temperatura.db"

def init_db():
    """Inicializa o banco de dados e cria as tabelas necessárias."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Tabela para logs da CPU
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS log_cpu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            temperatura REAL
        )
    ''')
    
    # Tabela para logs do Ambiente (ESP32)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS log_ambiente (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            temp_ambiente REAL,
            umidade REAL
        )
    ''')
    conn.commit()
    conn.close()

def salvar_cpu(temp):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    hora = datetime.now().strftime("%H:%M:%S")
    cursor.execute("INSERT INTO log_cpu (timestamp, temperatura) VALUES (?, ?)", (hora, temp))
    conn.commit()
    conn.close()

def salvar_ambiente(temp, umid):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    hora = datetime.now().strftime("%H:%M:%S")
    cursor.execute("INSERT INTO log_ambiente (timestamp, temp_ambiente, umidade) VALUES (?, ?, ?)", (hora, temp, umid))
    conn.commit()
    conn.close()

def get_historico_cpu():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, temperatura FROM log_cpu ORDER BY id DESC LIMIT 20")
    dados = cursor.fetchall()
    conn.close()
    return dados[::-1] # Retorna cronológico

def get_historico_ambiente():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, temp_ambiente, umidade FROM log_ambiente ORDER BY id DESC LIMIT 1")
    dados = cursor.fetchone() # Pega apenas o último dado para mostrar no painel
    conn.close()
    return dados