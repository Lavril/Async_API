from itertools import groupby
import logging
from operator import itemgetter
from typing import Any

from psycopg.rows import Row

from models.models import Movie, Genre, Person, PersonRoles


def _map_model(model_name: str):
    """Get model class by name."""
    model_mapping = {
        'film_work': Movie,
        'person': Person,
        'genre': Genre
    }
    return model_mapping.get(model_name)


class DataTransformer:
    """Data transformer from PostgresSQL to Elasticsearch format."""
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def transform_data(self, extracted_data: dict) -> dict:
        """Transform data from PostgresSQL to Elasticsearch format."""
        model = _map_model(extracted_data.get('model'))
        model_name = model.__name__
        self.logger.info(f'Transform data in model "{model_name}"')
        transformed_data = []
        for row in extracted_data.get('data'):
            model_data = row.copy()
            if model_name == 'Movie':
                model_data.update(self._filter_movie_genres(model_data))
                model_data.update(self._split_movie_persons(model_data))
            transformed_row = model.model_validate(model_data)
            transformed_data.append(transformed_row.model_dump())
        return {'index': f'{model_name.lower()}s',
                'data': transformed_data}

    @staticmethod
    def _filter_movie_genres(raw_data: Row) -> dict[str, Any]:
        """Filter information about movie genres by roles."""
        filtered_genres = []
        for genre in raw_data.get('genres', []):
            filtered_genre = Genre.model_validate(genre)
            filtered_genres.append(filtered_genre.model_dump(exclude='description'))
        return {'genres': filtered_genres}

    @staticmethod
    def _split_movie_persons(raw_data: Row) -> dict[str, Any]:
        """Split information about movie persons by roles."""
        persons = raw_data.get('persons')
        sorted_persons = sorted(persons, key=itemgetter('role'))
        grouped_persons = {k: list(v) for k, v in
                           groupby(sorted_persons, itemgetter('role'))}

        split_persons = {}
        for role in PersonRoles.roles:
            group, group_names = f'{role}s', f'{role}s_names'
            transformed_persons, persons_names = [], []

            for person in grouped_persons.get(role, []):
                transformed_person = Person.model_validate(person)
                transformed_persons.append(transformed_person.model_dump())
                persons_names.append(transformed_person.full_name)

            split_persons[group] = transformed_persons
            split_persons[group_names] = persons_names

        return split_persons
