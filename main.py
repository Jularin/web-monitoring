import requests as r
from requests.exceptions import HTTPError
from datetime import datetime
import threading


def get_list_of_urls(filename):
    url_list = []
    with open(filename, encoding="utf-8") as file:
        for line in file:
            url_list.append(line[:-1])
    return url_list


def redirect_history(responses):
    """Func return history of redirects"""
    result = []
    for response in responses.history:
        result.append(response.url)
    return result


def check_site(n, url: str):
    print("Поток номер {} начат".format(n))
    """Get request to site"""
    try:
        response = r.get(url)
        print(response)
        if len(response.history):  # if response have redirects
            response_history = redirect_history(response)

            
    except r.ConnectionError as e:  # wrong url
        print(e, "NOT CONNECTED ")
        return "Error: {} \nPlease delete this url from file or correct url".format(e)

    except Exception as e:
        print(e)
    print("Поток номер {} закончен".format(n))


def write_result(url, status_code, error, final_url):
    time = datetime.now().strftime("%d-%m-%Y %H:%M")
    result = {"{}".format(url): {
        "last_check_time": time,
        "status_code": status_code,
        "error":error,
        "final_url":url
        }
    }


def main():
    urls = get_list_of_urls("urls.txt")
    for n, url in enumerate(urls):
        threading.Thread(target=check_site, args=[n + 1, url]).start()


if __name__ == '__main__':
    main()
