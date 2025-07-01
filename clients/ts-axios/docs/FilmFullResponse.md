# FilmFullResponse

Полная информация по кинопроизведениям

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**uuid** | **string** | Уникальный идентификатор фильма | [default to undefined]
**title** | **string** | Название кинопроизведения | [default to undefined]
**imdb_rating** | **number** |  | [optional] [default to undefined]
**genres** | [**Array&lt;Genre&gt;**](Genre.md) |  | [optional] [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**pg_rating** | **string** |  | [optional] [default to undefined]
**duration** | **number** |  | [optional] [default to undefined]
**release_year** | **number** |  | [optional] [default to undefined]
**poster_url** | **string** |  | [optional] [default to undefined]
**actors** | [**Array&lt;Person&gt;**](Person.md) |  | [optional] [default to undefined]
**writers** | [**Array&lt;Person&gt;**](Person.md) |  | [optional] [default to undefined]
**directors** | [**Array&lt;Person&gt;**](Person.md) |  | [optional] [default to undefined]

## Example

```typescript
import { FilmFullResponse } from './api';

const instance: FilmFullResponse = {
    uuid,
    title,
    imdb_rating,
    genres,
    description,
    pg_rating,
    duration,
    release_year,
    poster_url,
    actors,
    writers,
    directors,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
