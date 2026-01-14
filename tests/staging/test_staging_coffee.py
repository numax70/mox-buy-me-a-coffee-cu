import pytest
from script.deploy import deploy_coffee
from tests.conftest import SEND_VALUE
from moccasin.config import get_active_network
import boa
import pytest


@pytest.mark.staging
@pytest.mark.local
@pytest.mark.ignore_isolation


def test_can_fund_and_withdraw_live():
    active_network = get_active_network()
    price_feed = active_network.manifest_named("price_feed")
    coffee = deploy_coffee(price_feed)
    balance = boa.env.get_balance(boa.env.eoa)
    if balance < SEND_VALUE:
         pytest.skip("EOA non ha sufficienti ETH per eseguire il test in staging/fork")
    coffee.fund(value = SEND_VALUE)
    amount_funded = coffee.funder_to_amount_funded(boa.env.eoa)
    assert amount_funded > 0
    with boa.env.prank(coffee.OWNER()):
        coffee.withdraw()
    assert boa.env.get_balance(coffee.address) == 0
       
           