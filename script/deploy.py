from moccasin.config import get_active_network
from moccasin.config import VyperContract
from src import buy_me_a_coffee
from script.deploy_mocks import deploy_feed

def deploy_coffee(price_feed: VyperContract)-> VyperContract:
    coffee: VyperContract = buy_me_a_coffee.deploy(price_feed)
    active_network = get_active_network()

    if active_network.has_explorer() and active_network.is_local_or_forked_network() is False:
        result = active_network.moccasin_verify(coffee)
        result.wait_for_verification()
    
    return coffee
     

def moccasin_main():
    active_network = get_active_network()
    price_feed: VyperContract = active_network.manifest_named("price_feed") 
    print(f"On network at {active_network.name}, using price feed {price_feed.address}")
    return deploy_coffee(price_feed)

    