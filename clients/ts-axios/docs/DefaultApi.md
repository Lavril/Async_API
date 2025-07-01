# DefaultApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**filmDetailsApiV1FilmsFilmIdGet**](#filmdetailsapiv1filmsfilmidget) | **GET** /api/v1/films/{film_id} | Получить информацию о кинопроизведении|
|[**genreDetailsApiV1GenresGenreIdGet**](#genredetailsapiv1genresgenreidget) | **GET** /api/v1/genres/{genre_id} | Получить информацию о жанре|
|[**listFilmsApiV1FilmsGet**](#listfilmsapiv1filmsget) | **GET** /api/v1/films/ | Получить список фильмов по заданным критериям|
|[**listFilmsApiV1PersonsPersonIdFilmsGet**](#listfilmsapiv1personspersonidfilmsget) | **GET** /api/v1/persons/{person_id}/films | Получить список фильмов персоны|
|[**listGenresApiV1GenresGet**](#listgenresapiv1genresget) | **GET** /api/v1/genres/ | Получить список жанров|
|[**personDetailsApiV1PersonsPersonIdGet**](#persondetailsapiv1personspersonidget) | **GET** /api/v1/persons/{person_id} | Получить информацию о персоне|
|[**searchFilmsApiV1FilmsSearchGet**](#searchfilmsapiv1filmssearchget) | **GET** /api/v1/films/search/ | Поиск кинопроизведений|
|[**searchFilmsApiV1PersonsSearchGet**](#searchfilmsapiv1personssearchget) | **GET** /api/v1/persons/search/ | Поиск персон|

# **filmDetailsApiV1FilmsFilmIdGet**
> FilmFullResponse filmDetailsApiV1FilmsFilmIdGet()

Возвращает полную информацию о кинопроизведении по его идентификатору

### Example

```typescript
import {
    DefaultApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DefaultApi(configuration);

let filmId: string; //UUID фильма (default to undefined)

const { status, data } = await apiInstance.filmDetailsApiV1FilmsFilmIdGet(
    filmId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **filmId** | [**string**] | UUID фильма | defaults to undefined|


### Return type

**FilmFullResponse**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Объект с информацией о кинопроизведении |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **genreDetailsApiV1GenresGenreIdGet**
> Genre genreDetailsApiV1GenresGenreIdGet()

Возвращает полную информацию о жанре по его идентификатору

### Example

```typescript
import {
    DefaultApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DefaultApi(configuration);

let genreId: string; //UUID жанра (default to undefined)

const { status, data } = await apiInstance.genreDetailsApiV1GenresGenreIdGet(
    genreId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **genreId** | [**string**] | UUID жанра | defaults to undefined|


### Return type

**Genre**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Объект с информацией о жанре |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listFilmsApiV1FilmsGet**
> Array<FilmShortResponse> listFilmsApiV1FilmsGet()

Возвращает список из короткой информации по кинопроизведениям по заданным фильтрам

### Example

```typescript
import {
    DefaultApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DefaultApi(configuration);

let sort: string; //Сортировка (-imdb_rating для DESC, imdb_rating для ASC) (optional) (default to '-imdb_rating')
let genre: string; //UUID жанра для фильтрации (optional) (default to undefined)
let page: number; //Номер страницы (optional) (default to 1)
let size: number; //Количество элементов на странице (1-100) (optional) (default to 50)

const { status, data } = await apiInstance.listFilmsApiV1FilmsGet(
    sort,
    genre,
    page,
    size
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **sort** | [**string**] | Сортировка (-imdb_rating для DESC, imdb_rating для ASC) | (optional) defaults to '-imdb_rating'|
| **genre** | [**string**] | UUID жанра для фильтрации | (optional) defaults to undefined|
| **page** | [**number**] | Номер страницы | (optional) defaults to 1|
| **size** | [**number**] | Количество элементов на странице (1-100) | (optional) defaults to 50|


### Return type

**Array<FilmShortResponse>**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Список кинопроизведении с короткой информацией |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listFilmsApiV1PersonsPersonIdFilmsGet**
> Array<PersonFilms> listFilmsApiV1PersonsPersonIdFilmsGet()

Возвращает список из короткой информации по кинопроизведениям персоны

### Example

```typescript
import {
    DefaultApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DefaultApi(configuration);

let personId: string; //UUID персоны (default to undefined)

const { status, data } = await apiInstance.listFilmsApiV1PersonsPersonIdFilmsGet(
    personId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personId** | [**string**] | UUID персоны | defaults to undefined|


### Return type

**Array<PersonFilms>**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Список кинопроизведений персоны с короткой информацией |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listGenresApiV1GenresGet**
> Array<Genre> listGenresApiV1GenresGet()

Возвращает список жанров с их уникальными идентификаторами

### Example

```typescript
import {
    DefaultApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DefaultApi(configuration);

let page: number; //Номер страницы (optional) (default to 1)
let size: number; //Количество элементов на странице (1-100) (optional) (default to 50)

const { status, data } = await apiInstance.listGenresApiV1GenresGet(
    page,
    size
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **page** | [**number**] | Номер страницы | (optional) defaults to 1|
| **size** | [**number**] | Количество элементов на странице (1-100) | (optional) defaults to 50|


### Return type

**Array<Genre>**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Список жанров |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **personDetailsApiV1PersonsPersonIdGet**
> PersonFullResponse personDetailsApiV1PersonsPersonIdGet()

Возвращает информацию о персоне по его идентификатору

### Example

```typescript
import {
    DefaultApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DefaultApi(configuration);

let personId: string; //UUID персоны (default to undefined)

const { status, data } = await apiInstance.personDetailsApiV1PersonsPersonIdGet(
    personId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personId** | [**string**] | UUID персоны | defaults to undefined|


### Return type

**PersonFullResponse**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Объект с информацией о персоне |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **searchFilmsApiV1FilmsSearchGet**
> Array<FilmBaseResponse> searchFilmsApiV1FilmsSearchGet()

Полнотекстовый поиск по названиям и описаниям кинопроизведений

### Example

```typescript
import {
    DefaultApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DefaultApi(configuration);

let query: string; //Поисковый запрос (default to undefined)
let page: number; //Номер страницы (optional) (default to 1)
let size: number; //Количество элементов (optional) (default to 50)

const { status, data } = await apiInstance.searchFilmsApiV1FilmsSearchGet(
    query,
    page,
    size
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **query** | [**string**] | Поисковый запрос | defaults to undefined|
| **page** | [**number**] | Номер страницы | (optional) defaults to 1|
| **size** | [**number**] | Количество элементов | (optional) defaults to 50|


### Return type

**Array<FilmBaseResponse>**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Название и рейтинг фильма |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **searchFilmsApiV1PersonsSearchGet**
> Array<PersonFullResponse> searchFilmsApiV1PersonsSearchGet()

Полнотекстовый поиск персон по имени

### Example

```typescript
import {
    DefaultApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DefaultApi(configuration);

let query: string; //Поисковый запрос (default to undefined)
let page: number; //Номер страницы (optional) (default to 1)
let size: number; //Количество элементов (optional) (default to 50)

const { status, data } = await apiInstance.searchFilmsApiV1PersonsSearchGet(
    query,
    page,
    size
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **query** | [**string**] | Поисковый запрос | defaults to undefined|
| **page** | [**number**] | Номер страницы | (optional) defaults to 1|
| **size** | [**number**] | Количество элементов | (optional) defaults to 50|


### Return type

**Array<PersonFullResponse>**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Роли и фильмы персон |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

