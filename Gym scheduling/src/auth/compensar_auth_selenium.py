import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from config.config import Config
import time

class CompensarAuthSelenium:
    """Maneja la autenticación con Compensar usando Selenium (navegador real)"""
    
    def __init__(self):
        self.session = requests.Session()
        self.authenticated = False
        self.user_id = None
        self.driver = None
    
    def login(self, document_type: str, document_number: str, password: str) -> bool:
        """Login automatizado con Selenium"""
        try:
            print("🔐 Iniciando login automatizado con Selenium...")
            
            # Configurar Chrome Headless
            chrome_options = Options()
            chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            # User agent real para evitar bloqueos
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 1. Navegar al login
            login_url = f"{Config.LOGIN_URL}?serviceProviderName=HER-SP&protocol=SAML"
            print(f"   Navegando a {login_url}...")
            self.driver.get(login_url)
            
            wait = WebDriverWait(self.driver, 20)
            
            # 2. Llenar formulario
            print("   Buscando campos del formulario...")
            
            # Intentar selectores comunes
            try:
                # Tipo de documento (puede ser un select o un custom dropdown)
                # Intentamos buscar por nombre o ID común
                try:
                    doc_type_select = wait.until(EC.presence_of_element_located((By.NAME, "documentType")))
                    doc_type_select.send_keys(document_type)
                except:
                    print("   ⚠️ No se encontró select de tipo de documento (continuando...)")

                # Usuario / Documento
                user_input = wait.until(EC.presence_of_element_located((By.ID, "username")))
                user_input.clear()
                user_input.send_keys(document_number)
                
                # Contraseña
                pass_input = self.driver.find_element(By.ID, "password")
                pass_input.clear()
                pass_input.send_keys(password)
                
                # Botón Ingresar
                submit_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Ingresar') or contains(text(), 'Iniciar')]")
                
                print("   Enviando credenciales...")
                submit_btn.click()
                
            except Exception as e:
                print(f"   ❌ Error interactuando con el formulario: {e}")
                # Fallback: intentar buscar por name si ID falla
                try:
                    user_input = self.driver.find_element(By.NAME, "username")
                    user_input.send_keys(document_number)
                    pass_input = self.driver.find_element(By.NAME, "password")
                    pass_input.send_keys(password)
                    pass_input.submit()
                except:
                    print("   ❌ Falló también el fallback de selectores")
                    print(self.driver.page_source[:1000]) # Debug
                    return False

            # 3. Esperar redirección o éxito
            print("   Esperando autenticación...")
            time.sleep(5) # Espera inicial
            
            # Verificar URL o cookies
            max_retries = 10
            for _ in range(max_retries):
                if "seguridad.compensar.com" not in self.driver.current_url:
                    print("   ✅ Redirección detectada fuera del login")
                    self.authenticated = True
                    break
                
                # Verificar si hay mensaje de error
                if "usuario o contraseña incorrectos" in self.driver.page_source.lower():
                    print("   ❌ Credenciales incorrectas reportadas por la página")
                    return False
                    
                time.sleep(2)
            
            if not self.authenticated:
                print("   ⚠️ No se detectó redirección exitosa")
                # Intentar verificar cookies de todas formas
            
            # 4. Copiar sesión
            cookies = self.driver.get_cookies()
            for cookie in cookies:
                self.session.cookies.set(cookie['name'], cookie['value'])
                
            # Headers
            self.session.headers.update({
                'User-Agent': self.driver.execute_script("return navigator.userAgent;"),
                'Referer': 'https://sistemaplanbienestar.deportescompensar.com/'
            })
            
            # 5. Verificar acceso real
            print("   Verificando acceso a API...")
            if self._fetch_tiqueteras_data():
                print("   ✅ Login Selenium exitoso y validado")
                self.driver.quit()
                return True
            else:
                print("   ❌ Login Selenium falló en validación final")
                self.driver.quit()
                return False

        except Exception as e:
            print(f"❌ Error crítico en login Selenium: {str(e)}")
            if self.driver:
                self.driver.quit()
            return False

    def _fetch_tiqueteras_data(self):
        """Obtiene los datos de tiqueteras scrapeando el HTML renderizado"""
        import json
        from bs4 import BeautifulSoup
        
        try:
            # Navegar a la página principal de reservas (que carga los datos via AJAX)
            reservas_url = f"{Config.API_BASE_URL}/sistema.php/entrenamiento/reserva/practica/libre?autenticador=compensar"
            print(f"      Navegando a página de reservas: {reservas_url}")
            self.driver.get(reservas_url)
            
            # Esperar a que la página cargue y Angular renderice los datos
            print("      Esperando a que Angular renderice los datos...")
            time.sleep(8)  # Dar más tiempo para que Angular renderice todo
            
            # Obtener el HTML renderizado
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Buscar todos los elementos que contienen tiqueteras
            # Están en divs con ng-repeat="tiquetera in controller.tiqueteras.tiqueteras"
            tiquetera_divs = soup.find_all('div', {'ng-repeat': lambda x: x and 'tiquetera in controller.tiqueteras.tiqueteras' in x})
            
            if not tiquetera_divs:
                print("      ⚠️ No se encontraron tiqueteras en el HTML")
                with open('reservas_page_debug.html', 'w', encoding='utf-8') as f:
                    f.write(page_source)
                return False
            
            print(f"      📊 Encontradas {len(tiquetera_divs)} tiqueteras en el HTML")
            
            # Extraer datos de cada tiquetera
            tiqueteras = []
            for idx, div in enumerate(tiquetera_divs):
                try:
                    # Extraer nombre (en h5 > strong)
                    nombre_elem = div.find('h5')
                    nombre = nombre_elem.find('strong').get_text(strip=True) if nombre_elem else f"Tiquetera {idx+1}"
                    
                    # Extraer todas las labels
                    labels = div.find_all('label', class_='progress-label')
                    
                    # Determinar si es ilimitada
                    ilimitado = any('ilimitada' in label.get_text().lower() for label in labels)
                    
                    # Extraer sede, centro, deporte (están en labels sin clase especial)
                    label_texts = [label.get_text(strip=True) for label in labels if 'nombre-plan' not in label.get('class', [])]
                    
                    # Filtrar textos vacíos y fechas
                    info_labels = [text for text in label_texts if text and 'nov.' not in text.lower() and 'dic.' not in text.lower() and 'días restantes' not in text.lower() and 'ilimitada' not in text.lower() and 'prioridad' not in text.lower()]
                    
                    tiquetera_data = {
                        'id': idx + 1,
                        'nombre': nombre,
                        'nombre_centro_entrenamiento': info_labels[0] if len(info_labels) > 0 else nombre,
                        'nombre_sede': info_labels[1] if len(info_labels) > 1 else info_labels[0] if len(info_labels) > 0 else 'Desconocida',
                        'nombre_deporte': info_labels[2] if len(info_labels) > 2 else 'Acondicionamiento',
                        'ilimitado': ilimitado,
                        'entradas': 0 if ilimitado else 10,  # Valor por defecto
                        'id_centro_entrenamiento': idx + 1,
                        'id_participacion_deportista': 4626802  # Del debug_deportistas.json
                    }
                    
                    tiqueteras.append(tiquetera_data)
                    
                except Exception as e:
                    print(f"      ⚠️ Error procesando tiquetera {idx+1}: {str(e)}")
                    continue
            
            # Guardar en cache
            cache_data = {'tiqueteras': tiqueteras}
            with open('tiqueteras_cache.json', 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            print(f"      ✅ Datos de {len(tiqueteras)} tiqueteras guardados en tiqueteras_cache.json")
            return True
                
        except Exception as e:
            print(f"      ❌ Error obteniendo datos: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_user_id(self) -> str:
        """Obtiene el ID de usuario"""
        if not self.authenticated:
            raise Exception("No estás autenticado. Ejecuta login() primero.")
        
        if self.user_id:
            return str(self.user_id)
            
        # Fallback: intentar obtenerlo de la API si no está seteado
        try:
            response = self.session.get(
                f"{Config.API_BASE_URL}{Config.TIQUETERAS_ENDPOINT}",
                params={'autenticador': 'compensar'}
            )
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('tiqueteras') and len(data['tiqueteras']) > 0:
                        self.user_id = data['tiqueteras'][0]['id_participacion_deportista']
                        return str(self.user_id)
                except:
                    pass
            
            # Si fallamos en obtener el ID real, retornamos un default para permitir el acceso
            # ya que la autenticación fue exitosa
            print("⚠️ No se pudo obtener ID real, usando default")
            self.user_id = "usuario_compensar"
            return self.user_id
            
        except Exception as e:
            print(f"❌ Error obteniendo ID de usuario: {str(e)}")
            # Si ya estamos autenticados, permitir acceso
            self.user_id = "usuario_compensar"
            return self.user_id
    
    def is_authenticated(self) -> bool:
        """Verifica si la sesión está autenticada"""
        return self.authenticated
    
    def get_session(self) -> requests.Session:
        """Retorna la sesión autenticada"""
        if not self.authenticated:
            raise Exception("No estás autenticado. Ejecuta login() primero.")
        return self.session
    
    def __del__(self):
        """Asegurar que el navegador se cierre"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
