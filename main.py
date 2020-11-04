import requests as r
from datetime import datetime
import threading
import psycopg2
from Connection_to_db import command_execution
import time


def get_list_of_urls(filename):
    url_list = []
    with open(filename, encoding="utf-8") as file:
        for line in file:
            url_list.append(line[:-1])
    return url_list


def get_list_from_db():
    con = psycopg2.connect(  # connecting to PostgreSQL database
        database='urls',
        user='postgres',
        password='',
        host="127.0.0.1",
        port="5432"
    )
    cur = con.cursor()
    cur.execute("SELECT * FROM urls ORDER BY last_check_time;")  # order by last check
    data = cur.fetchall()
    con.close()
    return data


def update_response(url, last_check_time, status_code, status, error, final_url):
    command_execution("""UPDATE urls SET last_check_time = '{}', status_code = '{}', status = '{}',
     error ='{}', final_url = '{}' WHERE url = '{}';""".format(
        last_check_time,
        status_code,
        status,
        error,
        final_url,
        url))  # adding new row to database


def insert_into_db(url, last_check_time, status_code, status, error, final_url):
    command_execution("""INSERT INTO urls (url, last_check_time, status_code, status, error, final_url)
     VALUES ('{}','{}','{}', '{}', '{}', '{}');""".format(
        url,
        last_check_time,
        status_code,
        status,
        error,
        final_url))  # adding new row to database


class App:
    def __init__(self, timeout_between_requests, urls, data, connection_timeout, max_threads_count):
        self.timeout = timeout_between_requests
        self.urls = urls
        self.data = data
        self.connection_timeout = connection_timeout
        self.max_threads_count = max_threads_count

    def time_processing(self):
        """This func check's datetime from db and if past more than variable timeout,
        add in list urls_to_update urls which need to update"""
        data = get_list_from_db()
        urls_to_update = []
        for row in data:
            if (datetime.now() - datetime(  # *args where args it is a list with int of time
                    *list(map(int, row[1][:row[1].index(" ")].split("-"))) +
                     list(map(int, row[1][row[1].index(" ") + 1:].split(":"))))
            ).seconds > self.timeout:  # if time from last check more than variable timeout
                urls_to_update.append(row[0])
        for url in urls_to_update:
            while threading.active_count() > self.max_threads_count:
                time.sleep(10)  # script sleeping
            threading.Thread(target=self.check_site, args=[url, 'update']).start()  # creating thread

    # TODO add logging!
    def check_site(self, url: str, check_type):
        """Get request to site"""
        current_time = str(datetime.now())[:-7]
        error = 'None'
        status = 'ok'
        try:
            response = r.get(url, allow_redirects=True, timeout=self.connection_timeout)
            if response.status_code >= 400:
                status = 'error'
                error = "Some error here"
            if check_type == "insert":
                insert_into_db(url, current_time, response.status_code, status, error, response.url)
            elif check_type == "update":
                update_response(url, current_time, response.status_code, status, error, response.url)
        except r.ConnectionError as e:  # wrong url
            print(e, "NOT CONNECTED ")
            print(url)
            print("Error: {} \nPlease delete this url from file or correct url".format(e))

        except Exception as e:
            print(e)

    def add_new_url_in_db(self):
        for url in self.urls:
            while threading.active_count() > self.max_threads_count:
                time.sleep(10)  # script sleeping
            threading.Thread(target=self.check_site, args=[url, 'insert']).start()  # creating thread


if __name__ == '__main__':  # starting program
    urls = get_list_of_urls("urls.txt")  # get list of urls
    data = get_list_from_db()
    timeout_between_requests = 60
    max_threads_count = 500
    app = App(timeout_between_requests=timeout_between_requests, urls=urls, data=data, connection_timeout=10,
              max_threads_count=max_threads_count)
    while 1:  # checking old urls in db
        app.time_processing()
        time.sleep(timeout_between_requests + 1)
