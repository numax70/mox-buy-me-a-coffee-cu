from eth_utils import to_wei
import boa

from tests.conftest import SEND_VALUE
RANDOM_USER = boa.env.generate_address("non-owner")

def test_price_feed_is_correct(coffee, eth_usd):
    assert coffee.PRICE_FEED() == eth_usd.address

def test_starting_value(coffee, account):
    assert coffee.MINIMUM_USD() == to_wei(5, "ether") 
    assert coffee.OWNER() ==  account.address  

def test_fund_fails_without_enough_eth(coffee):
    with boa.reverts("You must spend more ETH!"):
        coffee.fund()    

def test_fund_with_money(coffee, account):
    boa.env.set_balance(account.address, SEND_VALUE)
    coffee.fund(value = SEND_VALUE)
    funder = coffee.funders(0)
    assert funder == account.address
    assert coffee.funder_to_amount_funded(funder) == SEND_VALUE


def test_non_owner_cannot_withdraw(coffee_funded, account):
  with boa.env.prank(RANDOM_USER):
    with boa.reverts():
        coffee_funded.withdraw()   

def test_owner_can_withdraw(coffee_funded, account):
    with boa.env.prank(coffee_funded.OWNER()):
        coffee_funded.withdraw()
    assert boa.env.get_balance(coffee_funded.address) == 0    

def test_get_rate(coffee):
    assert coffee. get_eth_to_usd_rate(SEND_VALUE) > 0   


# Workshop
def test_funders_creation_and_withdraw(coffee):
    for _ in range(10):
        new_funders = boa.env.generate_address("non-owner")
        boa.env.set_balance(new_funders, SEND_VALUE)
        with boa.env.prank(new_funders):
            coffee.fund(value = SEND_VALUE)
    owner_balance = boa.env.get_balance(coffee.OWNER())
    contract_balance = boa.env.get_balance(coffee.address)
    total_owner_balance = owner_balance + contract_balance
    with boa.env.prank(coffee.OWNER()):
        coffee.withdraw()
    assert boa.env.get_balance(coffee.address) == 0
    assert boa.env.get_balance(coffee.OWNER()) == total_owner_balance   


def test_funders_clear_eth_after_withdraw(coffee):
    funders = []
    for _ in range(10):
        funders_address = boa.env.generate_address()
        boa.env.set_balance(funders_address, SEND_VALUE)
        with boa.env.prank(funders_address):
            coffee.fund(value = SEND_VALUE)
            funders.append(funders_address)
        
    with boa.env.prank(coffee.OWNER()):
        coffee.withdraw()
    assert boa.env.get_balance(coffee.address) == 0
    assert coffee.funder_to_amount_funded(funders[0]) == 0
    for i in funders:
        assert coffee.funder_to_amount_funded(i) == 0