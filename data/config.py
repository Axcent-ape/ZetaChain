# реф ссылка
REF_LINK = 'https://hub.zetachain.com/xp?code=YWRkcmVzcz0weGJDZDJCMzE3MDYxODY1RTdhZWZERTc0MDBGOGQ4REIxNDY4MzU2MzAmZXhwaXJhdGlvbj0xNzEwMjM2Mzk4JnI9MHg5YjMxYjAzMTEzOWEwNjI4YjU2NjA2YjhlMDlhODQ2YTVjNThmOGRjNzc5NjU4ZTNlNmNkMDA0ODhlYjdmMzk0JnM9MHgwOTkwM2JjNzIxOGI5ZTRiOTJkZjM4M2UxZDU0MDk2YWVhZDdiY2UzZjJkZDU4NGM0MjE4ZDhhZGI3ZjViMjMwJnY9Mjc%3D'

DELAY = {
    "account": (5, 10),       # Задержка в секундах между аккаунтами
    "transaction": (20, 30),  # Задержка в секундах между транзакциями
    "quest": (5, 10)          # Задержка в секундах между квестами
}


# [x,y]. х - минимальное кол-во, у - максимальное кол-во. Рандом до 10 цифр после точки
SENDS_QUESTS = {
    "send_zeta": [0.001, 0.01],         # Сколько zeta отправить самому себе?
    "send_bnb":  [0.001, 0.002],     # Сколько zeta отправить для транзакции zeta->bnb.bsc (izumi)
    "send_eth":  [0.0001, 0.0002],    # Сколько zeta отправить для транзакции zeta->eth.rth (izumi)
    "send_btc":  [0.001, 0.002],     # Сколько zeta отправить для транзакции zeta->btc.btc (izumi)
}

# Чтобы отправлять в пулы указывать True/False в use.
POOLS = {
    "send_bnb": 0.0001,       # сколько отправлять бнб в пул
    "send_zeta": 0.0001,      # сколько отправлять zeta в пул

    # range pool
    "stzeta": 0.001  #должно быть меньше zeta_to_stzeta и zeta_to_wzeta с EDDY_SWAP
}

APPROVES = {
    "bnb_approve": 1,  # кол-во бнб для апрува
    "stzeta_approve": 12,  # кол-во stzeta для апрува
    "wzeta_approve": 12,   # кол-во wzeta для апрува
    "stzeta_accumulated_approve": 12
}

# свап на app.eddy.finance/swap
EDDY_SWAP = {
    "zeta_to_stzeta": 0.0013,  # кол-во zeta для свапа на stzeta
    "zeta_to_wzeta": 0.001,   # кол-во zeta для свапа на wzeta, можно не больше zeta_to_stzeta
}

ACCUMULATED_FINANCE = {
    "zeta_to_stzeta": 0.0001,     # кол-во zeta для свапа на stzeta на accumulated finance
    "stzeta_to_wstzeta": 0.0001  # кол-во stzeta для свапа на wstzeta на accumulated finance, должно быть не больше zeta_to_stzeta
}

# рпц
RPCs = {
    "zetachain": "https://zetachain-evm.blockpi.network/v1/rpc/public"  # zetachain rpc
}
