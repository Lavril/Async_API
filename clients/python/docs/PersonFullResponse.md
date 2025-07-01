# PersonFullResponse

Полная информация по персоне

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**uuid** | **str** | Уникальный идентификатор персоны | 
**full_name** | **str** | Полное имя персоны | 
**films** | **List[object]** |  | [optional] 

## Example

```python
from openapi_client.models.person_full_response import PersonFullResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PersonFullResponse from a JSON string
person_full_response_instance = PersonFullResponse.from_json(json)
# print the JSON string representation of the object
print(PersonFullResponse.to_json())

# convert the object into a dict
person_full_response_dict = person_full_response_instance.to_dict()
# create an instance of PersonFullResponse from a dict
person_full_response_from_dict = PersonFullResponse.from_dict(person_full_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


