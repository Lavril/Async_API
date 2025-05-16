# FilmShortResponse

Короткая информация по кинопроизведениям

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**uuid** | **string** | Уникальный идентификатор фильма | [default to undefined]
**title** | **string** | Название кинопроизведения | [default to undefined]
**imdb_rating** | **number** |  | [optional] [default to undefined]
**genres** | [**Array&lt;Genre&gt;**](Genre.md) |  | [optional] [default to undefined]

## Example

```typescript
import { FilmShortResponse } from './api';

const instance: FilmShortResponse = {
    uuid,
    title,
    imdb_rating,
    genres,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
