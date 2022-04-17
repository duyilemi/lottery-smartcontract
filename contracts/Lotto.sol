// SPDX-License-Identifier: MIT

pragma solidity ^0.6.6;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol";

contract Lotto is VRFConsumerBase, Ownable {
    address payable[] public players;
    address payable public winner;
    uint256 public entryFeeInUsd;
    uint256 public randomness;
    AggregatorV3Interface internal ethUsdPriceFeed;

    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    LOTTERY_STATE public lottery_state;
    uint256 public fee;
    bytes32 public keyhash;
    event RequestedRandomness(bytes32 requestId);


    constructor(address _priceFeedAddress, address _vrfCoordinator, address _link, uint256 _fee, bytes32 _keyhash) public VRFConsumerBase(_vrfCoordinator, _link) {
        entryFeeInUsd = 50 * 10**18;
        ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
        lottery_state = LOTTERY_STATE.CLOSED;
        fee = _fee;
        keyhash = _keyhash;
    }

    function enterLotto() public payable {
        require(lottery_state == LOTTERY_STATE.OPEN);
        require(msg.value >= getEntranceFee(), "Amount not enough");
        players.push(msg.sender);
    }

    function getEntranceFee() public view returns (uint256) {
        (,int256 price,,,) = ethUsdPriceFeed.latestRoundData();
        uint256 adjustedPrice = uint256(price) * 10**10;
        uint256 entryCost =  (entryFeeInUsd * 10**18) / adjustedPrice;
        return entryCost;

    }

    function startLotto() public onlyOwner {
        require(lottery_state == LOTTERY_STATE.CLOSED, "Can not start a new lotto at the moment");

        lottery_state = LOTTERY_STATE.OPEN;
    }


    function endLotto() public {
        // uint256(keccack256(abi.encodePacked(nonce, msg.sender, block.difficulty, block.timestamp);)) % players.length;

        lottery_state = LOTTERY_STATE.CALCULATING_WINNER;
        // call requestRandomness
        bytes32 requestId = requestRandomness(keyhash, fee);
        emit RequestedRandomness(requestId);
    }

    function fulfillRandomness(bytes32 _requestId, uint256 _randomness) internal override {
        require(lottery_state == LOTTERY_STATE.CALCULATING_WINNER, "Wait for the result");
        require(_randomness > 0, "random not found");
        uint256 winnerIndex = _randomness % players.length;
        winner = players[winnerIndex];
        winner.transfer(address(this).balance);
        players = new address payable[](0);
        lottery_state = LOTTERY_STATE.CLOSED;
        randomness = _randomness;
    }

}