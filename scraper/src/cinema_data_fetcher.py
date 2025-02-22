import logging
from .models import MovieMetadata, Session, Cinema, Schedule, Movie, ExportData
from .session_manager import SessionManager
from .date_utils import convert_portuguese_date

logger = logging.getLogger(__name__)


class NOSCinemaDataFetcher:
    """Gère la récupération des données de films et de séances pour les cinémas NOS."""
    
    def __init__(self, session_manager: SessionManager):
        """Initialise le fetcher avec un gestionnaire de session.
        
        Args:
            session_manager (SessionManager): Gestionnaire de session HTTP
        """
        self.session_manager = session_manager
        self.base_url = "https://www.cinemas.nos.pt"
    
    def get_movie_schedules(self, movie_id):
        """Récupère les horaires pour un film donné.
        
        Args:
            movie_id (str): Identifiant du film
            
        Returns:
            List[Schedule]: Liste des horaires du film
        """
        logger.debug(f"Récupération des horaires pour le film {movie_id}")
        url = f'{self.base_url}/bin/cinemas/render/getMovieSessions.getMovieSessionsAggregator.json?aggregateMovieId={movie_id}'
        
        try:
            response = self.session_manager.get(url, encoding='latin1')
            if response.status_code == 200:
                data = response.json()
                schedules = []
                
                for day in data.get('days', []):
                    iso_date = convert_portuguese_date(day['name'])
                    if not iso_date:
                        logger.warning(f"Date ignorée car invalide: {day['name']}")
                        continue
                        
                    cinemas = []
                    for theater in day.get('theaters', []):
                        # Récupérer seulement la région de Porto
                        if theater['regionId'] != "f889907b-97ae-4ab7-a8a8-b6c22cc8584d":
                            continue
                        
                        sessions = [
                            Session(time=session['time'], format=session['format'])
                            for session in theater.get('sessions', [])
                        ]
                        if sessions:
                            cinemas.append(Cinema(name=theater['name'], sessions=sessions))
                    
                    if cinemas:
                        schedules.append(Schedule(date=iso_date, cinemas=cinemas))
                
                logger.debug(f"Horaires récupérés pour le film {movie_id}: {len(schedules)} jours trouvés")
                return schedules
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des horaires pour le film {movie_id}: {e}")
            return []
            
    def fetch_all_movies(self):
        """Récupère tous les films et leurs horaires.
        
        Returns:
            ExportData: Données exportées contenant tous les films
        """
        url = f'{self.base_url}/graphql/execute.json/cinemas/getAllMovies'
        logger.debug(f"URL de l'endpoint: {url}")
        
        try:
            response = self.session_manager.get(url)
            if response.status_code != 200:
                logger.error(f'Erreur lors de la requête : {response.status_code}')
                return None
                
            data = response.json()
            logger.info("Liste des films récupérée avec succès")
            
            export_data = ExportData()
            total_movies = data['data']['movieList']['items']
            movies_in_2d = [movie for movie in total_movies if movie['format'] == '2d']
            
            logger.info(f"Traitement de {len(movies_in_2d)} films")
            
            for i, movie_data in enumerate(movies_in_2d, 1):
                logger.info(f"Traitement du film {i}/{len(movies_in_2d)}: {movie_data.get('title', 'Sans titre')}")
                
                try:
                    uuid = movie_data['aggregateformatnumber']
                    schedules = self.get_movie_schedules(uuid)
                    
                    metadata = MovieMetadata(
                        title=movie_data['title'],
                        genre=movie_data['genre'],
                        synopsis=movie_data['synopsis']['plaintext'],
                        releasedate=movie_data['releasedate'],
                        portraitimages=movie_data['portraitimages'],
                        duration=movie_data['duration'],
                        version=movie_data['version'],
                        format=movie_data['format'].upper()
                    )
                    
                    movie = Movie(
                        url=movie_data['detailurl'],
                        metadata=metadata,
                        schedules=schedules
                    )
                    
                    export_data.movies.append(movie)
                    logger.info(f"Film ajouté avec succès: {movie_data['title']}")
                    
                except KeyError as e:
                    logger.warning(f"Données manquantes dans le film {movie_data.get('title', 'Sans titre')}: {e}")
                    continue
                except TypeError as e:
                    logger.warning(f"Structure de données invalide dans le film {movie_data.get('title', 'Sans titre')}: {e}")
                    continue
            
            return export_data
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des films : {e}")
            return None

