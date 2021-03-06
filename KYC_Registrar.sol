pragma solidity ^0.5.4;

contract Account_Numbers{

    //events
    event RegistrationRequest(address indexed sender);
    event UnregistrationRequest(address indexed sender);
    event RegistrationConfirmed(address indexed sender);
    event UnregistrationConfirmed(address indexed sender);
    event RegistrationCanceled(address indexed sender);
    event UnregistrationCanceled(address indexed sender);

    //Approved
    mapping (string => address) person;
    mapping (address => bool) est;
    //Requested
    mapping (address => bool) RequestedA;
    mapping (address => bool) RequestedR;
    mapping (address => string) RequestedNum;

    address public owner;

    constructor () public {
        owner = msg.sender;
    }

    function GetOwner() public returns(address) {
        return owner;
    }

    function GetAddress(string memory _number) public returns(address){
        return person[_number];
    }

    function RedactOwner(address _person) public {
        require(msg.sender == owner);
        owner = _person;
    }

    //Get Info:
    function GetPersonInfoAR(address _person) public returns(bool){
        return RequestedA[_person];
    }

    function GetPersonInfoEST(address _person) public returns(bool){
        return est[_person];
    }

    function GetPersonInfoDR(address _person) public returns(bool){
        return RequestedR[_person];
    }

    //Requests:
    function RequestAddNumber(string memory _number) public {
        require(!RequestedA[msg.sender]);
        require(person[_number] == 0x0000000000000000000000000000000000000000);
        RequestedA[msg.sender] = true;
        RequestedNum[msg.sender] = _number;
        emit RegistrationRequest(msg.sender);
    }

    function RequestDelNumber() public {
        require(est[msg.sender]);
        require(!RequestedR[msg.sender]);
        RequestedR[msg.sender] = true;
        emit UnregistrationRequest(msg.sender);
    }

    function Cancel() public{
        require(RequestedA[msg.sender] || RequestedR[msg.sender]);
        if(RequestedA[msg.sender]){
            RequestedA[msg.sender] = false;
            emit RegistrationCanceled(msg.sender);
        }
        if(RequestedR[msg.sender]){
            RequestedR[msg.sender] = false;
            emit UnregistrationCanceled(msg.sender);
        }
    }


    //Confirm
    function Confirm(address _person) public {
        require(msg.sender == owner);
        require(RequestedA[_person] || RequestedR[_person]);
        if(RequestedA[_person]){
            est[_person] = true;
            person[RequestedNum[_person]] = _person;
            RequestedA[_person] = false;
            emit RegistrationConfirmed(_person);
        }
        if(RequestedR[_person]){
            est[_person] = false;
            person[RequestedNum[_person]] = 0x0000000000000000000000000000000000000000;
            RequestedR[_person] = false;
            emit UnregistrationConfirmed(_person);
        }
    }


}
