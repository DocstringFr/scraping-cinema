import requests
import logging
import time
import os

logger = logging.getLogger(__name__)

class SessionManager:
    """Gère les requêtes HTTP avec gestion du délai entre requêtes et configuration du proxy."""
    
    def __init__(self, use_proxy=False, request_delay=1.0):
        """Initialise la session avec les paramètres nécessaires.
        
        Args:
            use_proxy (bool): Indique si on doit utiliser le proxy Bright Data
            request_delay (float): Délai minimum entre les requêtes en secondes
        """
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Cinema Scraper (support@docstring.fr)',
        })
        
        self.request_delay = float(request_delay)
        self.last_request_time = 0
        
        if use_proxy:
            try:
                self.session.proxies = self._get_proxies()
                self.session.verify = os.getenv('CERT_PATH')
                logger.info('Utilisation du proxy Bright Data')
            except Exception as e:
                logger.error(f'Erreur lors de la configuration du proxy : {e}')
                raise
    
    def _get_proxies(self):
        """Configure et retourne les proxies Bright Data."""
        logger.debug("Configuration des proxies Bright Data")
        username = os.getenv('BRIGHT_DATA_CUSTOMER')
        password = os.getenv('BRIGHT_DATA_PASSWORD')
        proxy_zone = os.getenv('BRIGHT_DATA_ZONE')
        proxy_host = os.getenv('BRIGHT_DATA_HOST')
        proxy_port = os.getenv('BRIGHT_DATA_PORT')

        proxy_url = f'http://{username}-{proxy_zone}:{password}@{proxy_host}:{proxy_port}'
        return {
            'http': proxy_url,
            'https': proxy_url
        }
    
    def _wait_for_delay(self):
        """Attend le délai nécessaire entre les requêtes."""
        if self.last_request_time > 0:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.request_delay:
                wait_time = self.request_delay - elapsed
                logger.debug(f"Attente de {wait_time:.2f} secondes avant la prochaine requête")
                time.sleep(wait_time)
        self.last_request_time = time.time()
    
    def get(self, url, encoding='utf-8'):
        """Effectue une requête GET avec gestion du délai.
        
        Args:
            url (str): URL de la requête
            
        Returns:
            requests.Response: Réponse de la requête
        """
        self._wait_for_delay()
        response = self.session.get(url)
        response.encoding = encoding
        return response 