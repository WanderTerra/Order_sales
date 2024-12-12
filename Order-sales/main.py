from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
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
        

def selecionar_numero_itens(browser):
    try:
        # Localizar o elemento <select> pelo seu nome
        select_element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.NAME, 'salesOrderDataTable_length'))
        )
        
        # Criar um objeto Select e selecionar a opção "50"
        select = Select(select_element)
        select.select_by_value('50')
        
        # Adicionar uma pausa para garantir que a tabela seja atualizada
        time.sleep(2)
        
    except Exception as e:
        print(f"Erro ao selecionar o número de itens: {e}")
        
def capturar_tracking_numbers(browser):
    try:
        # Encontrar todas as tabelas de itens de pedidos expandidos
        tabelas_itens = browser.find_elements(By.XPATH, '//table[contains(@class, "sales-order-items")]')
        
        tracking_numbers = []
        print(tracking_numbers)
        for tabela in tabelas_itens:
            # Encontrar todas as linhas da tabela de itens
            linhas_itens = tabela.find_elements(By.XPATH, './/tbody/tr')
            
            for linha in linhas_itens:
                # Obter o número de rastreamento
                tracking_number = linha.find_element(By.XPATH, './td[2]').text
                tracking_numbers.append(tracking_number)
        
        return tracking_numbers
    
    except Exception as e:
        print(f"Erro ao capturar os números de rastreamento: {e}")
        return []
    
def verificar_status_entrega(browser, tracking_number):
    try:
        # Navegar para a URL fornecida
        browser.get('https://pathfinder.automationanywhere.com/challenges/salesorder-tracking.html#')
        
        # Esperar a página carregar
        time.sleep(2)
        
        # Inserir o número de rastreamento
        input_tracking = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, 'inputTrackingNo'))
        )
        input_tracking.clear()
        input_tracking.send_keys(tracking_number)
        
        # Clicar no botão de verificação de status
        btn_check_status = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, 'btnCheckStatus'))
        )
        btn_check_status.click()
        
        # Esperar o resultado carregar
        time.sleep(2)
        
        # Verificar se o campo "SCHEDULED DELIVERY" é igual a "Delivered"
        scheduled_delivery = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, '//tr[td[@class="font-weight-bold" and text()="SCHEDULED DELIVERY"]]/td[2]'))
        )
        status = scheduled_delivery.text
        return status == "Delivered"
    
    except Exception as e:
        print(f"Erro ao verificar o status de entrega para o número de rastreamento {tracking_number}: {e}")
        return False
    
# Exemplo de uso dentro da função verificar_order_status
def verificar_order_status(browser):
    try:
        # --------------------------------- VERIFICAR STATUS DO PEDIDO ---------------------------------
        # Clicar no botão "Sales Order"
        clicar_elemento(browser, By.XPATH, '//span[text()="Sales Order"]')
        
        # Esperar a tabela carregar
        time.sleep(1)
        
        # Selecionar a visualização de 50 itens
        selecionar_numero_itens(browser)
        
        while True:
            try:
                # Encontrar todas as linhas da tabela
                linhas = browser.find_elements(By.XPATH, '//table[@id="salesOrderDataTable"]/tbody/tr')
                
                for linha in linhas:
                    try:
                        # Obter o status do pedido
                        status = linha.find_element(By.XPATH, './td[5]').text
                        # Verificar se o status é "Confirmed" ou "Delivery Outstanding"
                        if status in ["Confirmed", "Delivery Outstanding"]:
                            print(f"Status do pedido: {status}")    
                            try:
                                # Clicar no botão de "+"
                                botao_expandir = linha.find_element(By.XPATH, './/i[contains(@class, "fa-square-plus")]')
                                botao_expandir.click()
                                
                                # Adicionar uma pausa após o clique no botão de "+"
                                time.sleep(0.5)
                                
                                # Capturar os números de rastreamento
                                tracking_numbers = capturar_tracking_numbers(browser)
                                print(f"Números de rastreamento: {tracking_numbers}")
                                
                                # # Verificar o status de entrega para cada número de rastreamento
                                # for tracking_number in tracking_numbers:
                                #     if verificar_status_entrega(browser, tracking_number):
                                #         print(f"O número de rastreamento {tracking_number} foi entregue.")
                                #     else:
                                #         print(f"O número de rastreamento {tracking_number} não foi entregue.")
                                
                            except Exception as e:
                                print(f"Erro ao clicar no botão de expandir: {e}")
                    except Exception as e:
                        print(f"Erro ao processar a linha da tabela: {e}")
                break
            except Exception as e:
                print(f"Erro ao encontrar as linhas da tabela: {e}")
                time.sleep(1)
                
    except Exception as e:
        print(f"Erro ao verificar o status do pedido: {e}")

def verificar_status_entrega(browser, tracking_number):
    try:
        # Navegar para a URL fornecida
        browser.get('https://pathfinder.automationanywhere.com/challenges/salesorder-tracking.html#')
        
        # Esperar a página carregar
        time.sleep(2)
        
        # Inserir o número de rastreamento
        input_tracking = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, 'inputTrackingNo'))
        )
        input_tracking.clear()
        input_tracking.send_keys(tracking_number)
        
        # Clicar no botão de verificação de status
        btn_check_status = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, 'btnCheckStatus'))
        )
        btn_check_status.click()
        
        # Esperar o resultado carregar
        time.sleep(2)
        
        # Verificar se o campo "SCHEDULED DELIVERY" é igual a "Delivered"
        scheduled_delivery = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, '//tr[td[@class="font-weight-bold" and text()="SCHEDULED DELIVERY"]]/td[2]'))
        )
        status = scheduled_delivery.text
        return status == "Delivered"
    
    except Exception as e:
        print(f"Erro ao verificar o status de entrega para o número de rastreamento {tracking_number}: {e}")
        return False
                

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
        time.sleep(0.5)
    except Exception as e:
        print(f"Erro ao iniciar o ChromeDriver: {e}")
    finally:
        browser.quit()

if __name__ == '__main__':
    main()