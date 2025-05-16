# FilmBaseResponse

Базовая информация по кинопроизведениям

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**uuid** | **str** | Уникальный идентификатор фильма | 
**title** | **str** | Название кинопроизведения | 

## Example

```python
from openapi_client.models.film_base_response import FilmBaseResponse

# TODO update the JSON string below
json = "{}"
# create an instance of FilmBaseResponse from a JSON string
film_base_response_instance = FilmBaseResponse.from_json(json)
# print the JSON string representation of the object
print(FilmBaseResponse.to_json())

# convert the object into a dict
film_base_response_dict = film_base_response_instance.to_dict()
# create an instance of FilmBaseResponse from a dict
film_base_response_from_dict = FilmBaseResponse.from_dict(film_base_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


