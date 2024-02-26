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
            status, tx_hash = await retry_function(zetachain.enroll, thread)
            if status:
                logger.success(f"Поток {thread} | Выполнил enroll! {zetachain.web3_utils.acct.address}:{tx_hash}")
                logger.info(f"Поток {thread} | Спит 20с после enroll!")

                await asyncio.sleep(20)
                await zetachain.new_session()
            else:
                logger.error(f"Поток {thread} | Не выполнил enroll! {zetachain.web3_utils.acct.address}:{tx_hash}")

        # отправляет сам себе зету
        if await retry_function(zetachain.check_completed_task, thread, "SEND_ZETA") and config.SENDS_QUESTS['send_zeta'][1]:
            status, tx_hash, random_value = await retry_function(zetachain.transfer_zeta, thread)
            if status:
                logger.success(f"Поток {thread} | Отправил {random_value} zeta сам себе! {zetachain.web3_utils.acct.address}:{tx_hash}")
                await zetachain.sleep(config.DELAY['transaction'], logger, thread)
            else:
                logger.error(f"Поток {thread} | Не отправил zeta сам себе! {zetachain.web3_utils.acct.address}:{tx_hash}")
            await zetachain.sleep(config.DELAY['quest'], logger, thread)

        # свап на бнб
        if await zetachain.check_completed_task("RECEIVE_BNB") and config.SENDS_QUESTS['send_bnb'][1]:
            status, tx_hash, random_value = await retry_function(zetachain.transfer_bnb, thread)
            if status:
                logger.success(f"Поток {thread} | Сделал транзакцию: {random_value} zeta -> bnb.bsc! {zetachain.web3_utils.acct.address}:{tx_hash}")
                await zetachain.sleep(config.DELAY['transaction'], logger, thread)
            else:
                logger.error(f"Поток {thread} | Не сделал транзакцию: zeta -> bnb.bsc! {zetachain.web3_utils.acct.address}:{tx_hash}")
            await zetachain.sleep(config.DELAY['quest'], logger, thread)

        # свап на этх
        if await zetachain.check_completed_task("RECEIVE_ETH") and config.SENDS_QUESTS['send_eth'][1]:
            status, tx_hash, random_value = await retry_function(zetachain.transfer_eth, thread)
            if status:
                logger.success(f"Поток {thread} | Сделал транзакцию: {random_value} zeta -> eth.eth! {zetachain.web3_utils.acct.address}:{tx_hash}")
                await zetachain.sleep(config.DELAY['transaction'], logger, thread)
            else:
                logger.error(f"Поток {thread} | Не сделал транзакцию: zeta -> eth.eth! {zetachain.web3_utils.acct.address}:{tx_hash}")
            await zetachain.sleep(config.DELAY['quest'], logger, thread)

        # свап на бтс
        if await zetachain.check_completed_task("RECEIVE_BTC") and config.SENDS_QUESTS['send_btc'][1]:
            status, tx_hash, random_value = await retry_function(zetachain.transfer_btc, thread)
            if status:
                logger.success(f"Поток {thread} | Сделал транзакцию: {random_value} zeta -> btc.btc! {zetachain.web3_utils.acct.address}:{tx_hash}")
                await zetachain.sleep(config.DELAY['transaction'], logger, thread)
            else:
                logger.error(f"Поток {thread} | Не сделал транзакцию: zeta -> btc.btc! {zetachain.web3_utils.acct.address}:{tx_hash}")
            await zetachain.sleep(config.DELAY['quest'], logger, thread)

        # апрув бнб
        if float(await zetachain.allowance_bnb())+0.001 < config.APPROVES['bnb_approve']:
            status, tx_hash = await retry_function(zetachain.approve_bnb, thread)
            if status:
                logger.success(f"Поток {thread} | Апрувнул {config.APPROVES['bnb_approve']} бнб! {zetachain.web3_utils.acct.address}:{tx_hash}")
                await zetachain.sleep(config.DELAY['transaction'], logger, thread)
            else:
                logger.success(f"Поток {thread} | Не апрувнул бнб! {zetachain.web3_utils.acct.address}:{tx_hash}")

        # добавляет в пул бнб
        if await zetachain.check_completed_task("POOL_DEPOSIT_ANY_POOL") and zetachain.web3_utils.w3.from_wei(zetachain.web3_utils.balance_of_erc20(zetachain.web3_utils.acct.address, '0x48f80608B672DC30DC7e3dbBd0343c5F02C738Eb'), 'ether') >= config.POOLS['send_bnb']:
            status, tx_hash = await retry_function(zetachain.add_liquidity, thread)
            if status:
                logger.success(f"Поток {thread} | Добавил ликвидность zeta-bnb! {zetachain.web3_utils.acct.address}:{tx_hash}")
                await zetachain.sleep(config.DELAY['transaction'], logger, thread)
            else:
                logger.error(f"Поток {thread} | Не добавил ликвидность zeta-bnb! {zetachain.web3_utils.acct.address}:{tx_hash}")
            await zetachain.sleep(config.DELAY['quest'], logger, thread)

        # свапает zeta в stzeta на eddy finance
        if await zetachain.check_completed_task("EDDY_FINANCE_SWAP"):
            status, tx_hash = await retry_function(zetachain.swap_zeta_to_stzeta, thread)
            if status:
                logger.success(f"Поток {thread} | Сделал свап zeta -> stzeta! {zetachain.web3_utils.acct.address}:{tx_hash}")
                await zetachain.sleep(config.DELAY['transaction'], logger, thread)
            else:
                logger.error(f"Поток {thread} | Не сделал свап zeta -> stzeta! {zetachain.web3_utils.acct.address}:{tx_hash}")
            await zetachain.sleep(config.DELAY['quest'], logger, thread)

        # апрув stzeta
        if float(await zetachain.allowance_stzeta())+0.1 < config.APPROVES['stzeta_approve']:
            status, tx_hash = await retry_function(zetachain.approve_stzeta, thread)
            if status:
                logger.success(f"Поток {thread} | Апрувнул {config.APPROVES['stzeta_approve']} stzeta! {zetachain.web3_utils.acct.address}:{tx_hash}")
                await zetachain.sleep(config.DELAY['transaction'], logger, thread)
            else:
                logger.success(f"Поток {thread} | Не апрувнул stzeta! {zetachain.web3_utils.acct.address}:{tx_hash}")

        # апрув wzeta
        if float(await zetachain.allowance_wzeta()) + 0.1 < config.APPROVES['wzeta_approve']:
            status, tx_hash = await retry_function(zetachain.approve_wzeta, thread)
            if status:
                logger.success(
                    f"Поток {thread} | Апрувнул {config.APPROVES['wzeta_approve']} wzeta! {zetachain.web3_utils.acct.address}:{tx_hash}")
                await zetachain.sleep(config.DELAY['transaction'], logger, thread)
            else:
                logger.success(
                    f"Поток {thread} | Не апрувнул wzeta! {zetachain.web3_utils.acct.address}:{tx_hash}")

        # свап zeta на wzeta
        if await zetachain.get_wzeta_balance() < config.EDDY_SWAP['zeta_to_wzeta']:
            status, tx_hash = await retry_function(zetachain.swap_zeta_to_wzeta, thread)
            if status:
                logger.success(f"Поток {thread} | Сделал свап zeta -> wzeta! {zetachain.web3_utils.acct.address}:{tx_hash}")
                await zetachain.sleep(config.DELAY['transaction'], logger, thread)
            else:
                logger.success(
                    f"Поток {thread} | Не сделал свап zeta -> wzeta! {zetachain.web3_utils.acct.address}:{tx_hash}")

        # добавляет ликвидность в range protocol zeta/stzeta если баланс stzeta больше/равно POOLS['stzeta'], если баланс wzeta больше/равно EDDY_SWAP['zeta_to_wzeta'], если апрув stzeta больше/равно POOLS['stzeta'], если апрув wzeta больше/равно EDDY_SWAP['zeta_to_wzeta']
        if await zetachain.check_completed_task("RANGE_PROTOCOL_VAULT_TRANSACTION") and await zetachain.get_stzeta_balance() >= config.POOLS['stzeta'] and await zetachain.get_wzeta_balance() >= config.EDDY_SWAP['zeta_to_wzeta'] and await zetachain.allowance_stzeta() >= config.POOLS['stzeta'] and await zetachain.allowance_wzeta() >= config.EDDY_SWAP['zeta_to_wzeta']:
            status, tx_hash = await retry_function(zetachain.add_liquidity_range, thread)
            if status:
                logger.success(
                    f"Поток {thread} | Добавил ликвидность stzeta-wzeta! {zetachain.web3_utils.acct.address}:{tx_hash}")
                await zetachain.sleep(config.DELAY['transaction'], logger, thread)
            else:
                logger.error(
                    f"Поток {thread} | Не добавил ликвидность stzeta-wzeta! {zetachain.web3_utils.acct.address}:{tx_hash}")
            await zetachain.sleep(config.DELAY['quest'], logger, thread)

        if await zetachain.check_completed_task("ACCUMULATED_FINANCE_DEPOSIT"):
            # свап zeta на stzeta accumulated
            if await zetachain.get_balance_stzeta_accumulated_finance() < config.ACCUMULATED_FINANCE['zeta_to_stzeta']:
                status, tx_hash = await retry_function(zetachain.swap_zeta_to_stzeta_accumulated_finance, thread)
                if status:
                    logger.success(f"Поток {thread} | Свапнул на accumulated finance: zeta -> stzeta! {zetachain.web3_utils.acct.address}:{tx_hash}")
                    await zetachain.sleep(config.DELAY['transaction'], logger, thread)
                else:
                    logger.error(f"Поток {thread} | Не свапнул на accumulated finance: zeta -> stzeta! {zetachain.web3_utils.acct.address}:{tx_hash}")
                await zetachain.sleep(config.DELAY['quest'], logger, thread)

            # апрув stzeta accumulated finance
            if float(await zetachain.allowance_stzeta_accumulated_finance()) + 0.1 < config.APPROVES['stzeta_accumulated_approve']:
                status, tx_hash = await retry_function(zetachain.approve_stzeta_accumulated_finance, thread)
                if status:
                    logger.success(f"Поток {thread} | Апрувнул {config.APPROVES['stzeta_accumulated_approve']} stzeta для accumulated finance! {zetachain.web3_utils.acct.address}:{tx_hash}")
                    await zetachain.sleep(config.DELAY['transaction'], logger, thread)
                else:
                    logger.success(f"Поток {thread} | Не апрувнул stzeta! {zetachain.web3_utils.acct.address}:{tx_hash}")

            # свап stzeta accumulated finance на wstzeta
            if await zetachain.allowance_stzeta_accumulated_finance() >= config.ACCUMULATED_FINANCE['stzeta_to_wstzeta'] and await zetachain.get_balance_stzeta_accumulated_finance() >= config.ACCUMULATED_FINANCE['stzeta_to_wstzeta']:
                status, tx_hash = await retry_function(zetachain.swap_stzeta_to_wstzeta_accumulated_finance, thread)
                if status:
                    logger.success(f"Поток {thread} | Свапнул на accumulated finance: stzeta -> wstzeta! {zetachain.web3_utils.acct.address}:{tx_hash}")
                    await zetachain.sleep(config.DELAY['transaction'], logger, thread)
                else:
                    logger.success(f"Поток {thread} | Не свапнул на accumulated finance: stzeta -> wstzeta! {zetachain.web3_utils.acct.address}:{tx_hash}")

        # клеймит выполненые квесты
        claimed = await zetachain.claim_tasks()
        if claimed:
            logger.success(f"Поток {thread} | Заклеймил {claimed} квестов! {zetachain.web3_utils.acct.address}")
        else:
            logger.warning(f"Поток {thread} | Нет квестов для клейма! {zetachain.web3_utils.acct.address}")

        await zetachain.logout()
        await zetachain.sleep(config.DELAY['account'], logger, thread)

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
