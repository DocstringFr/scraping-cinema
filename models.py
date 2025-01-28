from dataclasses import dataclass, field, asdict
from typing import List, Optional
from datetime import datetime

@dataclass
class MovieMetadata:
    title: str
    genre: str
    synopsis: str
    releasedate: str
    portraitimages: dict
    duration: str
    version: str
    format: str

@dataclass
class Session:
    time: str
    format: str

@dataclass
class Cinema:
    name: str
    sessions: List[Session] = field(default_factory=list)

@dataclass
class Schedule:
    date: str
    cinemas: List[Cinema] = field(default_factory=list)

@dataclass
class Movie:
    url: str
    metadata: MovieMetadata
    schedules: List[Schedule] = field(default_factory=list)

@dataclass
class ExportData:
    export_date: str = field(default_factory=lambda: datetime.now().isoformat())
    movies: List[Movie] = field(default_factory=list) 


if __name__ == "__main__":
    session = Session(time="12:00", format="2D")
    session.bonjour = "bonjour"
    print(session.__dict__)
    print(asdict(session))