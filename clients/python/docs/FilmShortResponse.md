# FilmShortResponse

Короткая информация по кинопроизведениям

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**uuid** | **str** | Уникальный идентификатор фильма | 
**title** | **str** | Название кинопроизведения | 
**imdb_rating** | **float** |  | [optional] 
**genres** | [**List[Genre]**](Genre.md) |  | [optional] 

## Example

```python
from openapi_client.models.film_short_response import FilmShortResponse

# TODO update the JSON string below
json = "{}"
# create an instance of FilmShortResponse from a JSON string
film_short_response_instance = FilmShortResponse.from_json(json)
# print the JSON string representation of the object
print(FilmShortResponse.to_json())

# convert the object into a dict
film_short_response_dict = film_short_response_instance.to_dict()
# create an instance of FilmShortResponse from a dict
film_short_response_from_dict = FilmShortResponse.from_dict(film_short_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


