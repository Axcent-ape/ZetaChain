# реф ссылка
REF_LINK = 'https://hub.zetachain.com/xp?code=YWRkcmVzcz0weGJDZDJCMzE3MDYxODY1RTdhZWZERTc0MDBGOGQ4REIxNDY4MzU2MzAmZXhwaXJhdGlvbj0xNzEwMjM2Mzk4JnI9MHg5YjMxYjAzMTEzOWEwNjI4YjU2NjA2YjhlMDlhODQ2YTVjNThmOGRjNzc5NjU4ZTNlNmNkMDA0ODhlYjdmMzk0JnM9MHgwOTkwM2JjNzIxOGI5ZTRiOTJkZjM4M2UxZDU0MDk2YWVhZDdiY2UzZjJkZDU4NGM0MjE4ZDhhZGI3ZjViMjMwJnY9Mjc%3D'

# задержка в секундах между аккаунтами
DELAY = (5, 10)

# Чтобы отправлять транзакции указывать True/False и через запятую кол-во монет, я указал минимум.
SENDS_QUESTS = {
    "send_zeta": [True, 0],         # Сколько zeta отправить самому себе?
    "send_bnb": [True, 0.001],      # Сколько zeta отправить для транзакции zeta->bnb.bsc (izumi)
    "send_eth": [True, 0.0001],     # Сколько zeta отправить для транзакции zeta->eth.rth (izumi)
    "send_btc": [True, 0.001],      # Сколько zeta отправить для транзакции zeta->btc.btc (izumi)


}

# Чтобы отправлять в пулы указывать True/False в use.
POOLS = {
    "use": True,              # использовать пулы
    "send_bnb": 0.0001,       # сколько отправлять бнб в пул
    "send_zeta": 0.0001       # сколько отправлять zeta в пул
}

APPROVES = {
    "bnb_approve": 0.02  # кол-во бнб для апрува
}

# рпц
RPCs = {
    "zetachain": "https://zetachain-evm.blockpi.network/v1/rpc/public"  # zetachain rpc
}
