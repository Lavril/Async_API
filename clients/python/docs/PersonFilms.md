# PersonFilms

Модель фильмов с рейтингом

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**uuid** | **str** | Уникальный идентификатор фильма | 
**title** | **str** | Название кинопроизведения | 
**imdb_rating** | **float** |  | [optional] 

## Example

```python
from openapi_client.models.person_films import PersonFilms

# TODO update the JSON string below
json = "{}"
# create an instance of PersonFilms from a JSON string
person_films_instance = PersonFilms.from_json(json)
# print the JSON string representation of the object
print(PersonFilms.to_json())

# convert the object into a dict
person_films_dict = person_films_instance.to_dict()
# create an instance of PersonFilms from a dict
person_films_from_dict = PersonFilms.from_dict(person_films_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


