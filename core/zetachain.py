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

        self.session = aiohttp.ClientSession(headers=headers, trust_env=True)

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
    async def sleep(interval, logger, thread: int):
        rs = random.randint(interval[0], interval[1])
        logger.info(f"Поток {thread} | Спит {rs} секунд")

        await asyncio.sleep(rs)

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
            # "gasPrice": self.web3_utils.w3.eth.gas_price,
            "chainId": 7000,
            "data": data,
        }

        max_priority_fee_per_gas_gwei, max_fee_per_gas_gwei = self.web3_utils.gas_eip_1559()

        tx["gas"] = int(self.web3_utils.w3.eth.estimate_gas(tx))
        tx["maxPriorityFeePerGas"] = self.web3_utils.w3.to_wei(max_priority_fee_per_gas_gwei, 'gwei')
        tx["maxFeePerGas"] = self.web3_utils.w3.to_wei(max_fee_per_gas_gwei, 'gwei')

        tx = self.web3_utils.w3.eth.account.sign_transaction(tx, self.web3_utils.acct.key.hex())
        transaction_hash = self.web3_utils.w3.eth.send_raw_transaction(tx.rawTransaction).hex()
        wait_tx = self.web3_utils.w3.eth.wait_for_transaction_receipt(transaction_hash)

        return wait_tx.status == 1, transaction_hash

    async def transfer_zeta(self):
        random_value = round(random.uniform(config.SENDS_QUESTS['send_zeta'][0], config.SENDS_QUESTS['send_zeta'][1]), 10)

        tx = {
            "from": self.web3_utils.acct.address,
            "to": self.web3_utils.acct.address,
            "value": self.web3_utils.w3.to_wei(random_value, "ether"),
            "nonce": self.web3_utils.w3.eth.get_transaction_count(self.web3_utils.acct.address),
            # "gasPrice": self.web3_utils.w3.eth.gas_price,
            "chainId": 7000,
        }

        max_priority_fee_per_gas_gwei, max_fee_per_gas_gwei = self.web3_utils.gas_eip_1559()

        tx["gas"] = int(self.web3_utils.w3.eth.estimate_gas(tx))
        tx["maxPriorityFeePerGas"] = self.web3_utils.w3.to_wei(max_priority_fee_per_gas_gwei, 'gwei')
        tx["maxFeePerGas"] = self.web3_utils.w3.to_wei(max_fee_per_gas_gwei, 'gwei')

        tx = self.web3_utils.w3.eth.account.sign_transaction(tx, self.web3_utils.acct.key.hex())
        transaction_hash = self.web3_utils.w3.eth.send_raw_transaction(tx.rawTransaction).hex()
        wait_tx = self.web3_utils.w3.eth.wait_for_transaction_receipt(transaction_hash)

        return wait_tx.status == 1, transaction_hash, random_value

    async def transfer_bnb(self):
        random_value = round(random.uniform(config.SENDS_QUESTS['send_bnb'][0], config.SENDS_QUESTS['send_bnb'][1]), 10)

        encoded_data = self.contract_for_encoding.encodeABI(
            fn_name="swapAmount",
            args=[
                (
                    b"_\x0b\x1a\x82t\x9c\xb4\xe2'\x8e\xc8\x7f\x8b\xf6\xb6\x18\xdcq\xa8\xbf\x00'\x10H\xf8\x06\x08\xb6r\xdc0\xdc~=\xbb\xd04<_\x02\xc78\xeb",
                    self.web3_utils.acct.address,
                    self.web3_utils.w3.to_wei(random_value, "ether"),
                    10,
                    self.web3_utils.w3.eth.get_block("latest").timestamp + 3600,
                )
            ],
        )
        tx_data = self.main_contract.encodeABI(fn_name="multicall", args=[[encoded_data, "0x12210e8a"]])

        tx = {
            "from": self.web3_utils.acct.address,
            "to": self.web3_utils.w3.to_checksum_address("0x34bc1b87f60e0a30c0e24FD7Abada70436c71406"),
            "value": self.web3_utils.w3.to_wei(random_value, "ether"),
            "nonce": self.web3_utils.w3.eth.get_transaction_count(self.web3_utils.acct.address),
            # "gasPrice": self.web3_utils.w3.eth.gas_price,
            "chainId": 7000,
            "data": tx_data,
        }

        max_priority_fee_per_gas_gwei, max_fee_per_gas_gwei = self.web3_utils.gas_eip_1559()

        tx["gas"] = int(self.web3_utils.w3.eth.estimate_gas(tx))
        tx["maxPriorityFeePerGas"] = self.web3_utils.w3.to_wei(max_priority_fee_per_gas_gwei, 'gwei')
        tx["maxFeePerGas"] = self.web3_utils.w3.to_wei(max_fee_per_gas_gwei, 'gwei')

        tx = self.web3_utils.w3.eth.account.sign_transaction(tx, self.web3_utils.acct.key.hex())
        transaction_hash = self.web3_utils.w3.eth.send_raw_transaction(tx.rawTransaction).hex()

        wait_tx = self.web3_utils.w3.eth.wait_for_transaction_receipt(transaction_hash)
        return wait_tx.status == 1, transaction_hash, random_value

    async def transfer_eth(self):
        random_value = round(random.uniform(config.SENDS_QUESTS['send_eth'][0], config.SENDS_QUESTS['send_eth'][1]), 10)

        encoded_data = self.contract_for_encoding.encodeABI(
            fn_name="swapAmount",
            args=[
                (
                    b"_\x0b\x1a\x82t\x9c\xb4\xe2'\x8e\xc8\x7f\x8b\xf6\xb6\x18\xdcq\xa8\xbf\x00\x0b\xb8\x91\xd4\xf0\xd5@\x90\xdf-\x81\xe84\xc3\xc8\xceq\xc6\xc8e\xe7\x9f\x00\x0b\xb8\xd9{\x1d\xe3a\x9e\xd2\xc6\xbe\xb3\x86\x01G\xe3\x0c\xa8\xa7\xdc\x98\x91",
                    self.web3_utils.acct.address,
                    self.web3_utils.w3.to_wei(random_value, "ether"),
                    10,
                    self.web3_utils.w3.eth.get_block("latest").timestamp + 3600,
                )
            ],
        )
        tx_data = self.main_contract.encodeABI(fn_name="multicall", args=[[encoded_data, "0x12210e8a"]])

        tx = {
            "from": self.web3_utils.acct.address,
            "to": self.web3_utils.w3.to_checksum_address("0x34bc1b87f60e0a30c0e24FD7Abada70436c71406"),
            "value": self.web3_utils.w3.to_wei(random_value, "ether"),
            "nonce": self.web3_utils.w3.eth.get_transaction_count(self.web3_utils.acct.address),
            # "gasPrice": self.web3_utils.w3.eth.gas_price,
            "chainId": 7000,
            "data": tx_data,
        }

        max_priority_fee_per_gas_gwei, max_fee_per_gas_gwei = self.web3_utils.gas_eip_1559()

        tx["gas"] = int(self.web3_utils.w3.eth.estimate_gas(tx))
        tx["maxPriorityFeePerGas"] = self.web3_utils.w3.to_wei(max_priority_fee_per_gas_gwei, 'gwei')
        tx["maxFeePerGas"] = self.web3_utils.w3.to_wei(max_fee_per_gas_gwei, 'gwei')

        tx = self.web3_utils.w3.eth.account.sign_transaction(tx, self.web3_utils.acct.key.hex())
        transaction_hash = self.web3_utils.w3.eth.send_raw_transaction(tx.rawTransaction).hex()

        wait_tx = self.web3_utils.w3.eth.wait_for_transaction_receipt(transaction_hash)
        return wait_tx.status == 1, transaction_hash, random_value

    async def transfer_btc(self):
        random_value = round(random.uniform(config.SENDS_QUESTS['send_btc'][0], config.SENDS_QUESTS['send_btc'][1]), 10)

        encoded_data = self.contract_for_encoding.encodeABI(
            fn_name="swapAmount",
            args=[
                (
                    b"_\x0b\x1a\x82t\x9c\xb4\xe2'\x8e\xc8\x7f\x8b\xf6\xb6\x18\xdcq\xa8\xbf\x00'\x10|\x8d\xda\x80\xbb\xbe\x12T\xa7\xaa\xcf2\x19\xeb\xe1H\x1cn\x01\xd7\x00'\x10_\x0b\x1a\x82t\x9c\xb4\xe2'\x8e\xc8\x7f\x8b\xf6\xb6\x18\xdcq\xa8\xbf\x00'\x10\x13\xa0\xc5\x93\x0c\x02\x85\x11\xdc\x02f^r\x85\x13Km\x11\xa5\xf4",
                    self.web3_utils.acct.address,
                    self.web3_utils.w3.to_wei(random_value, "ether"),
                    3,
                    self.web3_utils.w3.eth.get_block("latest").timestamp + 3600,
                )
            ],
        )
        tx_data = self.main_contract.encodeABI(fn_name="multicall", args=[[encoded_data, "0x12210e8a"]])

        tx = {
            "from": self.web3_utils.acct.address,
            "to": self.web3_utils.w3.to_checksum_address("0x34bc1b87f60e0a30c0e24FD7Abada70436c71406"),
            "value": self.web3_utils.w3.to_wei(random_value, "ether"),
            "nonce": self.web3_utils.w3.eth.get_transaction_count(self.web3_utils.acct.address),
            # "gasPrice": self.web3_utils.w3.eth.gas_price,
            "chainId": 7000,
            "data": tx_data,
        }

        max_priority_fee_per_gas_gwei, max_fee_per_gas_gwei = self.web3_utils.gas_eip_1559()

        tx["gas"] = int(self.web3_utils.w3.eth.estimate_gas(tx))
        tx["maxPriorityFeePerGas"] = self.web3_utils.w3.to_wei(max_priority_fee_per_gas_gwei, 'gwei')
        tx["maxFeePerGas"] = self.web3_utils.w3.to_wei(max_fee_per_gas_gwei, 'gwei')

        tx = self.web3_utils.w3.eth.account.sign_transaction(tx, self.web3_utils.acct.key.hex())
        transaction_hash = self.web3_utils.w3.eth.send_raw_transaction(tx.rawTransaction).hex()

        wait_tx = self.web3_utils.w3.eth.wait_for_transaction_receipt(transaction_hash)
        return wait_tx.status == 1, transaction_hash, random_value

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
                # "gasPrice": self.web3_utils.w3.eth.gas_price,
                "chainId": 7000,
            }
        )

        max_priority_fee_per_gas_gwei, max_fee_per_gas_gwei = self.web3_utils.gas_eip_1559()

        tx["gas"] = int(self.web3_utils.w3.eth.estimate_gas(tx))
        tx["maxPriorityFeePerGas"] = self.web3_utils.w3.to_wei(max_priority_fee_per_gas_gwei, 'gwei')
        tx["maxFeePerGas"] = self.web3_utils.w3.to_wei(max_fee_per_gas_gwei, 'gwei')

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

    async def allowance_bnb(self):
        return self.web3_utils.allowance(spender="0x2ca7d64A7EFE2D62A725E2B35Cf7230D6677FfEe", contract="0x48f80608B672DC30DC7e3dbBd0343c5F02C738Eb", abi=abi.approve_abi)

    async def allowance_stzeta(self):
        return self.web3_utils.allowance(spender="0x08f4539f91faa96b34323c11c9b00123ba19eef3", contract="0x45334a5b0a01ce6c260f2b570ec941c680ea62c0", abi=abi.approve_abi)

    async def allowance_wzeta(self):
        return self.web3_utils.allowance(spender="0x08f4539f91faa96b34323c11c9b00123ba19eef3", contract="0x5f0b1a82749cb4e2278ec87f8bf6b618dc71a8bf", abi=abi.approve_abi)

    async def approve_bnb(self):
        spender = "0x2ca7d64A7EFE2D62A725E2B35Cf7230D6677FfEe"
        contract = "0x48f80608B672DC30DC7e3dbBd0343c5F02C738Eb"
        random_value = round(random.uniform(config.APPROVES['bnb_approve'][0], config.APPROVES['bnb_approve'][1]), 10)
        return self.web3_utils.approve(spender, random_value, abi.approve_abi, contract)

    async def approve_stzeta(self):
        spender = "0x08f4539f91faa96b34323c11c9b00123ba19eef3"
        contract = "0x45334a5b0a01ce6c260f2b570ec941c680ea62c0"
        random_value = round(random.uniform(config.APPROVES['bnb_approve'][0], config.APPROVES['bnb_approve'][1]), 10)
        return self.web3_utils.approve(spender, random_value, abi.approve_abi, contract)

    async def approve_wzeta(self):
        spender = "0x08f4539f91faa96b34323c11c9b00123ba19eef3"
        contract = "0x5f0b1a82749cb4e2278ec87f8bf6b618dc71a8bf"
        random_value = round(random.uniform(config.APPROVES['bnb_approve'][0], config.APPROVES['bnb_approve'][1]), 10)
        return self.web3_utils.approve(spender, random_value, abi.approve_abi, contract)

    async def swap_zeta_to_stzeta(self):
        from_ = "0x5f0b1a82749cb4e2278ec87f8bf6b618dc71a8bf"   # zeta
        to = "0x45334a5b0a01ce6c260f2b570ec941c680ea62c0"      # stzeta

        return self.web3_utils.eddy_finance_swap(from_, to, config.EDDY_SWAP["zeta_to_stzeta"])

    async def swap_zeta_to_wzeta(self):
        tx = {
            "from": self.web3_utils.acct.address,
            "to": self.web3_utils.w3.to_checksum_address("0x5f0b1a82749cb4e2278ec87f8bf6b618dc71a8bf"),
            "value": self.web3_utils.w3.to_wei(config.EDDY_SWAP['zeta_to_wzeta'], "ether"),
            "nonce": self.web3_utils.w3.eth.get_transaction_count(self.web3_utils.acct.address),
            # "gasPrice": self.web3_utils.w3.eth.gas_price,
            "chainId": 7000,
            "data": "0xd0e30db0",
        }

        max_priority_fee_per_gas_gwei, max_fee_per_gas_gwei = self.web3_utils.gas_eip_1559()

        tx["gas"] = int(self.web3_utils.w3.eth.estimate_gas(tx))
        tx["maxPriorityFeePerGas"] = self.web3_utils.w3.to_wei(max_priority_fee_per_gas_gwei, 'gwei')
        tx["maxFeePerGas"] = self.web3_utils.w3.to_wei(max_fee_per_gas_gwei, 'gwei')

        tx = self.web3_utils.w3.eth.account.sign_transaction(tx, self.web3_utils.acct.key.hex())
        transaction_hash = self.web3_utils.w3.eth.send_raw_transaction(tx.rawTransaction).hex()

        wait_tx = self.web3_utils.w3.eth.wait_for_transaction_receipt(transaction_hash)
        return wait_tx.status == 1, transaction_hash

    async def get_wzeta_balance(self):
        return self.web3_utils.w3.from_wei(self.web3_utils.balance_of_erc20(self.web3_utils.acct.address, '0x5F0b1a82749cb4E2278EC87F8BF6B618dC71a8bf'),'ether')

    async def get_stzeta_balance(self):
        return self.web3_utils.w3.from_wei(self.web3_utils.balance_of_erc20(self.web3_utils.acct.address, '0x45334a5b0a01ce6c260f2b570ec941c680ea62c0'), 'ether')

    async def get_price_range(self):
        json_data = {"query":"\n      query getVaultItemById($vaultId: String) {\n        vault(id: $vaultId) {\n          \n  id\n  liquidity\n  balance0\n  balance1\n  totalSupply\n  totalFeesEarned0\n  totalFeesEarned1\n  tokenX\n  tokenY\n  firstMintAtBlock\n  managerBalanceX\n  managerBalanceY\n  name\n  tag\n  pool\n\n          managingFee\n          performanceFee\n        }\n      }\n    ","variables":{"vaultId":"0x08F4539f91faA96b34323c11C9B00123bA19eef3"},"operationName":"getVaultItemById"}
        url = "https://api.goldsky.com/api/public/project_clm97huay3j9y2nw04d8nhmrt/subgraphs/izumi-zetachain/0.2/gn"

        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, json=json_data) as resp:
                resp_json = await resp.json()

        percent = int(resp_json['data']['vault']['balance0'])/int(resp_json['data']['vault']['balance1'])
        return percent

    def generate_data_range(self, stzeta_amount, wzeta_amount, mint_amount):
        stzeta_hex = self.web3_utils.w3.to_hex(stzeta_amount)[2:]
        wzeta_hex = self.web3_utils.w3.to_hex(wzeta_amount)[2:]
        mint_hex = self.web3_utils.w3.to_hex(mint_amount)[2:]

        stzeta = '0' * (64 - len(stzeta_hex)) + stzeta_hex
        wzeta = '0' * (64 - len(wzeta_hex)) + wzeta_hex
        mint = '0' * (64 - len(mint_hex)) + mint_hex

        return f"0xb341ee9f{mint.lower()}{stzeta.lower()}{wzeta.lower()}"

    async def mint_amount(self):
        contract = self.web3_utils.w3.eth.contract(address=self.web3_utils.w3.to_checksum_address("0x08f4539f91faa96b34323c11c9b00123ba19eef3"), abi=abi.range_protocol_abi)
        percent = await self.get_price_range()

        token_x = self.web3_utils.w3.to_wei(config.POOLS['stzeta'], 'ether')
        token_y = self.web3_utils.w3.to_wei(config.POOLS['stzeta']/percent, 'ether')
        return contract.functions.getMintAmounts(int(token_x), int(token_y)).call()

    async def add_liquidity_range(self):
        stzeta_amount, wzeta_amount, mint_amount = await self.mint_amount()

        # print(stzeta_amount, wzeta_amount, mint_amount)
        # print(f"ztzeta: {stzeta_amount}({stzeta_amount/1e18}), wzeta: {wzeta_amount}({wzeta_amount/1e18}), mint amount: {mint_amount}({mint_amount/1e18})")

        tx = {
            "from": self.web3_utils.acct.address,
            "to": self.web3_utils.w3.to_checksum_address("0x08F4539f91faA96b34323c11C9B00123bA19eef3"),
            "value": 0,
            "nonce": self.web3_utils.w3.eth.get_transaction_count(self.web3_utils.acct.address),
            # "gasPrice": self.web3_utils.w3.eth.gas_price,
            "chainId": 7000,
            "data": self.generate_data_range(stzeta_amount, wzeta_amount, mint_amount),
        }

        max_priority_fee_per_gas_gwei, max_fee_per_gas_gwei = self.web3_utils.gas_eip_1559()

        tx["gas"] = int(self.web3_utils.w3.eth.estimate_gas(tx))
        tx["maxPriorityFeePerGas"] = self.web3_utils.w3.to_wei(max_priority_fee_per_gas_gwei, 'gwei')
        tx["maxFeePerGas"] = self.web3_utils.w3.to_wei(max_fee_per_gas_gwei, 'gwei')

        tx = self.web3_utils.w3.eth.account.sign_transaction(tx, self.web3_utils.acct.key.hex())
        transaction_hash = self.web3_utils.w3.eth.send_raw_transaction(tx.rawTransaction).hex()

        wait_tx = self.web3_utils.w3.eth.wait_for_transaction_receipt(transaction_hash)
        return wait_tx.status == 1, transaction_hash

    async def swap_zeta_to_stzeta_accumulated_finance(self):
        tx = {
            "from": self.web3_utils.acct.address,
            "to": self.web3_utils.w3.to_checksum_address("0xcf1A40eFf1A4d4c56DC4042A1aE93013d13C3217"),
            "value": self.web3_utils.w3.to_wei(config.ACCUMULATED_FINANCE['zeta_to_stzeta'], 'ether'),
            "nonce": self.web3_utils.w3.eth.get_transaction_count(self.web3_utils.acct.address),
            # "gasPrice": self.web3_utils.w3.eth.gas_price,
            "chainId": 7000,
            "data": f"0xf340fa01000000000000000000000000{self.web3_utils.acct.address[2:]}",
        }

        max_priority_fee_per_gas_gwei, max_fee_per_gas_gwei = self.web3_utils.gas_eip_1559()

        tx["gas"] = int(self.web3_utils.w3.eth.estimate_gas(tx))
        tx["maxPriorityFeePerGas"] = self.web3_utils.w3.to_wei(max_priority_fee_per_gas_gwei, 'gwei')
        tx["maxFeePerGas"] = self.web3_utils.w3.to_wei(max_fee_per_gas_gwei, 'gwei')

        tx = self.web3_utils.w3.eth.account.sign_transaction(tx, self.web3_utils.acct.key.hex())
        transaction_hash = self.web3_utils.w3.eth.send_raw_transaction(tx.rawTransaction).hex()

        wait_tx = self.web3_utils.w3.eth.wait_for_transaction_receipt(transaction_hash)
        return wait_tx.status == 1, transaction_hash

    async def get_balance_stzeta_accumulated_finance(self):
        return self.web3_utils.w3.from_wei(self.web3_utils.balance_of_erc20(self.web3_utils.acct.address, '0xcba2aeec821b0b119857a9ab39e09b034249681a'), 'ether')

    async def allowance_stzeta_accumulated_finance(self):
        return self.web3_utils.allowance(spender="0x7ac168c81f4f3820fa3f22603ce5864d6ab3c547", contract="0xcba2aeec821b0b119857a9ab39e09b034249681a", abi=abi.approve_abi)

    async def approve_stzeta_accumulated_finance(self):
        spender = "0x7ac168c81f4f3820fa3f22603ce5864d6ab3c547"
        contract = "0xcba2aeec821b0b119857a9ab39e09b034249681a"
        random_value = round(random.uniform(config.APPROVES['bnb_approve'][0], config.APPROVES['bnb_approve'][1]), 10)
        return self.web3_utils.approve(spender, random_value, abi.approve_abi, contract)

    async def swap_stzeta_to_wstzeta_accumulated_finance(self):
        amount_hex = self.web3_utils.w3.to_hex(self.web3_utils.w3.to_wei(config.ACCUMULATED_FINANCE['stzeta_to_wstzeta'], 'ether'))[2:]
        amount = '0' * (64 - len(amount_hex)) + amount_hex

        data = f"0x6e553f65{amount}000000000000000000000000{self.web3_utils.acct.address[2:]}"

        tx = {
            "from": self.web3_utils.acct.address,
            "to": self.web3_utils.w3.to_checksum_address("0x7AC168c81F4F3820Fa3F22603ce5864D6aB3C547"),
            "value": 0,
            "nonce": self.web3_utils.w3.eth.get_transaction_count(self.web3_utils.acct.address),
            # "gasPrice": self.web3_utils.w3.eth.gas_price,
            "chainId": 7000,
            "data": data,
        }

        max_priority_fee_per_gas_gwei, max_fee_per_gas_gwei = self.web3_utils.gas_eip_1559()

        tx["gas"] = int(self.web3_utils.w3.eth.estimate_gas(tx))
        tx["maxPriorityFeePerGas"] = self.web3_utils.w3.to_wei(max_priority_fee_per_gas_gwei, 'gwei')
        tx["maxFeePerGas"] = self.web3_utils.w3.to_wei(max_fee_per_gas_gwei, 'gwei')

        tx = self.web3_utils.w3.eth.account.sign_transaction(tx, self.web3_utils.acct.key.hex())
        transaction_hash = self.web3_utils.w3.eth.send_raw_transaction(tx.rawTransaction).hex()

        wait_tx = self.web3_utils.w3.eth.wait_for_transaction_receipt(transaction_hash)
        return wait_tx.status == 1, transaction_hash

    async def stake_on_zetachain(self):
        tx = {
            "from": self.web3_utils.acct.address,
            "to": self.web3_utils.w3.to_checksum_address("0x45334a5B0a01cE6C260f2B570EC941C680EA62c0"),
            "value": self.web3_utils.w3.to_wei(config.STAKE_ZETACHAIN['zeta_count'], 'ether'),
            "nonce": self.web3_utils.w3.eth.get_transaction_count(self.web3_utils.acct.address),
            # "gasPrice": self.web3_utils.w3.eth.gas_price,
            "chainId": 7000,
            "data": "0x5bcb2fc6",
        }

        max_priority_fee_per_gas_gwei, max_fee_per_gas_gwei = self.web3_utils.gas_eip_1559()

        tx["gas"] = int(self.web3_utils.w3.eth.estimate_gas(tx))
        tx["maxPriorityFeePerGas"] = self.web3_utils.w3.to_wei(max_priority_fee_per_gas_gwei, 'gwei')
        tx["maxFeePerGas"] = self.web3_utils.w3.to_wei(max_fee_per_gas_gwei, 'gwei')

        tx = self.web3_utils.w3.eth.account.sign_transaction(tx, self.web3_utils.acct.key.hex())
        transaction_hash = self.web3_utils.w3.eth.send_raw_transaction(tx.rawTransaction).hex()

        wait_tx = self.web3_utils.w3.eth.wait_for_transaction_receipt(transaction_hash)
        return wait_tx.status == 1, transaction_hash

    async def approve_zetaswap_wzeta(self):
        spender = "0xc6f7a7ba5388bfb5774bfaa87d350b7793fd9ef1"
        contract = "0x5f0b1a82749cb4e2278ec87f8bf6b618dc71a8bf"
        random_value = round(random.uniform(config.APPROVES['zetaswap_wzeta_approve'][0], config.APPROVES['zetaswap_wzeta_approve'][1]), 10)
        return self.web3_utils.approve(spender, random_value, abi.approve_abi, contract)

    async def allowance_zetaswap_wzeta(self):
        return self.web3_utils.allowance(spender="0xc6f7a7ba5388bfb5774bfaa87d350b7793fd9ef1", contract="0x5f0b1a82749cb4e2278ec87f8bf6b618dc71a8bf", abi=abi.approve_abi)

    async def zetaswap_wzeta_to_eth(self):
        headers = {"apiKey": config.NATIVE_API_KEY}
        random_value = round(random.uniform(config.ZETASWAP['wzeta_count'][0], config.ZETASWAP['wzeta_count'][1]), 5)

        params = {
            "chain": "zetachain",
            "token_in": "0x5F0b1a82749cb4E2278EC87F8BF6B618dC71a8bf",
            "token_out": "0xd97b1de3619ed2c6beb3860147e30ca8a7dc9891",
            "amount": random_value,
            "address": self.web3_utils.acct.address,
            "slippage": 2
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get('https://newapi.native.org/v1/firm-quote', params=params) as resp:
                resp_json = await resp.json()
                to = resp_json.get('txRequest').get('target')
                data = resp_json.get('txRequest').get('calldata')

        tx = {
            "from": self.web3_utils.acct.address,
            "to": self.web3_utils.w3.to_checksum_address(to),
            "value": 0,
            "nonce": self.web3_utils.w3.eth.get_transaction_count(self.web3_utils.acct.address),
            # "gasPrice": self.web3_utils.w3.eth.gas_price,
            "chainId": 7000,
            "data": data,
        }

        max_priority_fee_per_gas_gwei, max_fee_per_gas_gwei = self.web3_utils.gas_eip_1559()

        tx["gas"] = int(self.web3_utils.w3.eth.estimate_gas(tx))
        tx["maxPriorityFeePerGas"] = self.web3_utils.w3.to_wei(max_priority_fee_per_gas_gwei, 'gwei')
        tx["maxFeePerGas"] = self.web3_utils.w3.to_wei(max_fee_per_gas_gwei, 'gwei')

        tx = self.web3_utils.w3.eth.account.sign_transaction(tx, self.web3_utils.acct.key.hex())
        transaction_hash = self.web3_utils.w3.eth.send_raw_transaction(tx.rawTransaction).hex()

        wait_tx = self.web3_utils.w3.eth.wait_for_transaction_receipt(transaction_hash)
        return wait_tx.status == 1, transaction_hash

    async def check_ultiverse_badge(self):
        return self.web3_utils.balance_of_erc721(address=self.web3_utils.acct.address, contract_address="0xc2396941957dA28583935f6e076f1D7d10C9F2D5")

    async def min_ultiverse_badge(self):
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": "https://mission.ultiverse.io",
            "Referer": "https://mission.ultiverse.io/",
            "Ul-Auth-Api-Key": "bWlzc2lvbl9ydW5uZXJAZFd4MGFYWmxjbk5s",
            "User-Agent": UserAgent(os='windows').random
        }

        session = aiohttp.ClientSession(headers=headers, cookie_jar=aiohttp.CookieJar())

        json_data = {"address": self.web3_utils.acct.address, "feature": "assets-wallet-login", "chainId": 7000}
        resp = await session.post("https://account-api.ultiverse.io/api/user/signature", json=json_data, proxy=self.proxy)

        json_data = {
            "address": self.web3_utils.acct.address,
            "signature": self.web3_utils.get_signed_code((await resp.json()).get('data').get("message")),
            "chainId": 7000
        }
        resp = await session.post("https://account-api.ultiverse.io/api/wallets/signin", json=json_data, proxy=self.proxy)

        session.cookie_jar.update_cookies(resp.cookies)
        session.headers['Ul-Auth-Api-Key'] = (await resp.json()).get('data').get("access_token")
        session.headers['Referer'] = "https://mission.ultiverse.io/t/ZmluZHBhdGh8MTcwNjg2MDczMTkzMQ=="

        json_data = {
            "eventId": 21,
            "address": self.web3_utils.acct.address,
        }

        resp = await session.post("https://mission.ultiverse.io/api/tickets/mint", json=json_data, proxy=self.proxy)
        resp_json = (await resp.json()).get("data")
        await session.close()

        expire_at = resp_json.get("expireAt")
        token_id = resp_json.get("tokenId")
        event_id = resp_json.get("eventId")
        signature = resp_json.get("signature")

        contract = self.web3_utils.w3.eth.contract(address=resp_json.get('contract'), abi=abi.ultiverse_abi)

        tx = contract.functions.buy(expire_at, token_id, event_id, signature).build_transaction(
            {
                "from": self.web3_utils.acct.address,
                "value": self.web3_utils.w3.to_wei(config.POOLS['send_zeta'], "ether"),
                "nonce": self.web3_utils.w3.eth.get_transaction_count(self.web3_utils.acct.address),
                # "gasPrice": self.web3_utils.w3.eth.gas_price,
                "chainId": 7000,
            }
        )

        max_priority_fee_per_gas_gwei, max_fee_per_gas_gwei = self.web3_utils.gas_eip_1559()

        tx["gas"] = int(self.web3_utils.w3.eth.estimate_gas(tx))
        tx["maxPriorityFeePerGas"] = self.web3_utils.w3.to_wei(max_priority_fee_per_gas_gwei, 'gwei')
        tx["maxFeePerGas"] = self.web3_utils.w3.to_wei(max_fee_per_gas_gwei, 'gwei')

        tx = self.web3_utils.w3.eth.account.sign_transaction(tx, self.web3_utils.acct.key.hex())
        transaction_hash = self.web3_utils.w3.eth.send_raw_transaction(tx.rawTransaction).hex()
        wait_tx = self.web3_utils.w3.eth.wait_for_transaction_receipt(transaction_hash)

        return wait_tx.status == 1, transaction_hash
