from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service
from datetime import datetime, timedelta
from dotenv import load_dotenv

import os
import time
import pyautogui

load_dotenv()

usuario_aut_any = os.getenv('USUARIO_AUT_ANY')
senha_aut_any = os.getenv('SENHA_AUT_ANY')
usuario = os.getenv('USUARIO')
senha = os.getenv('SENHA')

def clicar_elemento(browser, by, value):
    try:
        # Localizar e clicar no elemento
        elemento = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((by, value))
        )
        elemento.click()
        
        # Adiciona uma pausa após o clique no elemento
        time.sleep(0.5)
        
    except Exception as e:
        print(f"Erro ao clicar no elemento: {e}")
        
def acessar_sistema(browser):
    clicar_elemento(browser, By.ID, 'onetrust-accept-btn-handler')
    clicar_elemento(browser, By.ID, 'button_modal-login-btn__iPh6x')
    usuario_field = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[id="43:2;a"]'))
        )
    usuario_field.send_keys(usuario_aut_any)
    pyautogui.press('enter')
    senha_field = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[id="10:148;a"]'))
        )
    senha_field.send_keys(senha_aut_any)
    pyautogui.press('enter')
    
def login(browser):
    try:
        # --------------------------------- LOGIN ---------------------------------
        # Preencher o campo de usuário
        usuario_field = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, 'salesOrderInputEmail'))
        )
        usuario_field.send_keys(usuario)
        
        # Preencher o campo de senha
        senha_field = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, 'salesOrderInputPassword'))
        )
        senha_field.send_keys(senha)
        clicar_elemento(browser, By.XPATH, '//a[@onclick="authLogin()"]')
        time.sleep(0.5)
        
    except Exception as e:
        print(f"Erro ao fazer login: {e}")
        
def verificar_order_status(browser):
    try:
        # --------------------------------- VERIFICAR STATUS DO PEDIDO ---------------------------------
        # Clicar no botão "Order Status"
        clicar_elemento(browser, By.XPATH, '//span[text()="Sales Order"]')
        
        time.sleep(25)
    except Exception as e:
        print(f"Erro ao verificar o status do pedido: {e}")

def main():
    try:
        # Configurar o driver do Chrome
        chrome_driver_path = ChromeDriverManager().install()
        if not chrome_driver_path.endswith("chromedriver.exe"):
            chrome_driver_path = os.path.join(os.path.dirname(chrome_driver_path), "chromedriver.exe")
        print(f"ChromeDriver path: {chrome_driver_path}")

        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")

        service = Service(executable_path=chrome_driver_path)

        browser = webdriver.Chrome(service=service, options=options)
        browser.maximize_window()
        link = 'https://pathfinder.automationanywhere.com/challenges/salesorder-applogin.html#'
        browser.get(link)

        acessar_sistema(browser)
        time.sleep(0.5)

        login(browser)
        verificar_order_status(browser)

    except Exception as e:
        print(f"Erro ao iniciar o ChromeDriver: {e}")
    finally:
        # Fechar o navegador
        browser.quit()

if __name__ == '__main__':
    main()