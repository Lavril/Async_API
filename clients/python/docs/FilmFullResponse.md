# FilmFullResponse

Полная информация по кинопроизведениям

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**uuid** | **str** | Уникальный идентификатор фильма | 
**title** | **str** | Название кинопроизведения | 
**imdb_rating** | **float** |  | [optional] 
**genres** | [**List[Genre]**](Genre.md) |  | [optional] 
**description** | **str** |  | [optional] 
**pg_rating** | **str** |  | [optional] 
**duration** | **int** |  | [optional] 
**release_year** | **int** |  | [optional] 
**poster_url** | **str** |  | [optional] 
**actors** | [**List[Person]**](Person.md) |  | [optional] 
**writers** | [**List[Person]**](Person.md) |  | [optional] 
**directors** | [**List[Person]**](Person.md) |  | [optional] 

## Example

```python
from openapi_client.models.film_full_response import FilmFullResponse

# TODO update the JSON string below
json = "{}"
# create an instance of FilmFullResponse from a JSON string
film_full_response_instance = FilmFullResponse.from_json(json)
# print the JSON string representation of the object
print(FilmFullResponse.to_json())

# convert the object into a dict
film_full_response_dict = film_full_response_instance.to_dict()
# create an instance of FilmFullResponse from a dict
film_full_response_from_dict = FilmFullResponse.from_dict(film_full_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


