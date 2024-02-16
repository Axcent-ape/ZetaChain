import asyncio
import random
from data import config
from core.utils import Web3Utils
from fake_useragent import UserAgent
import aiohttp
import base64
from data import abi


class ZetaChain:
    def __init__(self, key: str, thread: int, proxy=None):
        self.web3_utils = Web3Utils(key=key, http_provider=config.RPCs['zetachain'])

        self.proxy = f"http://{proxy}" if proxy is not None else None
        self.thread = thread

        self.contract_for_encoding = self.web3_utils.w3.eth.contract(address=self.web3_utils.w3.to_checksum_address("0x8Afb66B7ffA1936ec5914c7089D50542520208b8"), abi=abi.encoding_contract_abi,)
        self.main_contract = self.web3_utils.w3.eth.contract(address=self.web3_utils.w3.to_checksum_address("0x34bc1b87f60e0a30c0e24FD7Abada70436c71406"), abi=abi.multicall_abi,)

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://hub.zetachain.com",
            "Referer": "https://hub.zetachain.com/",
            'User-Agent': UserAgent(os='windows').random,
        }

        self.session = aiohttp.ClientSession(headers=headers, trust_env=True,)

    async def new_session(self):
        await self.session.close()

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://hub.zetachain.com",
            "Referer": "https://hub.zetachain.com/",
            'User-Agent': UserAgent(os='windows').random,
        }

        self.session = aiohttp.ClientSession(headers=headers, trust_env=True)

    @staticmethod
    async def sleep():
        rs = random.randint(config.DELAY[0], config.DELAY[1])
        await asyncio.sleep(rs)
        return rs

    async def logout(self):

        await self.session.close()

    # @staticmethod
    async def get_referral_data(self):
        if config.REF_LINK:
            address, expiration, r, s, v = base64.b64decode(config.REF_LINK.split('code=')[1][:-1]).decode().split('&')

            address = address.split('=')[1][2:]
            expiration = self.web3_utils.w3.to_hex(int(expiration.split('=')[1]))[2:]
            r = r.split('=')[1][2:]
            s = s.split('=')[1][2:]
            v = self.web3_utils.w3.to_hex(int(v.split('=')[1][:2]))[2:]

            return f"0xb9daad50000000000000000000000000{address.lower()}00000000000000000000000000000000000000000000000000000000{expiration}00000000000000000000000000000000000000000000000000000000000000{v}{r}{s}"
        else:
            return "0x90c08473"

    async def check_completed_task(self, task):
        resp = await self.session.get(f'https://xp.cl04.zetachain.com/v1/get-user-has-xp-to-refresh?address={self.web3_utils.acct.address}', proxy=self.proxy)
        resp_json = await resp.json()

        return resp_json.get('xpRefreshTrackingByTask').get(task).get('hasXpToRefresh') is False and resp_json.get('xpRefreshTrackingByTask').get(task).get('hasAlreadyEarned') is False

    async def check_enroll(self):
        json_data = {'address': self.web3_utils.acct.address}
        resp = await self.session.post("https://xp.cl04.zetachain.com/v1/enroll-in-zeta-xp", json=json_data, proxy=self.proxy)
        a = await resp.json()

        return (a).get('isUserVerified') is True

    async def enroll(self):
        data = await self.get_referral_data()
        tx = {
            "from": self.web3_utils.acct.address,
            "to": "0x3C85e0cA1001F085A3e58d55A0D76E2E8B0A33f9",
            "value": 0,
            "nonce": self.web3_utils.w3.eth.get_transaction_count(self.web3_utils.acct.address),
            "gasPrice": self.web3_utils.w3.eth.gas_price,
            "chainId": 7000,
            "data": data,
        }

        tx["gas"] = int(self.web3_utils.w3.eth.estimate_gas(tx))

        tx = self.web3_utils.w3.eth.account.sign_transaction(tx, self.web3_utils.acct.key.hex())
        transaction_hash = self.web3_utils.w3.eth.send_raw_transaction(tx.rawTransaction).hex()
        wait_tx = self.web3_utils.w3.eth.wait_for_transaction_receipt(transaction_hash)

        return wait_tx.status == 1, transaction_hash

    async def transfer_zeta(self):
        tx = {
            "from": self.web3_utils.acct.address,
            "to": self.web3_utils.acct.address,
            "value": self.web3_utils.w3.to_wei(config.SENDS_QUESTS['send_zeta'][1], "ether"),
            "nonce": self.web3_utils.w3.eth.get_transaction_count(self.web3_utils.acct.address),
            "gasPrice": self.web3_utils.w3.eth.gas_price,
            "chainId": 7000,
        }

        tx["gas"] = int(self.web3_utils.w3.eth.estimate_gas(tx))

        tx = self.web3_utils.w3.eth.account.sign_transaction(tx, self.web3_utils.acct.key.hex())
        transaction_hash = self.web3_utils.w3.eth.send_raw_transaction(tx.rawTransaction).hex()
        wait_tx = self.web3_utils.w3.eth.wait_for_transaction_receipt(transaction_hash)

        return wait_tx.status == 1, transaction_hash

    async def transfer_bnb(self):
        encoded_data = self.contract_for_encoding.encodeABI(
            fn_name="swapAmount",
            args=[
                (
                    b"_\x0b\x1a\x82t\x9c\xb4\xe2'\x8e\xc8\x7f\x8b\xf6\xb6\x18\xdcq\xa8\xbf\x00'\x10H\xf8\x06\x08\xb6r\xdc0\xdc~=\xbb\xd04<_\x02\xc78\xeb",
                    self.web3_utils.acct.address,
                    self.web3_utils.w3.to_wei(config.SENDS_QUESTS['send_bnb'][1], "ether"),
                    10,
                    self.web3_utils.w3.eth.get_block("latest").timestamp + 3600,
                )
            ],
        )
        tx_data = self.main_contract.encodeABI(fn_name="multicall", args=[[encoded_data, "0x12210e8a"]])

        tx = {
            "from": self.web3_utils.acct.address,
            "to": self.web3_utils.w3.to_checksum_address("0x34bc1b87f60e0a30c0e24FD7Abada70436c71406"),
            "value": self.web3_utils.w3.to_wei(config.SENDS_QUESTS['send_bnb'][1], "ether"),
            "nonce": self.web3_utils.w3.eth.get_transaction_count(self.web3_utils.acct.address),
            "gasPrice": self.web3_utils.w3.eth.gas_price,
            "chainId": 7000,
            "data": tx_data,
        }
        tx["gas"] = int(self.web3_utils.w3.eth.estimate_gas(tx))
        tx = self.web3_utils.w3.eth.account.sign_transaction(tx, self.web3_utils.acct.key.hex())
        transaction_hash = self.web3_utils.w3.eth.send_raw_transaction(tx.rawTransaction).hex()

        wait_tx = self.web3_utils.w3.eth.wait_for_transaction_receipt(transaction_hash)
        return wait_tx.status == 1, transaction_hash

    async def transfer_eth(self):
        encoded_data = self.contract_for_encoding.encodeABI(
            fn_name="swapAmount",
            args=[
                (
                    b"_\x0b\x1a\x82t\x9c\xb4\xe2'\x8e\xc8\x7f\x8b\xf6\xb6\x18\xdcq\xa8\xbf\x00\x0b\xb8\x91\xd4\xf0\xd5@\x90\xdf-\x81\xe84\xc3\xc8\xceq\xc6\xc8e\xe7\x9f\x00\x0b\xb8\xd9{\x1d\xe3a\x9e\xd2\xc6\xbe\xb3\x86\x01G\xe3\x0c\xa8\xa7\xdc\x98\x91",
                    self.web3_utils.acct.address,
                    self.web3_utils.w3.to_wei(config.SENDS_QUESTS['send_eth'][1], "ether"),
                    10,
                    self.web3_utils.w3.eth.get_block("latest").timestamp + 3600,
                )
            ],
        )
        tx_data = self.main_contract.encodeABI(fn_name="multicall", args=[[encoded_data, "0x12210e8a"]])

        tx = {
            "from": self.web3_utils.acct.address,
            "to": self.web3_utils.w3.to_checksum_address("0x34bc1b87f60e0a30c0e24FD7Abada70436c71406"),
            "value": self.web3_utils.w3.to_wei(config.SENDS_QUESTS['send_eth'][1], "ether"),
            "nonce": self.web3_utils.w3.eth.get_transaction_count(self.web3_utils.acct.address),
            "gasPrice": self.web3_utils.w3.eth.gas_price,
            "chainId": 7000,
            "data": tx_data,
        }
        tx["gas"] = int(self.web3_utils.w3.eth.estimate_gas(tx))

        tx = self.web3_utils.w3.eth.account.sign_transaction(tx, self.web3_utils.acct.key.hex())
        transaction_hash = self.web3_utils.w3.eth.send_raw_transaction(tx.rawTransaction).hex()

        wait_tx = self.web3_utils.w3.eth.wait_for_transaction_receipt(transaction_hash)
        return wait_tx.status == 1, transaction_hash

    async def transfer_btc(self):
        encoded_data = self.contract_for_encoding.encodeABI(
            fn_name="swapAmount",
            args=[
                (
                    b"_\x0b\x1a\x82t\x9c\xb4\xe2'\x8e\xc8\x7f\x8b\xf6\xb6\x18\xdcq\xa8\xbf\x00'\x10|\x8d\xda\x80\xbb\xbe\x12T\xa7\xaa\xcf2\x19\xeb\xe1H\x1cn\x01\xd7\x00'\x10_\x0b\x1a\x82t\x9c\xb4\xe2'\x8e\xc8\x7f\x8b\xf6\xb6\x18\xdcq\xa8\xbf\x00'\x10\x13\xa0\xc5\x93\x0c\x02\x85\x11\xdc\x02f^r\x85\x13Km\x11\xa5\xf4",
                    self.web3_utils.acct.address,
                    self.web3_utils.w3.to_wei(config.SENDS_QUESTS['send_btc'][1], "ether"),
                    3,
                    self.web3_utils.w3.eth.get_block("latest").timestamp + 3600,
                )
            ],
        )
        tx_data = self.main_contract.encodeABI(fn_name="multicall", args=[[encoded_data, "0x12210e8a"]])

        tx = {
            "from": self.web3_utils.acct.address,
            "to": self.web3_utils.w3.to_checksum_address("0x34bc1b87f60e0a30c0e24FD7Abada70436c71406"),
            "value": self.web3_utils.w3.to_wei(config.SENDS_QUESTS['send_btc'][1], "ether"),
            "nonce": self.web3_utils.w3.eth.get_transaction_count(self.web3_utils.acct.address),
            "gasPrice": self.web3_utils.w3.eth.gas_price,
            "chainId": 7000,
            "data": tx_data,
        }
        tx["gas"] = int(self.web3_utils.w3.eth.estimate_gas(tx))

        tx = self.web3_utils.w3.eth.account.sign_transaction(tx, self.web3_utils.acct.key.hex())
        transaction_hash = self.web3_utils.w3.eth.send_raw_transaction(tx.rawTransaction).hex()

        wait_tx = self.web3_utils.w3.eth.wait_for_transaction_receipt(transaction_hash)
        return wait_tx.status == 1, transaction_hash

    async def add_liquidity(self):
        contract = self.web3_utils.w3.eth.contract(
            address=self.web3_utils.w3.to_checksum_address("0x2ca7d64A7EFE2D62A725E2B35Cf7230D6677FfEe"),
            abi=abi.pool_abi,
        )

        tx = contract.functions.addLiquidityETH(self.web3_utils.w3.to_checksum_address("0x48f80608B672DC30DC7e3dbBd0343c5F02C738Eb"), self.web3_utils.w3.to_wei(config.POOLS['send_bnb'], "ether"), 0, 0, self.web3_utils.acct.address, self.web3_utils.w3.eth.get_block("latest").timestamp + 3600,
        ).build_transaction(
            {
                "from": self.web3_utils.acct.address,
                "value": self.web3_utils.w3.to_wei(config.POOLS['send_zeta'], "ether"),
                "nonce": self.web3_utils.w3.eth.get_transaction_count(self.web3_utils.acct.address),
                "gasPrice": self.web3_utils.w3.eth.gas_price,
                "chainId": 7000,
            }
        )

        tx["gas"] = int(self.web3_utils.w3.eth.estimate_gas(tx))

        tx = self.web3_utils.w3.eth.account.sign_transaction(tx, self.web3_utils.acct.key.hex())
        transaction_hash = self.web3_utils.w3.eth.send_raw_transaction(tx.rawTransaction).hex()
        wait_tx = self.web3_utils.w3.eth.wait_for_transaction_receipt(transaction_hash)

        return wait_tx.status == 1, transaction_hash

    async def claim_tasks(self):
        resp = await self.session.get(f'https://xp.cl04.zetachain.com/v1/get-user-has-xp-to-refresh?address={self.web3_utils.acct.address}', proxy=self.proxy)
        resp_json = await resp.json()

        tasks_for_claim = [key for key, value in resp_json["xpRefreshTrackingByTask"].items() if value["hasXpToRefresh"]]

        success = 0
        for task in tasks_for_claim:
            claim_data = {
                "address": self.web3_utils.acct.address,
                "task": task,
                "signedMessage": self.web3_utils.get_signed_code_struct({"types": {"Message": [{"name": "content", "type": "string"}],"EIP712Domain": [{"name": "name", "type": "string"},{"name": "version", "type": "string"},{"name": "chainId", "type": "uint256"},],},"domain": {"name": "Hub/XP", "version": "1", "chainId": 7000},"primaryType": "Message","message": {"content": "Claim XP"},}),
            }

            resp = await self.session.post('https://xp.cl04.zetachain.com/v1/xp/claim-task', json=claim_data, proxy=self.proxy)
            if (await resp.json()).get('message') == 'XP refreshed successfully':
                success += 1

        return success

    async def check_approve_bnb(self):
        contract = self.web3_utils.w3.eth.contract(address=self.web3_utils.w3.to_checksum_address("0x48f80608B672DC30DC7e3dbBd0343c5F02C738Eb"), abi=abi.approve_abi)
        return self.web3_utils.w3.from_wei(contract.functions.allowance(self.web3_utils.w3.to_checksum_address(self.web3_utils.acct.address), self.web3_utils.w3.to_checksum_address("0x2ca7d64A7EFE2D62A725E2B35Cf7230D6677FfEe")).call(), 'ether')

    async def approve_bnb(self):
        contract = self.web3_utils.w3.eth.contract(address=self.web3_utils.w3.to_checksum_address("0x48f80608B672DC30DC7e3dbBd0343c5F02C738Eb"), abi=abi.approve_abi)

        tx = contract.functions.approve(self.web3_utils.w3.to_checksum_address('0x2ca7d64A7EFE2D62A725E2B35Cf7230D6677FfEe'), self.web3_utils.w3.to_wei(config.APPROVES['bnb_approve'], "ether"),
        ).build_transaction(
            {
                "from": self.web3_utils.acct.address,
                "value": 0,
                "nonce": self.web3_utils.w3.eth.get_transaction_count(self.web3_utils.acct.address),
                "gasPrice": self.web3_utils.w3.eth.gas_price,
                "chainId": 7000,
            }
        )
        tx["gas"] = int(self.web3_utils.w3.eth.estimate_gas(tx))

        tx = self.web3_utils.w3.eth.account.sign_transaction(tx, self.web3_utils.acct.key.hex())
        transaction_hash = self.web3_utils.w3.eth.send_raw_transaction(tx.rawTransaction).hex()
        wait_tx = self.web3_utils.w3.eth.wait_for_transaction_receipt(transaction_hash)

        return wait_tx.status == 1, transaction_hash
