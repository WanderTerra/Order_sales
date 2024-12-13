from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import Select
from datetime import datetime, timedelta
from dotenv import load_dotenv
import tkinter as tk
from tkinter import messagebox

import os
import time
import pyautogui
from time import sleep

load_dotenv()

usuario_aut_any = os.getenv('USUARIO_AUT_ANY')
senha_aut_any = os.getenv('SENHA_AUT_ANY')
usuario = os.getenv('USUARIO')
senha = os.getenv('SENHA')

import os

pyautoguiimg = os.path.join(os.getcwd(), 'pyautoguiimg')

class ImageFinder:
    def __init__(self, image_path, confidence=0.8, sleep_time=2):
        self.image_path = image_path
        self.confidence = confidence
        self.sleep_time = sleep_time

    def find_and_click(self):
        if not os.path.exists(self.image_path):
            raise FileNotFoundError(f"Imagem {self.image_path} não existe no diretório.")
        
        while True:
            try:
                time.sleep(self.sleep_time)
                location = pyautogui.locateOnScreen(self.image_path, confidence=self.confidence)
                if location:
                    pyautogui.click(location)
                    return location

            except Exception as e:
                print(f"O seguite erro ocorreu: {e}")
    
    def scroll_and_find(self, confidence=None):
                    if not os.path.exists(self.image_path):
                        raise FileNotFoundError(f"Imagem {self.image_path} não existe no diretório.")
                    
                    if confidence is None:
                        confidence = self.confidence  # Use o valor padrão se não for fornecido
                    
                    max_scroll_attempts = 10  # Defina o limite de tentativas de rolagem
                    scroll_attempts = 0
                    
                    while scroll_attempts < max_scroll_attempts:
                        try:
                            time.sleep(self.sleep_time)
                            location = pyautogui.locateOnScreen(self.image_path, confidence=confidence)
                            if location:
                                pyautogui.click(location)
                                return location
                            else:
                                pyautogui.scroll(-100)  # Scroll down
                                time.sleep(0.1)
                                scroll_attempts += 1
                        except Exception as e:
                            print(f"O seguinte erro ocorreu: {e}")
                    
                    print("Imagem não encontrada após várias tentativas de rolagem.")
                    return None  # Ou levante uma exceção, se preferir

def clicar_elemento(browser, by, value):
    try:
        # Localizar e clicar no elemento
        elemento = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((by, value))
        )
        elemento.click()
    except Exception as e:
        print(f"Erro ao clicar no elemento: {e}")

def clicar_imagem(nome_imagem, sleep_time=1):
    image_finder = ImageFinder(os.path.join(pyautoguiimg, nome_imagem), sleep_time=sleep_time)
    location = image_finder.find_and_click()
    return location

def acessar_sistema(browser):
    clicar_elemento(browser, By.ID, 'onetrust-accept-btn-handler')
    clicar_elemento(browser, By.ID, 'button_modal-login-btn__iPh6x')
    time.sleep(1)

    clicar_elemento(browser, By.ID, '43:2;a')
    pyautogui.write(usuario_aut_any)
    pyautogui.press('enter')
    clicar_elemento(browser, By.ID, '10:148;a')
    pyautogui.write(senha_aut_any)
    pyautogui.press('enter')

def login(browser):
    try:
        # --------------------------------- LOGIN ---------------------------------
        usuario_field = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, 'salesOrderInputEmail'))
        )
        usuario_field.send_keys(usuario)

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
        
        time.sleep(2)
        
    except Exception as e:
        print(f"Erro ao selecionar o número de itens: {e}")

def capturar_tracking_numbers(browser):
    try:
        # Encontrar todas as tabelas de itens de pedidos expandidos
        tabelas_itens = browser.find_elements(By.XPATH, '//table[contains(@class, "sales-order-items")]')
        
        tracking_numbers = []
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
        browser.execute_script("window.open('about:blank', '_blank');")
        time.sleep(1)  # Adicionar uma pequena pausa para garantir que a janela seja aberta
        browser.switch_to.window(browser.window_handles[-1])
        browser.maximize_window()

        browser.get('https://pathfinder.automationanywhere.com/challenges/salesorder-tracking.html#')
        time.sleep(2)
        
        # Inserir o número de rastreamento
        input_field = browser.find_element(By.ID, 'inputTrackingNo')
        input_field.clear()
        input_field.send_keys(tracking_number)
        
        # Clicar no botão de verificar status
        track_button = browser.find_element(By.ID, 'btnCheckStatus')
        track_button.click()
        
        # Esperar até que a tabela de status de envio esteja visível
        WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.ID, 'shippingTable'))
        )
        
        # Capturar o status do envio
        status_element = browser.find_element(By.XPATH, '//*[@id="shipmentStatus"]/tr[3]/td[2]')
        status = status_element.text.strip()
        print(f"Status do rastreamento {tracking_number}: {status}")
        time.sleep(1)
        browser.close()
        browser.switch_to.window(browser.window_handles[0])
        
        return status
    except Exception as e:
        print(f"Erro ao verificar o status do rastreamento {tracking_number}: {e}")
        browser.close()
        browser.switch_to.window(browser.window_handles[0])
        return None

def verificar_order_status(browser):
    pedidos_completos = 0
    pedidos_pendentes = 0

    try:
        # --------------------------------- VERIFICAR STATUS DO PEDIDO ---------------------------------
        # Clicar no botão "Sales Order"
        clicar_elemento(browser, By.XPATH, '//span[text()="Sales Order"]')
        time.sleep(1)

        # Selecionar a visualização de 50 itens
        selecionar_numero_itens(browser)
        index = 0

        while True:
            # Atualizar a lista de linhas
            linhas = browser.find_elements(By.XPATH, '//table[@id="salesOrderDataTable"]/tbody/tr')

            # Verificar se o índice está além do número de linhas
            if index >= len(linhas):
                break

            linha = linhas[index]

            try:
                # Verificar se a linha contém elementos <td>
                td_elements = linha.find_elements(By.TAG_NAME, 'td')
                if len(td_elements) < 5:
                    print("Linha não contém dados de pedido. Pulando para a próxima linha.")
                    index += 1
                    continue

                # Obter o status do pedido
                status = linha.find_element(By.XPATH, './td[5]').text

                # Verificar se o status é "Confirmed" ou "Delivery Outstanding"
                if status in ["Confirmed", "Delivery Outstanding"]:
                    print(f"Status do pedido: {status}")
                    try:
                        # Clicar no botão de "+"
                        botao_expandir = linha.find_element(By.XPATH, './/i[contains(@class, "fa-square-plus")]')
                        botao_expandir.click()
                        time.sleep(0.5)

                        # Capturar os números de rastreamento
                        tracking_numbers = capturar_tracking_numbers(browser)
                        print(f"Números de rastreamento: {tracking_numbers}")

                        # Verificar o status de entrega para cada número de rastreamento
                        todos_entregues = True
                        for tracking_number in tracking_numbers:
                            status_entrega = verificar_status_entrega(browser, tracking_number)

                            if status_entrega == 'Delivered':
                                print(f"O número de rastreamento {tracking_number} foi entregue.")
                            else:
                                print(f"O número de rastreamento {tracking_number} não foi entregue. Status: {status_entrega}")
                                todos_entregues = False
                                break  # Sair do loop for e continuar com o próximo item

                        if todos_entregues:
                            # Clicar no botão correspondente para gerar fatura
                            try:
                                image_path = os.path.join(pyautoguiimg, 'botao_generate_invoice.png')
                                image_finder = ImageFinder(image_path, sleep_time=1)
                                image_finder.scroll_and_find(confidence=0.97)
                                time.sleep(2)
                                print("Botão de gerar fatura clicado.")
                                pedidos_completos += 1
                                time.sleep(2)
                            except Exception as e:
                                print(f"Erro ao clicar no botão de gerar fatura: {e}")
                        else:
                            # Clicar no botão "Close"
                            try:
                                
                                image_path = os.path.join(pyautoguiimg, 'botao_close.png')
                                image_finder = ImageFinder(image_path, confidence=0.9)
                                image_finder.scroll_and_find(confidence=0.97)
                                print("Botão de fechar clicado.")
                                pedidos_pendentes += 1
                                time.sleep(2)
                            except Exception as e:
                                print(f"Erro ao clicar no botão de fechar: {e}")

                        linhas = browser.find_elements(By.XPATH, '//table[@id="salesOrderDataTable"]/tbody/tr')
                    except Exception as e:
                        print(f"Erro ao processar o pedido: {e}")
                else:
                    print(f"Pedido com status '{status}' ignorado.")
            except Exception as e:
                print(f"Erro ao processar a linha da tabela: {e}")

            index += 1

    except Exception as e:
        print(f"Erro ao verificar o status do pedido: {e}")

    return pedidos_completos, pedidos_pendentes


def mostrar_resultados(pedidos_completos, pedidos_pendentes):
    root = tk.Tk()
    root.withdraw()  
    messagebox.showinfo("Resultados", f"Pedidos completados: {pedidos_completos}\nPedidos pendentes: {pedidos_pendentes}")
    root.destroy()

def main():
    try:
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
        time.sleep(2)

        login(browser)
        pedidos_completos, pedidos_pendentes = verificar_order_status(browser)
        
        time.sleep(5)
    except Exception as e:
        print(f"Erro ao iniciar o ChromeDriver: {e}")
    finally:
        mostrar_resultados(pedidos_completos, pedidos_pendentes)
        browser.quit()

if __name__ == '__main__':
    main()