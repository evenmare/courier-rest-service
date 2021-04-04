# ya-backend-rest

### Использованные библиотеки
- [Flask                  1.1.2](https://flask.palletsprojects.com/en/1.1.x/)
- [Flask-SQLAlchemy       2.5.1](https://flask-sqlalchemy.palletsprojects.com/en/2.x/)
- [python-dateutil        2.8.1](https://dateutil.readthedocs.io/en/stable/index.html)
- [requests               2.22.0](https://pypi.org/project/requests/)

#### База данных
- [sqlite](https://www.sqlite.org/index.html)

#### Серверная часть
- [Gunicorn 20.1.0](https://gunicorn.org/)
- systemctl :)

## Логика сервиса
### [Описание потоков данных](ROUTES.md)
### Назначение заказов (`POST /orders/assign`)
#### Принципы:
0. Распределение заказов происходит на **сегодняшнюю** (дата отправки запроса) дату.
1. Для каждого курьера составляется собственный график работы, на выполнение каждого заказа внутри одного района отводится **30 минут**.
2. У каждого типа курьера своя **грузоподъемность**:
   - foot: <= 4 кг
   - bike: <= 8 кг
   - car: <= 16 кг
   > Таким образом, заказы, выходящие за верхний предел максимальной грузоподъемности, распределены не будут.
3. Из любого региона курьер может добраться в другой, время миграции между районами для каждого типа курьера разное:
   - car: = 2 времени доставки (60 минут)
   - bike: = 3 времени доставки (90 минут)
   - foot: = 4 времении доставки (120 минут)
   > Во время миграции заказы курьером не выполняются.
4. Приоритет в распределении отдаётся заказам с **меньшим** интервалом доставки.

### Расчет рейтинга и заработка
#### Принципы:
0. Рейтинг и заработок зависит от отношения выполненных в срок заказов к общему числу заказов: `k = число выполненных в срок заказов / общее число заказов`
1. Доход начисляется за выполнение доставки. Максимальная ставка дохода за одну доставку (при рейтинге 5): `max = 500`.
2. У курьеров, не выполнивших ни одного заказа, рейтинг и заработок отсутствуют (`NoneType`).
3. Формула расчёта рейтинга: `k * 5`
4. Формула расчёта заработка: `заработанное раннее + max * k`

## Запуск
### Главный исполняемый файл: `service.py`

### Запуск на сервере
> Путь хранения сервиса, для которого строится описание: `/opt/restya`
#### Вручную *(команда в терминале)*
- `gunicorn --chdir /opt/restya --bind=0.0.0.0:8080`
- `gunicorn --chdir /opt/restya --bind=0.0.0.0:8080 --log-level=debug service:app` (debug-mode)
#### Автоматически
0. **Создание .service-файла и подготовка**
   - `sudo nano /etc/systemd/system/start_server.service` - начать редактирование сервиса
     ```
      [Unit]
      Description=yaruBackendService
      After=network.target

      [Service]
      User=entrant
      WorkingDirectory=/opt/restya
      ExecStart=/home/entrant/.local/bin/gunicorn --chdir /opt/restya --bind=0.0.0.0:8080 --log-level=debug service:app
      ExecReload=/bin/kill -s HUP $MAINPID
      ExecStop=/bin/kill -s TERM $MAINPID
      PrivateTmp=true

      [Install]
      WantedBy=multi-user.target
     ```
   - `sudo systemctl daemon-reload` - перезапустим демона :)
   - `sudo systemctl enable start_server` - внесем наш сервис в базу *высокооцененных* системой
 1. - `sudo systemctl start start_server` - запустим!
    - Проверим статус `active (running)` в `sudo systemctl status start_server` и протрём пот со лба! 
 
 ## Тестирование
 ### Исполняемый файл: test.py
 Для работы скрипта необходима стандартная библиотека `unittest`.
 ### Тестирование на сервере: `python3 /opt/restya/test.py`
 Проводится тестирование всех [реализованных requests](ROUTES.md). Можно протестировать многопоточность, если убрать декоратор:
 ```
 @unittest.skip
 def test_parallel_work(self):
 ```
