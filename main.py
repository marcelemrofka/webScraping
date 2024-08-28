#marcele

import tkinter as tk
from tkinter import messagebox, filedialog
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import pandas as pd
import openai
import os
import time

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Função captura os dados
def buscar_avaliacoes_reclame_aqui(empresa):
    options = Options()
    options.add_argument('--log-level=3')
    driver_path = 'C:/Users/teste/chromedriver-win64/chromedriver.exe'
    
    service = Service(driver_path)

    try:
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao inicializar o WebDriver: {str(e)}")
        return []

    try:
        url = f"https://www.reclameaqui.com.br/busca/?q={empresa.replace(' ', '-')}"
        driver.get(url)
        time.sleep(5)
        avaliacoes = []
        resultados = driver.find_elements(By.CSS_SELECTOR, 'div.complain-item.ng-scope')

        for resultado in resultados:
            try:
                titulo = resultado.find_element(By.CSS_SELECTOR, 'h2.ng-binding').text.strip()
                descricao = resultado.find_element(By.CSS_SELECTOR, 'p.complaint-content').text.strip()
                status = resultado.find_element(By.CSS_SELECTOR, 'span.status-text').text.strip()
                
                avaliacoes.append({
                    'Título': titulo,
                    'Descrição': descricao,
                    'Status': status
                })

            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao extrair avaliação: {str(e)}")

        return avaliacoes

    finally:
        driver.quit()

def salvar_como_csv(empresa, avaliacoes):
    nome_arquivo = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
    if nome_arquivo:
        df = pd.DataFrame(avaliacoes)
        df.to_csv(nome_arquivo, index=False)
        messagebox.showinfo("Sucesso", f"Dados salvos com sucesso em '{nome_arquivo}'")

def avaliar(empresa, avaliacoes):
    try:
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",
            prompt=f"Avalie o seguinte texto, nele contém uma avaliação sobre a empresa {empresa} e me forneça em poucas palavras algumas sugestões de melhora: \n\n'{avaliacoes}'",
            temperature=0.7,
            max_tokens=2048,
            n=1,
            stop=None
        )
        return response['choices'][0]['text'].strip()
    except Exception as e:
        return f"Erro ao avaliar o texto: {str(e)}"

def buscar():
    empresa = entry_empresa.get()
    if not empresa:
        messagebox.showwarning("Aviso", "Por favor, insira o nome da empresa.")
        return

    avaliacoes = buscar_avaliacoes_reclame_aqui(empresa)
    if avaliacoes:
        sugestao = avaliar(empresa, avaliacoes)
        text_sugestao.config(state=tk.NORMAL)
        text_sugestao.delete(1.0, tk.END)
        text_sugestao.insert(tk.END, sugestao)
        text_sugestao.config(state=tk.DISABLED)
        btn_salvar.config(state=tk.NORMAL)
    else:
        messagebox.showinfo("Info", "Não foi possível obter as avaliações.")

def salvar():
    empresa = entry_empresa.get()
    avaliacoes = buscar_avaliacoes_reclame_aqui(empresa)
    if avaliacoes:
        salvar_como_csv(empresa, avaliacoes)

# Criação da janela principal
root = tk.Tk()
root.title("Reclame Aqui Avaliações")

# Elementos da interface
frame = tk.Frame(root)
frame.pack(pady=20)

label_empresa = tk.Label(frame, text="Nome da Empresa:")
label_empresa.grid(row=0, column=0, padx=10, pady=10)

entry_empresa = tk.Entry(frame, width=50)
entry_empresa.grid(row=0, column=1, padx=10, pady=10)

btn_buscar = tk.Button(frame, text="Buscar Avaliações", command=buscar)
btn_buscar.grid(row=1, column=0, columnspan=2, pady=10)

label_sugestao = tk.Label(root, text="Sugestão de Melhoria:")
label_sugestao.pack(pady=10)

text_sugestao = tk.Text(root, height=10, width=80, state=tk.DISABLED)
text_sugestao.pack(pady=10)

btn_salvar = tk.Button(root, text="Salvar como CSV", command=salvar, state=tk.DISABLED)
btn_salvar.pack(pady=20)

# Inicia a aplicação
root.mainloop()