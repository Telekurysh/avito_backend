# Запуск проекта
```bash
pip3 install -r requirements.txt
python3 app.py
```
# Запуск нагрузочного тестирования
Сначала вам нужно установить утилиту *locust*
```bash
pip3 install locust
```
для запуска
```bash
locust -f load_test.py
```
потом переходим на страницу и запускаем нагрузочное тестирование.