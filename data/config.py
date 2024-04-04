from core.zetachain import ZetaChain

# модули (функции скрипта). Чтобы убрать модуль, нужно поставить перед ним #, можно изменять порядок выполнения
MODULES = [
    ZetaChain.send_zeta,                            # отправляет сам себе зету
    ZetaChain.receive_bnb,                          # свап на бнб
    ZetaChain.receive_eth,                          # свап на этх
    ZetaChain.receive_btc,                          # свап на бтс
    ZetaChain.pool_deposit_any_pool,                # добавляет в пул бнб
    ZetaChain.eddy_finance_swap,                    # свапает zeta в stzeta на eddy finance
    ZetaChain.range_protocol_vault_transaction,     # добавляет ликвидность в range protocol
    ZetaChain.accumulated_finance_deposit,          # свап на accumulated finance
    ZetaChain.zeta_swap_swap,                       # свап wzeta на eth.eth через zetaswap
    ZetaChain.zeta_earn_stake,                      # стейк зеты на зетайчейн
    #ZetaChain.ultiverse_mint_badge,                 # минт бейджа на ultiverse
    ZetaChain.nativex_swap,                         # свап zeta на btc через nativex
]

# перемешивать ли порядок выполнения выбранных модулей для каждого потока. True - да, False - нет
SHUFFLE_MODULES = True

# реф ссылка
REF_LINK = 'https://hub.zetachain.com/xp?code=YWRkcmVzcz0weGJDZDJCMzE3MDYxODY1RTdhZWZERTc0MDBGOGQ4REIxNDY4MzU2MzAmZXhwaXJhdGlvbj0xNzEwMjM2Mzk4JnI9MHg5YjMxYjAzMTEzOWEwNjI4YjU2NjA2YjhlMDlhODQ2YTVjNThmOGRjNzc5NjU4ZTNlNmNkMDA0ODhlYjdmMzk0JnM9MHgwOTkwM2JjNzIxOGI5ZTRiOTJkZjM4M2UxZDU0MDk2YWVhZDdiY2UzZjJkZDU4NGM0MjE4ZDhhZGI3ZjViMjMwJnY9Mjc%3D'

# api key native.org. Можете использовать мой, но желательно свой. Гайд как его получить - https://telegra.ph/Kak-sozdat-api-key-dlya-nativeorg-03-09
NATIVE_API_KEY = "8c52192026b40b78c84a09d566faffa372b0031d"

# задержки
DELAY = {
    "account": (5, 10),       # Задержка в секундах между аккаунтами
    "transaction": (20, 30),  # Задержка в секундах между транзакциями
    "retry": (1, 3)           # Задержка в секундах между ретраями
}

# апрувы. [x,y]. х - минимальное кол-во, у - максимальное кол-во. Рандом до 10 цифр после точки
APPROVES = {
    "bnb_approve": [11, 20],  # кол-во бнб для апрува
    "stzeta_approve": [12, 20],  # кол-во stzeta для апрува
    "wzeta_approve": [12, 20],   # кол-во wzeta для апрува
    "stzeta_accumulated_approve": [12, 20],  # кол-во stzeta для апрува
    "zetaswap_wzeta_approve": [12, 20],
}

# [x,y]. х - минимальное кол-во, у - максимальное кол-во. Рандом до 10 цифр после точки
SENDS_QUESTS = {
    "send_zeta": [0.001, 0.01],         # Сколько zeta отправить самому себе?
    "send_bnb":  [0.01, 0.002],     # Сколько zeta отправить для транзакции zeta->bnb.bsc (izumi)
    "send_eth":  [0.0001, 0.0002],    # Сколько zeta отправить для транзакции zeta->eth.rth (izumi)
    "send_btc":  [0.001, 0.002],     # Сколько zeta отправить для транзакции zeta->btc.btc (izumi)
}

# Чтобы отправлять в пулы указывать True/False в use.
POOLS = {
    "send_bnb": 0.00001,       # сколько отправлять бнб в пул
    "send_zeta": 0.0001,      # сколько отправлять zeta в пул

    # range pool
    "stzeta": 0.001  #должно быть меньше zeta_to_stzeta и zeta_to_wzeta с EDDY_SWAP
}

# свап на app.eddy.finance/swap
EDDY_SWAP = {
    "zeta_to_stzeta": 0.0013,  # кол-во zeta для свапа на stzeta
    "zeta_to_wzeta": 0.01,   # кол-во zeta для свапа на wzeta, можно не больше zeta_to_stzeta
}

# минт и стейк на Accumulated finance
ACCUMULATED_FINANCE = {
    "zeta_to_stzeta": 0.0001,     # кол-во zeta для свапа на stzeta на accumulated finance
    "stzeta_to_wstzeta": 0.0001  # кол-во stzeta для свапа на wstzeta на accumulated finance, должно быть не больше zeta_to_stzeta
}

# стейк на ZetaChain
STAKE_ZETACHAIN= {
    "zeta_count": 0.0011  # кол-во zeta для стейка. минимум 0.0011
}

# свап wzeta на ETH.ETH через zetaswap. [x,y]. х - минимальное кол-во, у - максимальное кол-во. Рандом до 5 цифр после точки
ZETASWAP = {
    "wzeta_count": [0.0001, 0.0002]
}

# свап zeta на btc через nativeX
NATIVEX = {
    "zeta_count": [0.02, 0.03]
}

# рпц
RPCs = {
    "zetachain": "https://zetachain-evm.blockpi.network/v1/rpc/public"  # zetachain rpc
}
