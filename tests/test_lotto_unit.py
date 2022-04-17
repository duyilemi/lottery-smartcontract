from scripts.helper_script import (
    LOCAL_BLOCKCHAIN_ENVS,
    get_account,
    fund_with_link,
    get_contract,
)
from brownie import Lotto, accounts, config, network, exceptions
from scripts.deploy_lotto import deploy_lotto
from web3 import Web3
import pytest


def test_get_entrance_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVS:
        pytest.skip()
    # Arrange
    lotto = deploy_lotto()
    # Act
    # 2,000 eth / usd
    # usdEntryFee is 50
    # 2000/1 == 50/x == 0.025
    expected_entrance_fee = Web3.toWei(0.025, "ether")
    entrance_fee = lotto.getEntranceFee()
    # Assert
    assert expected_entrance_fee == entrance_fee


def test_cant_enter_unless_started():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVS:
        pytest.skip()
    lotto = deploy_lotto()
    # Act / Assert
    with pytest.raises(exceptions.VirtualMachineError):
        lotto.enterLotto({"from": get_account(), "value": lotto.getEntranceFee()})


def test_can_start_and_enter_lottery():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVS:
        pytest.skip()
    lotto = deploy_lotto()
    account = get_account()
    lotto.startLotto({"from": account})
    # Act
    lotto.enterLotto({"from": account, "value": lotto.getEntranceFee()})
    # Assert
    assert lotto.players(0) == account


def test_can_end_lotto():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVS:
        pytest.skip()
    lotto = deploy_lotto()
    account = get_account()
    lotto.startLotto({"from": account})
    lotto.enterLotto({"from": account, "value": lotto.getEntranceFee()})
    fund_with_link(lotto)
    lotto.endLotto({"from": account})
    assert lotto.lottery_state() == 2


def test_can_pick_winner_correctly():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVS:
        pytest.skip()
    lotto = deploy_lotto()
    account = get_account()
    lotto.startLotto({"from": account})
    lotto.enterLotto({"from": account, "value": lotto.getEntranceFee()})
    lotto.enterLotto({"from": get_account(index=1), "value": lotto.getEntranceFee()})
    lotto.enterLotto({"from": get_account(index=2), "value": lotto.getEntranceFee()})
    fund_with_link(lotto)
    starting_balance_of_account = account.balance()
    balance_of_lotto = lotto.balance()
    transaction = lotto.endLotto({"from": account})
    request_id = transaction.events["RequestedRandomness"]["requestId"]
    STATIC_RNG = 777
    # pretending that we are the vrf_coordinator and call the callBackWithRandomness as if we are a chainlink node ...
    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, STATIC_RNG, lotto.address, {"from": account}
    )
    # 777 % 3 = 0
    assert lotto.winner() == account
    assert lotto.balance() == 0
    assert account.balance() == starting_balance_of_account + balance_of_lotto 