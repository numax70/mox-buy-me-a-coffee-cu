# pragma version ^0.4.0
"""
@license MIT 
@title Buy Me A Coffee!
@author You!
@notice This contract is for creating a sample funding contract
"""
#interface AggregatorV3Interface:
    #def decimals() -> uint8: view
    #def description() -> String[1000]: view
    #def version() -> uint256: view
    #def latestAnswer() -> int256: view
from interfaces import AggregatorV3Interface
import get_price_module

# Constants & Immutables
MINIMUM_USD: public(constant(uint256)) = as_wei_value(5, "ether") # impostiamo un minimo importo per finanziare il contratto
PRICE_FEED: public(immutable(AggregatorV3Interface)) # 0x694AA1769357215DE4FAC081bf1f309aDC325306 sepolia indirizzo price_feed chainlink
OWNER: public(immutable(address)) # memorizzeremo l'indirizzo del proprietario del contratto
# PRECISION: constant(uint256) = 1 * (10 ** 18) # spostato sul modulo

# Storage
funders: public(DynArray[address, 1000]) # quì memorizziamo gli indirizzi dei finanziatori del contratto
funder_to_amount_funded: public(HashMap[address, uint256]) # quì associamo gli indirizzi agli importi finanziati

# With constants: 262,853
@deploy
def __init__(price_feed: address): # in fase di deploy inseriamo l'indirizzo feed
    PRICE_FEED = AggregatorV3Interface(price_feed) # lo convertiamo in interfaccia aggregator
    OWNER = msg.sender # impostiamo il proprietario con lindirizzo del finanziatore

@external
@payable
def fund(): # funzione fund esterna che chiama una interna
    self._fund()

@internal
@payable
def _fund(): # funzione interna fund
    """Allows users to send $ to this contract
    Have a minimum $ amount to send

    How do we convert the ETH amount to dollars amount?
    """
    #usd_value_of_eth: uint256 = self._get_eth_to_usd_rate(msg.value)
    usd_value_of_eth: uint256 = get_price_module._get_eth_to_usd_rate(PRICE_FEED, msg.value)
    # usa il modulo get_price_module dal quale chiamo la funzione get_eth_to_usd_rate passandogli
    # il price_feed e l'importo  
    assert usd_value_of_eth >= MINIMUM_USD, "You must spend more ETH!" #controlliamo de rispettiamo i termini, gli importi minimi
    self.funders.append(msg.sender) # se tutto va bene conseerviamo nell'array l'indirizzo del funder
    self.funder_to_amount_funded[msg.sender] += msg.value # associamo all'indirizzo del funder, l'importo finanziato


@external
def withdraw(): # funzione di preleievo
    """Take the money out of the contract, that people sent via the fund function.

    How do we make sure only we can pull the money out?
    """
    assert msg.sender == OWNER, "Not the contract owner!" # controlliamo se chi richiede sia effettivamente il proprietario
    raw_call(OWNER, b"", value = self.balance) #  # inviamo tutto al proprietario
    # send(OWNER, self.balance)  # inviamo tutto il balance, al proprietario (funzione deprecata perchè non sicura)
    # resetting
    for funder: address in self.funders: # resettiamo gli stati (array e hashmap)
        self.funder_to_amount_funded[funder] = 0
    self.funders = []

#@internal
#@view
#def _get_eth_to_usd_rate(eth_amount: uint256) -> uint256:
    #"""
    #Chris sent us 0.01 ETH for us to buy a coffee
    #Is that more or less than $5?
    #"""
    #price: int256 = staticcall PRICE_FEED.latestAnswer() 
    #eth_price: uint256 = (convert(price, uint256)) * (10**10)
    #eth_amount_in_usd: uint256 = (eth_price * eth_amount) // PRECISION
    #return eth_amount_in_usd # 18 0's, 18 decimal places

@external 
@view 
def get_eth_to_usd_rate(eth_amount: uint256) -> uint256: #questa funzione è inutilizzata e serve sostanzialmente
# a chiunque volesse convertire un importo in eth in usd conoscendo il price_feed e l'importo, senza però utilizzare eth
    #return self._get_eth_to_usd_rate(eth_amount)
    return get_price_module._get_eth_to_usd_rate(PRICE_FEED, eth_amount)

@external 
@payable 
def __default__(): # Permette di finanziare il contratto inviando ETH direttamente
    self._fund()   # Se qualcuno manda ETH senza specificare funzione → fund() viene eseguita
   

