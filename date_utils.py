from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def convert_portuguese_date(date_str):
    """Convertit une date du format portugais vers ISO 8601.
    
    Args:
        date_str (str): Date en portugais ('Hoje', 'Amanhã', ou 'day dd/mm')
        
    Returns:
        str: Date au format ISO 8601 (YYYY-MM-DD)
    """
    logger.debug(f"Conversion de la date: {date_str}")
    today = datetime.now().date()
    
    if date_str.lower() == 'hoje':
        return today.isoformat()
    elif date_str.lower() == 'amanhã':
        return (today + timedelta(days=1)).isoformat()
    else:
        # Format attendu: "day dd/mm"
        try:
            # Extraire le jour et le mois
            day_month = date_str.split(' ')[1]  # Prend la partie "dd/mm"
            day, month = map(int, day_month.split('/'))
            
            # Déterminer l'année
            year = today.year
            # Si le mois est inférieur au mois actuel, c'est pour l'année prochaine
            if month < today.month or (month == today.month and day < today.day):
                year += 1
                
            return f"{year}-{month:02d}-{day:02d}"
        except (IndexError, ValueError) as e:
            logger.error(f"Erreur lors de la conversion de la date {date_str}: {e}")
            return None 