from data import config
from core import ZetaChain
from core.utils import random_line, logger
import asyncio


async def retry_function(func, thread, *args, **kwargs):
    while True:
        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            logger.error(f"Поток {thread} | Ошибка выполнения функции {func.__name__}: {e}")
            await asyncio.sleep(10)


async def ZC(thread):
    logger.info(f"Поток {thread} | Начал работу")
    while True:
        act = await random_line('data/accounts.txt')
        if not act: break

        if '::' in act:
            private_key, proxy = act.split('::')
        else:
            private_key = act
            proxy = None

        zetachain = ZetaChain(key=private_key, thread=thread, proxy=proxy)

        # делает enroll
        if not await zetachain.check_enroll():
            # status, tx_hash = await zetachain.enroll()
            status, tx_hash = await retry_function(zetachain.enroll, thread)
            if status:
                logger.success(f"Поток {thread} | Выполнил enroll! {zetachain.web3_utils.acct.address}:{tx_hash}")
                logger.info(f"Поток {thread} | Спит 2с после enroll!")

                await asyncio.sleep(20)
                await zetachain.new_session()
            else:
                logger.error(f"Поток {thread} | Не выполнил enroll! {zetachain.web3_utils.acct.address}:{tx_hash}")

        # отправляет сам себе зету
        if await retry_function(zetachain.check_completed_task, thread, "SEND_ZETA") and config.SENDS_QUESTS['send_zeta'][0]:
            # status, tx_hash = await zetachain.transfer_zeta()
            status, tx_hash = await retry_function(zetachain.transfer_zeta, thread)
            if status:
                logger.success(f"Поток {thread} | Отправил zeta сам себе! {zetachain.web3_utils.acct.address}:{tx_hash}")
            else:
                logger.error(f"Поток {thread} | Не отправил zeta сам себе! {zetachain.web3_utils.acct.address}:{tx_hash}")

        # свап на бнб
        if await zetachain.check_completed_task("RECEIVE_BNB") and config.SENDS_QUESTS['send_bnb'][0]:
            # status, tx_hash = await zetachain.transfer_bnb()
            status, tx_hash = await retry_function(zetachain.transfer_bnb, thread)
            if status:
                logger.success(f"Поток {thread} | Сделал транзакцию zeta -> bnb.bsc! {zetachain.web3_utils.acct.address}:{tx_hash}")
                have_bnb = True
            else:
                logger.error(f"Поток {thread} | Не сделал транзакцию zeta -> bnb.bsc! {zetachain.web3_utils.acct.address}:{tx_hash}")
                have_bnb = False

        # свап на этх
        if await zetachain.check_completed_task("RECEIVE_ETH") and config.SENDS_QUESTS['send_eth'][0]:
            # status, tx_hash = await zetachain.transfer_eth()
            status, tx_hash = await retry_function(zetachain.transfer_eth, thread)
            if status:
                logger.success(f"Поток {thread} | Сделал транзакцию zeta -> eth.eth! {zetachain.web3_utils.acct.address}:{tx_hash}")
            else:
                logger.error(f"Поток {thread} | Не сделал транзакцию zeta -> eth.eth! {zetachain.web3_utils.acct.address}:{tx_hash}")

        # свап на бтс
        if await zetachain.check_completed_task("RECEIVE_BTC") and config.SENDS_QUESTS['send_btc'][0]:
            # status, tx_hash = await zetachain.transfer_btc()
            status, tx_hash = await retry_function(zetachain.transfer_btc, thread)
            if status:
                logger.success(f"Поток {thread} | Сделал транзакцию zeta -> btc.btc! {zetachain.web3_utils.acct.address}:{tx_hash}")
            else:
                logger.error(f"Поток {thread} | Не сделал транзакцию zeta -> btc.btc! {zetachain.web3_utils.acct.address}:{tx_hash}")

        # апрув бнб
        if float(await zetachain.check_approve_bnb())+0.001 < config.APPROVES['bnb_approve']:
            # status, tx_hash = await zetachain.approve_bnb()
            status, tx_hash = await retry_function(zetachain.approve_bnb, thread)
            if status:
                logger.success(
                    f"Поток {thread} | Апрувнул {config.APPROVES['bnb_approve']} бнб! {zetachain.web3_utils.acct.address}:{tx_hash}")
            else:
                logger.success(f"Поток {thread} | Не апрувнул бнб! {zetachain.web3_utils.acct.address}:{tx_hash}")

        # добавляет в пул бнб
        if await zetachain.check_completed_task("POOL_DEPOSIT_ANY_POOL") and config.SENDS_QUESTS['send_bnb'][0] and config.POOLS['use'] and float(await zetachain.check_approve_bnb())+0.0001 >= config.SENDS_QUESTS['send_bnb'][1] and zetachain.web3_utils.w3.from_wei(zetachain.web3_utils.balance_of_erc20(zetachain.web3_utils.acct.address, '0x48f80608B672DC30DC7e3dbBd0343c5F02C738Eb'), 'ether') >= config.SENDS_QUESTS['send_bnb'][1]:
            # status, tx_hash = await zetachain.add_liquidity()
            status, tx_hash = await retry_function(zetachain.add_liquidity, thread)
            if status:
                logger.success(f"Поток {thread} | Добавил ликвидность zeta-bnb! {zetachain.web3_utils.acct.address}:{tx_hash}")
            else:
                logger.error(f"Поток {thread} | Не добавил ликвидность zeta-bnb! {zetachain.web3_utils.acct.address}:{tx_hash}")

        # клеймит выполненые квесты
        claimed = await zetachain.claim_tasks()
        if claimed:
            logger.success(f"Поток {thread} | Заклеймил {claimed} квестов! {zetachain.web3_utils.acct.address}")
        else:
            logger.warning(f"Поток {thread} | Нет квестов для клейма! {zetachain.web3_utils.acct.address}")

        await zetachain.logout()
        logger.info(f"Поток {thread} | Спал {await zetachain.sleep()} секунд")

    logger.info(f"Поток {thread} | Закончил работу")


async def main():
    print("Автор софта: https://t.me/ApeCryptor")

    thread_count = int(input("Введите кол-во потоков: "))
    thread_count = 10 if thread_count > 10 else thread_count
    # thread_count = 1
    tasks = []
    for thread in range(1, thread_count+1):
        tasks.append(asyncio.create_task(ZC(thread)))

    await asyncio.gather(*tasks)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
