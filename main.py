import random

from data import config
from core import ZetaChain
from core.utils import random_line, logger
import asyncio


async def retry_function(func, thread, address='', *args, **kwargs):
    e_count = 0
    while e_count < 4:
        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            for_address = f" для адреса {address}" if address else ''
            logger.error(f"Поток {thread} | Ошибка выполнения функции {func.__name__}{for_address}: {e}")
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
            status, tx_hash = await retry_function(zetachain.enroll, thread, zetachain.web3_utils.acct.address)
            if status:
                logger.success(f"Поток {thread} | Выполнил enroll! {zetachain.web3_utils.acct.address}:{tx_hash}")
                logger.info(f"Поток {thread} | Спит 20с после enroll!")

                await asyncio.sleep(20)
                await zetachain.new_session()
            else:
                logger.error(f"Поток {thread} | Не выполнил enroll! {zetachain.web3_utils.acct.address}:{tx_hash}")

        # апрув бнб
        if float(await zetachain.allowance_bnb())+0.001 < config.APPROVES['bnb_approve'][0]:
            status, tx_hash = await retry_function(zetachain.approve_bnb, thread, zetachain.web3_utils.acct.address)
            if status:
                logger.success(f"Поток {thread} | Апрувнул бнб! {zetachain.web3_utils.acct.address}:{tx_hash}")
                await zetachain.sleep(config.DELAY['transaction'], logger, thread)
            else:
                logger.error(f"Поток {thread} | Не апрувнул бнб! {zetachain.web3_utils.acct.address}:{tx_hash}")

        # апрув stzeta
        if float(await zetachain.allowance_stzeta())+0.1 < config.APPROVES['stzeta_approve'][0]:
            status, tx_hash = await retry_function(zetachain.approve_stzeta, thread, zetachain.web3_utils.acct.address)
            if status:
                logger.success(f"Поток {thread} | Апрувнул stzeta! {zetachain.web3_utils.acct.address}:{tx_hash}")
                await zetachain.sleep(config.DELAY['transaction'], logger, thread)
            else:
                logger.error(f"Поток {thread} | Не апрувнул stzeta! {zetachain.web3_utils.acct.address}:{tx_hash}")

        # апрув wzeta
        if float(await zetachain.allowance_wzeta()) + 0.1 < config.APPROVES['wzeta_approve'][0]:
            status, tx_hash = await retry_function(zetachain.approve_wzeta, thread, zetachain.web3_utils.acct.address)
            if status:
                logger.success(
                    f"Поток {thread} | Апрувнул wzeta! {zetachain.web3_utils.acct.address}:{tx_hash}")
                await zetachain.sleep(config.DELAY['transaction'], logger, thread)
            else:
                logger.error(f"Поток {thread} | Не апрувнул wzeta! {zetachain.web3_utils.acct.address}:{tx_hash}")

        # свап zeta на wzeta
        if await zetachain.get_wzeta_balance() < config.EDDY_SWAP['zeta_to_wzeta']:
            status, tx_hash = await retry_function(zetachain.swap_zeta_to_wzeta, thread, zetachain.web3_utils.acct.address)
            if status:
                logger.success(f"Поток {thread} | Сделал свап zeta -> wzeta! {zetachain.web3_utils.acct.address}:{tx_hash}")
                await zetachain.sleep(config.DELAY['transaction'], logger, thread)
            else:
                logger.error(f"Поток {thread} | Не сделал свап zeta -> wzeta! {zetachain.web3_utils.acct.address}:{tx_hash}")

        # апрув wzeta для zetaswap
        if float(await zetachain.allowance_zetaswap_wzeta()) + 0.1 < config.APPROVES['zetaswap_wzeta_approve'][0]:
            status, tx_hash = await retry_function(zetachain.approve_zetaswap_wzeta, thread, zetachain.web3_utils.acct.address)
            if status:
                logger.success(
                    f"Поток {thread} | Апрувнул wzeta для zetaswap! {zetachain.web3_utils.acct.address}:{tx_hash}")
                await zetachain.sleep(config.DELAY['transaction'], logger, thread)
            else:
                logger.error(f"Поток {thread} | Не апрувнул wzeta для zetaswap! {zetachain.web3_utils.acct.address}:{tx_hash}")

        modules = config.MODULES
        if config.SHUFFLE_MODULES:
            random.shuffle(modules)

        for func_name in modules:
            func = getattr(zetachain, func_name.__name__)
            try:
                await func()
            except Exception as e:
                logger.error(
                    f"Поток {thread} | ошибка выполнения модуля {func_name} для адреса {zetachain.web3_utils.acct.address}")

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

    thread_count = min(10, int(input("Введите кол-во потоков: ")))
    # thread_count = 1

    tasks = []
    for thread in range(1, thread_count+1):
        tasks.append(asyncio.create_task(ZC(thread)))

    await asyncio.gather(*tasks)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
