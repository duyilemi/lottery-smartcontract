from brownie import Lotto, network, config
from scripts.helper_script import get_account, get_contract, fund_with_link
import time

def deploy_lotto():
    account = get_account()
    lotto = Lotto.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print("Lotto Has Been Deployed")
    return lotto

def start_lotto():
    account = get_account()
    lotto = Lotto[-1]
    transc = lotto.startLotto({"from": account})
    transc.wait(1)
    print("The lotto has started ...")

def enter_lotto():
    account = get_account()
    lotto = Lotto[-1]
    value = lotto.getEntranceFee() +10000
    transc = lotto.enterLotto({"from": account, "value": value})
    transc.wait(1)
    print("You entered the lotto ...")

def end_lotto():
    account = get_account()
    lotto = Lotto[-1]
    # fund the contract...
    # then end the lotto...
    transc = fund_with_link(lotto.address)
    transc.wait(1)
    ending_transc = lotto.endLotto({"from": account})
    ending_transc.wait(1)
    time.sleep(60)
    print(f"{lotto.winner()} is the new winner")

    


def main():
    deploy_lotto()
    start_lotto()
    enter_lotto()
    end_lotto()