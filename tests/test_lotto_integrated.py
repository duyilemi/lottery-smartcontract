from brownie import network
import pytest
from scripts.helper_script import (
    LOCAL_BLOCKCHAIN_ENVS,
    get_account,
    fund_with_link,
)
from scripts.deploy_lotto import deploy_lotto
import time


def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVS:
        pytest.skip()
    lotto = deploy_lotto()
    account = get_account()
    lotto.startLotto({"from": account})
    lotto.enterLotto({"from": account, "value": lotto.getEntranceFee()})
    lotto.enterLotto({"from": account, "value": lotto.getEntranceFee()})
    fund_with_link(lotto)
    lotto.endLotto({"from": account})
    # Here, we are not the chainlink node because we are on a  real network so we are going to wait for the actual chainlink node to respond
    time.sleep(180)
    assert lotto.winner() == account
    assert lotto.balance() == 0