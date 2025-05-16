# openapi_client.DefaultApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**film_details_api_v1_films_film_id_get**](DefaultApi.md#film_details_api_v1_films_film_id_get) | **GET** /api/v1/films/{film_id} | Получить информацию о кинопроизведении
[**genre_details_api_v1_genres_genre_id_get**](DefaultApi.md#genre_details_api_v1_genres_genre_id_get) | **GET** /api/v1/genres/{genre_id} | Получить информацию о жанре
[**list_films_api_v1_films_get**](DefaultApi.md#list_films_api_v1_films_get) | **GET** /api/v1/films/ | Получить список фильмов по заданным критериям
[**list_films_api_v1_persons_person_id_films_get**](DefaultApi.md#list_films_api_v1_persons_person_id_films_get) | **GET** /api/v1/persons/{person_id}/films | Получить список фильмов персоны
[**list_genres_api_v1_genres_get**](DefaultApi.md#list_genres_api_v1_genres_get) | **GET** /api/v1/genres/ | Получить список жанров
[**person_details_api_v1_persons_person_id_get**](DefaultApi.md#person_details_api_v1_persons_person_id_get) | **GET** /api/v1/persons/{person_id} | Получить информацию о персоне
[**search_films_api_v1_films_search_get**](DefaultApi.md#search_films_api_v1_films_search_get) | **GET** /api/v1/films/search/ | Поиск кинопроизведений
[**search_films_api_v1_persons_search_get**](DefaultApi.md#search_films_api_v1_persons_search_get) | **GET** /api/v1/persons/search/ | Поиск персон


# **film_details_api_v1_films_film_id_get**
> FilmFullResponse film_details_api_v1_films_film_id_get(film_id)

Получить информацию о кинопроизведении

Возвращает полную информацию о кинопроизведении по его идентификатору

### Example


```python
import openapi_client
from openapi_client.models.film_full_response import FilmFullResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    film_id = '3d825f60-9fff-4dfe-b294-1a45fa1e115d' # str | UUID фильма

    try:
        # Получить информацию о кинопроизведении
        api_response = api_instance.film_details_api_v1_films_film_id_get(film_id)
        print("The response of DefaultApi->film_details_api_v1_films_film_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->film_details_api_v1_films_film_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **film_id** | **str**| UUID фильма | 

### Return type

[**FilmFullResponse**](FilmFullResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Объект с информацией о кинопроизведении |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **genre_details_api_v1_genres_genre_id_get**
> Genre genre_details_api_v1_genres_genre_id_get(genre_id)

Получить информацию о жанре

Возвращает полную информацию о жанре по его идентификатору

### Example


```python
import openapi_client
from openapi_client.models.genre import Genre
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    genre_id = '3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff' # str | UUID жанра

    try:
        # Получить информацию о жанре
        api_response = api_instance.genre_details_api_v1_genres_genre_id_get(genre_id)
        print("The response of DefaultApi->genre_details_api_v1_genres_genre_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->genre_details_api_v1_genres_genre_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **genre_id** | **str**| UUID жанра | 

### Return type

[**Genre**](Genre.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Объект с информацией о жанре |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_films_api_v1_films_get**
> List[FilmShortResponse] list_films_api_v1_films_get(sort=sort, genre=genre, page=page, size=size)

Получить список фильмов по заданным критериям

Возвращает список из короткой информации по кинопроизведениям по заданным фильтрам

### Example


```python
import openapi_client
from openapi_client.models.film_short_response import FilmShortResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    sort = '-imdb_rating' # str | Сортировка (-imdb_rating для DESC, imdb_rating для ASC) (optional) (default to '-imdb_rating')
    genre = 'genre_example' # str | UUID жанра для фильтрации (optional)
    page = 1 # int | Номер страницы (optional) (default to 1)
    size = 50 # int | Количество элементов на странице (1-100) (optional) (default to 50)

    try:
        # Получить список фильмов по заданным критериям
        api_response = api_instance.list_films_api_v1_films_get(sort=sort, genre=genre, page=page, size=size)
        print("The response of DefaultApi->list_films_api_v1_films_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->list_films_api_v1_films_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sort** | **str**| Сортировка (-imdb_rating для DESC, imdb_rating для ASC) | [optional] [default to &#39;-imdb_rating&#39;]
 **genre** | **str**| UUID жанра для фильтрации | [optional] 
 **page** | **int**| Номер страницы | [optional] [default to 1]
 **size** | **int**| Количество элементов на странице (1-100) | [optional] [default to 50]

### Return type

[**List[FilmShortResponse]**](FilmShortResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Список кинопроизведении с короткой информацией |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_films_api_v1_persons_person_id_films_get**
> List[PersonFilms] list_films_api_v1_persons_person_id_films_get(person_id)

Получить список фильмов персоны

Возвращает список из короткой информации по кинопроизведениям персоны

### Example


```python
import openapi_client
from openapi_client.models.person_films import PersonFilms
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    person_id = '5b4bf1bc-3397-4e83-9b17-8b10c6544ed1' # str | UUID персоны

    try:
        # Получить список фильмов персоны
        api_response = api_instance.list_films_api_v1_persons_person_id_films_get(person_id)
        print("The response of DefaultApi->list_films_api_v1_persons_person_id_films_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->list_films_api_v1_persons_person_id_films_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **person_id** | **str**| UUID персоны | 

### Return type

[**List[PersonFilms]**](PersonFilms.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Список кинопроизведений персоны с короткой информацией |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_genres_api_v1_genres_get**
> List[Genre] list_genres_api_v1_genres_get(page=page, size=size)

Получить список жанров

Возвращает список жанров с их уникальными идентификаторами

### Example


```python
import openapi_client
from openapi_client.models.genre import Genre
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    page = 1 # int | Номер страницы (optional) (default to 1)
    size = 50 # int | Количество элементов на странице (1-100) (optional) (default to 50)

    try:
        # Получить список жанров
        api_response = api_instance.list_genres_api_v1_genres_get(page=page, size=size)
        print("The response of DefaultApi->list_genres_api_v1_genres_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->list_genres_api_v1_genres_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page** | **int**| Номер страницы | [optional] [default to 1]
 **size** | **int**| Количество элементов на странице (1-100) | [optional] [default to 50]

### Return type

[**List[Genre]**](Genre.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Список жанров |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **person_details_api_v1_persons_person_id_get**
> PersonFullResponse person_details_api_v1_persons_person_id_get(person_id)

Получить информацию о персоне

Возвращает информацию о персоне по его идентификатору

### Example


```python
import openapi_client
from openapi_client.models.person_full_response import PersonFullResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    person_id = '5b4bf1bc-3397-4e83-9b17-8b10c6544ed1' # str | UUID персоны

    try:
        # Получить информацию о персоне
        api_response = api_instance.person_details_api_v1_persons_person_id_get(person_id)
        print("The response of DefaultApi->person_details_api_v1_persons_person_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->person_details_api_v1_persons_person_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **person_id** | **str**| UUID персоны | 

### Return type

[**PersonFullResponse**](PersonFullResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Объект с информацией о персоне |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **search_films_api_v1_films_search_get**
> List[FilmBaseResponse] search_films_api_v1_films_search_get(query, page=page, size=size)

Поиск кинопроизведений

Полнотекстовый поиск по названиям и описаниям кинопроизведений

### Example


```python
import openapi_client
from openapi_client.models.film_base_response import FilmBaseResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    query = 'query_example' # str | Поисковый запрос
    page = 1 # int | Номер страницы (optional) (default to 1)
    size = 50 # int | Количество элементов (optional) (default to 50)

    try:
        # Поиск кинопроизведений
        api_response = api_instance.search_films_api_v1_films_search_get(query, page=page, size=size)
        print("The response of DefaultApi->search_films_api_v1_films_search_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->search_films_api_v1_films_search_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **query** | **str**| Поисковый запрос | 
 **page** | **int**| Номер страницы | [optional] [default to 1]
 **size** | **int**| Количество элементов | [optional] [default to 50]

### Return type

[**List[FilmBaseResponse]**](FilmBaseResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Название и рейтинг фильма |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **search_films_api_v1_persons_search_get**
> List[PersonFullResponse] search_films_api_v1_persons_search_get(query, page=page, size=size)

Поиск персон

Полнотекстовый поиск персон по имени

### Example


```python
import openapi_client
from openapi_client.models.person_full_response import PersonFullResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    query = 'query_example' # str | Поисковый запрос
    page = 1 # int | Номер страницы (optional) (default to 1)
    size = 50 # int | Количество элементов (optional) (default to 50)

    try:
        # Поиск персон
        api_response = api_instance.search_films_api_v1_persons_search_get(query, page=page, size=size)
        print("The response of DefaultApi->search_films_api_v1_persons_search_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->search_films_api_v1_persons_search_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **query** | **str**| Поисковый запрос | 
 **page** | **int**| Номер страницы | [optional] [default to 1]
 **size** | **int**| Количество элементов | [optional] [default to 50]

### Return type

[**List[PersonFullResponse]**](PersonFullResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Роли и фильмы персон |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

