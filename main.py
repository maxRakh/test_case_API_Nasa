import requests
from datetime import datetime


def check_date(start_date: str, end_date: str) -> bool:
    date_format = "%Y-%m-%d"
    try:
        datetime.strptime(start_date, date_format)
        datetime.strptime(end_date, date_format)
        return True
    except Exception:
        return False


def check_record_limit(limit: int) -> bool:
    return isinstance(limit, int) and limit > 0


def get_nasa_objects(start_date: str, end_date: str, record_limit: int) -> list[str]:
    """Достать из api NASA объекты, близкие к земной орбите за заданный интервал дат
    Вывести результат по заданному количеству строк на каждую дату (топ-5, топ-3 и т.д.) в виде:
    дата neo_reference_id: словарь со значениями по заданным ключам
    Пример вывода:
    2022-02-23 3768654: {'name': '(2017 CX1)', 'absolute_magnitude_h': 28.2, 'is_potentially_hazardous_asteroid': False}
    вывод отсортировать в рамках каждой даты по ключу absolute_magnitude_h по убыванию от большего
    ключи: ['name', 'absolute_magnitude_h', 'is_potentially_hazardous_asteroid']
    Пример GET запроса: https://api.nasa.gov/neo/rest/v1/feed?start_date=2015-09-07&end_date=2015-09-08&api_key=DEMO_KEY
    Допускается использовать только импорт модулей requests и datetime
    На вход функция вывода должна уметь принимать дату начала поиска, дату окончания поиска, лимит вывода записей на каждую дату"""

    url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={start_date}&end_date={end_date}&api_key=DEMO_KEY"

    if not check_date(start_date, end_date):
        raise ValueError("Даты должны быть введены в формате 'Y-m-d'.")
    elif start_date > end_date:
        raise ValueError("Дата начала поиска должна быть меньше или равна дате окончания поиска.")
    elif not check_record_limit(record_limit):
        raise ValueError("Лимит вывода записей должен быть целым положительным числом больше нуля.")

    try:
        response = requests.get(url=url)

        if response.status_code == 200:
            data = response.json()
            objects_by_data = data.get('near_earth_objects')

            results_list = []
            for date in objects_by_data:
                if not objects_by_data[date]:
                    continue

                sorted_objects_by_date = sorted(objects_by_data[date], key=lambda x: -x['absolute_magnitude_h'])
                top_sorted_objects_by_date = sorted_objects_by_date[0:record_limit]

                for elem in top_sorted_objects_by_date:
                    neo_reference_id = elem["neo_reference_id"]
                    date_and_neo_reference_id = f"{date} {neo_reference_id}"
                    name = elem["name"]
                    absolute_magnitude_h = elem["absolute_magnitude_h"]
                    is_potentially_hazardous_asteroid = elem["is_potentially_hazardous_asteroid"]

                    result_dict = dict()
                    result_dict['name'] = name
                    result_dict['absolute_magnitude_h'] = absolute_magnitude_h
                    result_dict['is_potentially_hazardous_asteroid'] = is_potentially_hazardous_asteroid

                    result = f"{date_and_neo_reference_id}: {result_dict}"

                    results_list.append(result)

            return results_list
    except requests.exceptions.RequestException as ex:
        raise ValueError(f'Проблема с подключением к API NASA: {ex}')
    except ValueError as ex:
        raise ValueError(f"Ошибка при обработке ответа API NASA: {ex}")


if __name__ == '__main__':
    get_result = get_nasa_objects(start_date='2015-09-07', end_date='2015-09-08', record_limit=3)
    print(*get_result)
