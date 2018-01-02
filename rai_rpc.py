import requests
import json
from configparser import ConfigParser
from pprint import pprint

import ipdb as pdb

# TODO: Error handling

class Rai_node:
    def __init__(self, uri, password=''):
        self.uri = uri
        self.password = password

    def _bool_to_str(self, boolean):
        ''' transforms a boolean into a true/false string '''
        return "true" if boolean else "false"

    def _to_list(self, x):
        ''' Converts x into a list if it isn't already '''
        if isinstance(x, str):
            x = [x,]
        elif isinstance(x, tuple):
            x = list(x)
        return x


    def send_rpc_request(self, data):
        '''
        Sends off POST request to rai_node, returns dict result.
        If bad response, returns None
        '''
        response = requests.post(self.uri, data=data)
        if not response.ok:
            return None
        resp_dict = json.loads(response.text)
        return resp_dict

    def account_balance(self, address):
        '''
        Get number of blocks for a specific account

        Key            Value
        'balance'      account balance in raw
        'pending'      not pocketed in raw
        '''
        request='''{
        "action":"account_balance",
        "account":"%s"
        }''' % address
        return self.send_rpc_request(request)

    def account_block_count(self, account):
        '''
        Get number of blocks for a specific account

        returns int
        '''
        request='''{
        "action":"account_block_count",
        "account":"%s"
        }''' % account
        res = self.send_rpc_request(request)
        return res['block_count']

    def account_information(self, account):
        '''
        Returns:

        Key                     Description
        'frontier'              head block hash
        'open_block'            open block hash
        'representative_block'  change rep block hash
        'balance'               account balance in raw
        'pending'               not pocketed account balance (raw)
        'modified_timestamp'    ?
        'block_count'           number of blocks in accountchain
        'representative'        xrb_ address of representative
        'weight'                voting weight in raw
        '''
        request='''{
        "action_info":"account_info",
        "representative":"true",
        "weight":"true",
        "pending":"true",
        "account":"%s"
        }''' % account
        res = self.send_rpc_request(request)
        return res['block_count']

    def account_create(self, wallet, work=True):
        '''
        Creates a new account, insert next deterministic key in wallet.

        Returns an xrb_ address (string)
        '''
        work_str = _bool_to_str(work)
        request='''{
        "action":"account_create",
        "wallet":"%s"
        }''' % wallet
        res = self.send_rpc_request(request)
        return res['account']

    def account_get(self, public_key):
        '''
        Get account number for the public key

        Returns an xrb_ address (string)
        '''
        request='''{
        "action":"account_get",
        "key":"%s"
        }''' % public_key
        res = self.send_rpc_request(request)
        return res['account']

    def account_history(self, account, count=1):
        '''
        Reports send/receive information for a account

        Example response (count=1):
        [{ "hash": "000D1BAEC8EC208142C99059B393051BAC8380F9B5A2E6B2489A277D81789F3F",
           "type": "receive",
           "account": "xrb_3e3j5tkog48pnny9dmfzj1r16pg8t1e76dz5tmac6iq689wyjfpi00000000",
           "amount": "100000000000000000000000000000000" },]
        '''
        request='''{
        "action":"account_history",
        "account":"%s",
        "count":"%d"
        }''' % (account, count)
        res = self.send_rpc_request(request)
        return res['history']

    def account_list(self, wallet):
        '''
        Lists all the accounts inside wallet

        Returns list of xrb_ addresses
        '''
        request='''{
        "action":"account_list",
        "wallet":"%s"
        }''' % wallet
        res = self.send_rpc_request(request)
        return res['accounts']

    def account_move(self, src_wallet, dst_wallet, accounts):
        '''
        Moves account(s) from source to wallet

        Lists all the accounts inside wallet

        Returns integer of number of moved addresses
        '''

        accounts = self._to_list(accounts)

        request='''{
        "action":"account_move",
        "wallet":"%s",
        "source":"%s",
        "accounts":"%s"
        }''' % (dst_wallet, src_wallet, accounts)
        res = self.send_rpc_request(request)
        return int(res['moved'])

    def account_remove(self, wallet, account):
        '''
        Remove account from wallet.

        Returns integer number of removed addresses.
        '''
        request='''{
        "action":"account_remove",
        "wallet":"%s",
        "account":"%s"
        }''' % (wallet, account)
        res = self.send_rpc_request(request)
        return int(res['removed'])

    def account_representative(self, account):
        '''
        Returns the representative for account
        Returns xrb_ address
        '''
        request='''{
        "action":"account_representative",
        "account":"%s"
        }''' % account
        res = self.send_rpc_request(request)
        return res['representative']

    def set_representative(self, wallet, account, representative):
        '''
        Sets the representative of account in wallet to xrb_ representative
        address

        Returns change block hash.
        '''
        request='''{
        "action":"account_representative",
        "wallet":"%s",
        "account":"%s",
        "representative":"%s"
        }''' % (wallet, account, representative)
        res = self.send_rpc_request(request)
        return res['block']

    def account_weight(self, account):
        '''
        Gets the voting weight of an account
        '''
        request='''{
        "action":"account_weight",
        "account":"%s"
        }''' % account
        res = self.send_rpc_request(request)
        return int(res['weight'])

    def accounts_balances(self, accounts):
        '''
        Returns how many RAW is owned and how many have
        not yet been received by accounts list.

        Returns a dict of dicts where the first key is
        the xrb_ address, second key is:

        Key            Value
        'balance'      account balance in raw
        'pending'      not pocketed in raw
        '''
        accounts = self.to_list(accounts)
        request='''{
        "action":"accounts_balances",
        "accounts":"%s"
        }''' % accounts
        res = self.send_rpc_request(request)
        return res['balances']

    def accounts_create(self, wallet, count=1, work=True):
        '''
        Creates new accounts, insert next deterministic keys in wallet up to count

        Returns list of xrb_ addresses
        '''
        work_str =  self._bool_to_str(work)
        request='''{
        "action":"accounts_create",
        "wallet":"%s",
        "count":"%s",
        "work":"work_str"
        }''' % (wallet, count, work_str)
        res = self.send_rpc_request(request)
        return res['accounts']

    def accounts_frontiers(self, accounts):
        '''
        Returns a list of pairs of account and block hash representing
        the head block for accounts list.

        Returns a dict where the key is the xrb_ address and
        the value is the head block hash.
        '''
        accounts = self._to_list(accounts)
        request='''{
        "action":"accounts_frontiers",
        "accounts":"%s"
        }''' % accounts
        res = self.send_rpc_request(request)
        return res['frontiers']

    def accounts_pending(self, accounts, count=1, threshold=0):
        '''
        Gets a list of block hashes for each account in accounts.

        Only returns pending amounts greater than threshold (raw).

        Returns a dict of dicts where the first key is the xrb_ address
        and the second dict is:

        Key            Value
        'amount'       transaction amount in raw
        'source'       source xrb_ address
        '''
        accounts = self._to_list(accounts)
        request='''{
        "action":"accounts_pending",
        "accounts":"%s",
        "count":"%d",
        "threshold":"%d",
        "source":"true"
        }''' % (accounts, count, threshold)
        res = self.send_rpc_request(request)
        return res['blocks']

    def available_supply(self):
        '''
        Returns how many rai are in the public supply
        '''
        request='''{
        "action":"accounts_pending"
        }'''
        res = self.send_rpc_request(request)
        return int(res['available'])

    def block(self, hash):
        '''
        Retrieves a JSON (dict) representation of a block

        The dict has the following keys:
        Key               Value
        'type'            'open'/'send'/'receive'/'change'
        'account'         'xrb_...'
        'representative'  'xrb_...'
        'work'            '00000...'
        'signature'       '00000...'
        '''
        request='''{
        "action":"block",
        "hash":"%s"
        }''' % hash
        res = self.send_rpc_request(request)
        return res['contents']

    def blocks(self, hashes):
        '''
        Retrieves a dict of JSON (dict) representation of a block

        The first dict's key is the xrb_ address

        The dict has the following keys:
        Key               Value
        'type'            'open'/'send'/'receive'/'change'
        'account'         'xrb_...'
        'representative'  'xrb_...'
        'work'            '00000...'
        'signature'       '00000...'
        '''
        hashes = self._to_list(hashes)
        request='''{
        "action":"blocks",
        "hashes":"%s"
        }''' % hashes
        res = self.send_rpc_request(request)
        return res['blocks']

    def blocks_info(self, hashes):
        '''
        A little more info than blocks
        '''
        hashes = self._to_list(hashes)
        request='''{
        "action":"blocks_info",
        "hashes":"%s"
        }''' % hashes
        res = self.send_rpc_request(request)
        return res['blocks']

    def block_account(self, hash):
        '''
        Returns the account containing the block hash
        '''
        request='''{
        "action":"block_account",
        "hash":"%s"
        }''' % hash
        res = self.send_rpc_request(request)
        return res['account']

    def block_count(self):
        '''
        Reports the number of blocks in ledger
        The dict has the following keys:
        Key               Value
        'count'           '1000'
        'unchecked'       '10'
        '''
        request='''{
        "action":"block_count"
        }'''
        res = self.send_rpc_request(request)
        return res

    def block_count_type(self):
        '''
        Reports the quantity of the different types of blocks in ledger

        The dict has the following keys:
        Key              Value
        'send'           '1000'
        'receive'        '900'
        'open'           '100'
        'change'         '50'
        '''
        request='''{
        "action":"block_count_type"
        }'''
        res = self.send_rpc_request(request)
        return res

    def bootstrap(self, ip, port):
        '''
        Initialize bootstrap to specific IP address and port

        Also see: bootstrap_any()
        '''
        port = str(port)
        request='''{
        "action":"bootstrap",
        "address":"%s",
        "port":"%s"
        }''' % (ip, port)
        res = self.send_rpc_request(request)
        return res['success']

    def bootstrap_any(self):
        '''
        '''
        request='''{
        "action":"bootstrap_any"
        }'''
        res = self.send_rpc_request(request)
        return res['success']

    def chain(self, block, count=1):
        '''
        Returns a list of block hashes in the account chain starting
        at block up to count.
        '''
        request='''{
        "action":"chain",
        "block":"%s",
        "count":"%d"
        }''' % (block, count)
        res = self.send_rpc_request(request)
        return res['blocks']

    def delegators(self, account):
        '''
        Returns a list of pairs of delegator names given account a
        representative and its balance.
        '''
        request='''{
        "action":"delegators",
        "account":"%s"
        }''' % account
        res = self.send_rpc_request(request)
        return res['delegators']

    def delegators_count(self, account):
        '''
        Gets the number of delegators for an account
        '''
        request='''{
        "action":"delegators_count",
        "account":"%s"
        }''' % account
        res = self.send_rpc_request(request)
        return int(res['count'])

    def deterministic_key(self, seed, index=0):
        '''
        Derive deterministic keypair from seed based on index

        Key              Value
        'private'        '9F0E...'
        'public'         'c008...'
        'account'        'xrb_3i...'
        '''
        request='''{
        "action":"deterministic_key",
        "seed":"%s",
        "index":"%d"
        }''' % (seed, index)
        res = self.send_rpc_request(request)
        return res['count']

    def frontiers(self, account, count=1):
        '''
        Returns a list of pairs of account and block hash representing
        the head block starting at account up to count
        '''
        request='''{
        "action":"frontiers",
        "account":"%s",
        "count":"%d"
        }''' % (account, count)
        res = self.send_rpc_request(request)
        return res['frontiers'][account]

    def frontier_count(self):
        '''
        Reports the number of accounts in the ledger
        '''
        request='''{
        "action":"frontier_count"
        }'''
        res = self.send_rpc_request(request)
        return int(res['count'])

    def history(self, hash, count=1):
        '''
        Reports send/receive information for a chain of blocks
        '''
        request='''{
        "action":"history",
        "hash":"%s",
        "count":"%d"
        }''' % (hash, count)
        res = self.send_rpc_request(request)
        return res['history']

    def mrai_from_raw(self, amount):
        '''
        Divide a raw amount down by the Mrai ratio.
        '''
        amount = int(amount)
        request='''{
        "action":"mrai_from_raw",
        "amount":"%d"
        }''' % amount
        res = self.send_rpc_request(request)
        return float(res['amount'])

    def mrai_to_raw(self, amount):
        '''
        Multiply an Mrai amount by the Mrai ratio.
        '''
        amount = float(amount)
        request='''{
        "action":"mrai_to_raw",
        "amount":"%f"
        }''' % amount
        res = self.send_rpc_request(request)
        return float(res['amount'])

    def krai_from_raw(self, amount):
        '''
        Divide a raw amount down by the krai ratio.
        '''
        amount = int(amount)
        request='''{
        "action":"krai_from_raw",
        "amount":"%d"
        }''' % amount
        res = self.send_rpc_request(request)
        return float(res['amount'])

    def krai_to_raw(self, amount):
        '''
        Multiply an krai amount by the krai ratio.
        '''
        amount = float(amount)
        request='''{
        "action":"krai_to_raw",
        "amount":"%f"
        }''' % amount
        res = self.send_rpc_request(request)
        return float(res['amount'])

    def rai_from_raw(self, amount):
        '''
        Divide a raw amount down by the rai ratio.
        '''
        amount = int(amount)
        request='''{
        "action":"rai_from_raw",
        "amount":"%d",
        }''' % amount
        res = self.send_rpc_request(request)
        return float(res['amount'])

    def rai_to_raw(self, amount):
        '''
        Multiply a rai amount by the rai ratio.
        '''
        amount = float(amount)
        request='''{
        "action":"rai_to_raw",
        "amount":"%f"
        }''' % amount
        res = self.send_rpc_request(request)
        return float(res['amount'])

    def keepalive(self, address, port):
        '''
        Tells the node to send a keepalive packet to address:port
        '''
        address = str(address)
        port = str(port)

        request='''{
        "action":"keepalive",
        "address":"%s",
        "port":"%s"
        }''' % (address, port)
        self.send_rpc_request(request)
        return None

    def key_create(self, ):
        '''
        Generates a adhoc random keypair
        '''
        request='''{
        "action":"key_create",
        }'''
        res = self.send_rpc_request(request)
        return res

    def ledger(self, account, count=1):
        '''
        Returns frontier, open block, change representative block,
        balance, last modified timestamp from local database & block
        count starting at account up to count.
        '''
        request='''{
        "action":"ledger",
        "account":"%s",
        "count":"%d",
        "representative":"true",
        "weight":"true",
        "pending":"true"
        }''' % (account, count)
        res = self.send_rpc_request(request)
        return res['accounts']

    def block_create(self, contents):
        '''
        This function is a doozy
        Offline Signing
        Takes in a dictionary contents to be parsed into a block
        Creates a json representations of new block based on input data &
        signed with private key or account in wallet*.
        '''
        # TODO: This is all just placeholders
        block_type = contents['type'].lower()
        if block_type == 'open':
            request='''{
            "action":"block_create",
            "type":"open",
            "key":"%s",
            "account":"%s",
            "representative":"%s",
            "source":"%s"
            }''' % (
                    contents['key'],
                    contents['account'],
                    contents['representative'],
                    contents['source'])
        elif block_type == 'change':
            request='''{
            "action":"block_create",
            "type":"change",
            "wallet":"%s",
            "account":"%s",
            "representative":"%s",
            "previous":"%s"
            }''' % (
                    contents['wallet'],
                    contents['account'],
                    contents['representative'],
                    contents['previous'])
        elif block_type == 'send':
            request='''{
            "action":"block_create",
            "type":"send",
            "wallet":"%s",
            "account":"%s",
            "destination":"%s",
            "balance":"%s",
            "amount":"%d",
            "previous":"%s"
            }''' % (
                    contents['wallet'],
                    contents['account'],
                    contents['destination'],
                    contents['balance'],
                    contents['amount'],
                    contents['previous'])
        elif block_type == 'receive':
            pass
        else:
            pass #error
        res = self.send_rpc_request(request)
        return res

    def payment_begin(self, wallet):
        '''
        Begin a new payment session. Searches wallet for an account
        that's marked as available and has a 0 balance. If one is found,
        the account number is returned and is marked as unavailable.
        If no account is found, a new account is created, placed in the wallet,
        and returned.
        '''
        request='''{
        "action":"payment_begin",
        "wallet":"%s",
        }''' % wallet
        res = self.send_rpc_request(request)
        return res['account']

    def payment_init(self, wallet):
        '''
        Marks all accounts in wallet as available for being used as a payment session.
        '''
        request='''{
        "action":"payment_init",
        "wallet":"%s",
        }''' % wallet
        res = self.send_rpc_request(request)
        return res['status']

    def payment_end(self, account, wallet):
        '''
        End a payment session. Marks the account as available for use
        in a payment session. Request:
        '''
        request='''{
        "action":"payment_end",
        "account":"%s",
        "wallet":"%s"
        }''' % (account, wallet)
        self.send_rpc_request(request)
        return None

    def payment_wait(self, account, amount, timeout=1000):
        '''
        End a payment session. Marks the account as available for use
        in a payment session. Request:
        '''
        request='''{
        "action":"payment_wait",
        "account":"%s",
        "amount":"%d",
        "timeout":"%d"
        }''' % (account, amount, timeout)
        res = self.send_rpc_request(request)
        return res['status']

    # pickup here!
    def meow():
        '''
        Gets the sync status of the node.

        Key            Value
        'count'        int
        'unchecked'    int
        '''

    def get_work_generate(hash):
        '''
        Computes the PoW for a given hash

        Key            Value
        'work'         str(16)
        '''
        request='''{
        "action":"work_generate",
        "hash":"%s"
        }''' % hash

        return send_rpc_request(request)


    def send(wallet, source, destination, amount):
        request='''{
        "action":"send",
        "wallet":"%s",
        "source":"%s",
        "destination":"%s",
        "amount":"%s"
        }''' % (wallet, source, destination, amount)

        return send_rpc_request(request)

    def receive(self, wallet, account, block):
        request='''{
        "action":"receive",
        "wallet":"%s",
        "account":"%s",
        "block":"%s"
        }''' % (wallet, account, block)

        res = self.send_rpc_request(request)
        return res['block']

    def pending(self, account, count=1):
        request='''{
        "action":"pending",
        "account":"%s",
        "count":"%d"
        }''' % (account, count)

        res = self.send_rpc_request(request)
        if count==1:
            return res['blocks'][0]
        else:
            return res['blocks']

    def process(self, block):
        if isinstance(block, str):
            # convert string block to a dictionary
            block = json.loads(block)
        block = json.dumps(block)
        block = block.replace('"','\\"')
        request='''{
        "action":"process",
        "block":"%s"
        }''' % block
        res = self.send_rpc_request(request)
        return res['hash']

    def republish(self, hash):
        request='''{
        "action":"republish",
        "hash":"%s"
        }''' % hash
        res = self.send_rpc_request(request)
        return res['blocks']

if __name__=="__main__":
    '''
    Demos these rpc commands
    '''
    demo_address = 0

    # Get the Block Count
    print("Get Block Count")
    pprint(get_block_count())
