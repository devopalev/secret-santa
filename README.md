# Тайный Санта бот
Суть игры "Тайный Санта" состоит в анонимном обмене подарками между всеми ее участниками. 
Каждый становится Тайным Сантой для другого участника. 
Интерес в том, что получатели не должны знать, кто именно подарит им подарок.
Попробовать можно [тут](https://t.me/dushnyy_ded_bot).

## Цель разработки
В этом проекте экспериментами стали: использование кастомного контекста для каждого обработчика, RAW SQL, свои 
модели предметной области, миграции с yoyo, репозиторий вместо crud, календарь для telegram. Основной идеей являлось 
искать найболее простые решения и следовать топорному дизайну, вместо нагрузки зависимостями.

## Quick start
1. Rename the file `.env.example` to `.env` and write your bot token in it to the BOT_TOKEN variable (for example, 
BOT_TOKEN=<your_token>). 

### Docker compose
2. Install docker-compose (see https://docs.docker.com/compose/install/linux/)
3. Run `docker-compose up`
