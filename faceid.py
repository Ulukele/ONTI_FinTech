#!/usr/bin/env python
import sys
import json
from eth_account import Account
from web3 import Web3, HTTPProvider
import sha3
import cognitive_face as cf
import os
import requests
from face_lib import add_new_person, checker, recognize, delete_person, list_of_users, train, update_user_data, identification, checker_for_find
import random
import DI_Transactions as dit

def GetPerson():
    try:
        with open('person.json') as file:
            infor = json.load(file)
            return (infor['id'])
    except:
        return None

def KeyCreate(ident, pin):
    ident = (ident[:8] + ident[9:13] + ident[14:18] + ident[19:23] + ident[24:])

    pin = str(pin)
    pin = [('0'+pin[0]), ('0'+pin[1]), ('0'+pin[2]), ('0'+pin[3])]

    #Calculate privateKey
    data = b''
    for i in range(4):
        data = sha3.keccak_256(data).hexdigest()
        data = data + ident + pin[i]
        data = bytes.fromhex(data)
    data = sha3.keccak_256(data).hexdigest()
    privateKey = data
    return privateKey

def GenerateKey(PINcode):
    personInfo = GetPerson()
    if personInfo == None:
        return None
    if len(str(PINcode)) != 4:
        print("invalid key!")
        sys.exit()
    key = KeyCreate(personInfo, PINcode)
    return key

def PrintBalance(privateKey):
    adress = dit.get_adress(privateKey)
    balance = [0, 0]
    balance[0], balance[1] = dit.balance_all(web3.eth.getBalance(adress.address))
    if balance[0] == '':
        balance[0] = 0
    print("Your balance is {} {}".format(balance[0], balance[1]))

def checkNumber(phoneNum):
    phoneNum = str(phoneNum)
    if len(phoneNum) == 12:
        if(phoneNum[0] == '+' and len(phoneNum) == 12):
            for i in range(1, 12):
                if(phoneNum[i] < '0' or phoneNum[i] > '9'):
                    return False
            return True
        else:
            return False
    else:
        return False

def AddNumberRequest(PINcode, Key, PhoneNum):
    (Caddress, abiKYC, byteKYC) = dit.contract_info("KYC_Registrar")
    if Caddress == None:
        return {'status': -2}
    person = dit.get_adress(Key)
    try:
        contract_by_address =  web3.eth.contract(address = Caddress, abi = abiKYC, bytecode=byteKYC)
        status = contract_by_address.functions.GetPersonInfoAR(person.address).call()
    except:
        return {'status': -3}


    if status:
        return {'status': -1}

    tx_wo_sign = contract_by_address.functions.RequestAddNumber(PhoneNum).buildTransaction({
        'from': person.address,
        'nonce': web3.eth.getTransactionCount(person.address),
        'gasPrice': dit.get_gas_price()
    })
    try:
        signed_tx = person.signTransaction(tx_wo_sign)
        txId = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
    except:
        return {'status': -4}
    TX = web3.eth.waitForTransactionReceipt(txId)
    return TX

def DelNumberRequest(PINcode, Key):
    (Caddress, abiKYC, byteKYC) = dit.contract_info("KYC_Registrar")
    if Caddress == None:
        return {'status': -2}
    person = dit.get_adress(Key)
    try:
        contract_by_address =  web3.eth.contract(address = Caddress, abi = abiKYC, bytecode=byteKYC)
        status = contract_by_address.functions.GetPersonInfoEST(person.address).call()
    except:
        return {'status': -3}


    if status == False:
        return {'status': -5}
    status = contract_by_address.functions.GetPersonInfoDR(person.address).call()
    if status:
        return {'status': -1}
    tx_wo_sign = contract_by_address.functions.RequestDelNumber().buildTransaction({
        'from': person.address,
        'nonce': web3.eth.getTransactionCount(person.address),
        'gasPrice': dit.get_gas_price()
    })

    try:
        signed_tx = person.signTransaction(tx_wo_sign)
        txId = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
    except:
        return {'status': -4}
    TX = web3.eth.waitForTransactionReceipt(txId)
    return TX


def GetAddressWithPhone(phoneNum):
    (Caddress, abiKYC, byteKYC) = dit.contract_info("KYC_Registrar")
    contract_by_address = web3.eth.contract(address = Caddress, abi = abiKYC, bytecode=byteKYC)
    return contract_by_address.functions.GetAddress(phoneNum).call()

def sendFunds(pinCode, phoneNum, value):
    keyFrom = (GenerateKey(pinCode))
    person = dit.get_adress(keyFrom)
    if(web3.eth.getBalance(person.address) < value):
        print("No funds to send the payment")
        return False
    if(not checkNumber(phoneNum)):
        print("Incorrect phone number")
        return False
    to = GetAddressWithPhone(phoneNum)
    if(len(to) == 0 or to == "0x0000000000000000000000000000000000000000"):
        print("No account with the phone number", phoneNum)
        return False
    dit.send_to(person, to, value, print_info=True)

def CreateGift(PINcode, value, time):
    (Caddress, abiPH, bytePH) = dit.contract_info("Payment_Handler")
    if Caddress == None:
        return {'status': -2}
    person = dit.get_adress(Key)
    try:
        contract_by_address =  web3.eth.contract(address=Caddress, abi=abiPH, bytecode=bytePH)
    except:
        return {'status': -3}

    tx_wo_sign = contract_by_address.functions.GiftCreate(time).buildTransaction({
        'from': person.address,
        'value': value,
        'nonce': web3.eth.getTransactionCount(person.address),
        'gasPrice': dit.get_gas_price()
    })

    try:
        signed_tx = person.signTransaction(tx_wo_sign)
        txId = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
    except:
         {'status': -4}
    TX = web3.eth.waitForTransactionReceipt(txId)
    return TX

def CancelRec(Key):
    res = ""
    (Caddress, abiKYC, byteKYC) = dit.contract_info("KYC_Registrar")
    if Caddress == None:
        return ({'status': -2}, res)
    person = GetAdress(Key)
    try:
        contract_by_address =  web3.eth.contract(address=Caddress, abi=abiKYC, bytecode=byteKYC)
        status1 = contract_by_address.functions.GetPersonInfoAR(person.address).call()
        status2 = contract_by_address.functions.GetPersonInfoDR(person.address).call()
    except:
        return ({'status': -3}, res)


    if not (status1 or status2):
        return ({'status': -1}, res)
    if status1:
        res = "Registration"
    else:
        res = "Unregistration"

    tx_wo_sign = contract_by_address.functions.Cancel().buildTransaction({
        'from': person.address,
        'nonce': web3.eth.getTransactionCount(person.address),
        'gasPrice': dit.get_gas_price()
    })
    try:
        signed_tx = person.signTransaction(tx_wo_sign)
        txId = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
    except:
        return ({'status': -4}, res)
    TX = web3.eth.waitForTransactionReceipt(txId)

    return (TX, res)


args = (sys.argv)[1:]
sizeM = len(args)

with open('faceapi.json') as file:
    json2 = json.load(file)
    key = json2['key']
    BASE_URL = json2['serviceUrl']
    group = json2['groupId']

cf.BaseUrl.set(BASE_URL)

try:
    e = cf.Key.set(key)
except:
    print( "Incorrect subscription key")
    sys.exit()

with open('network.json') as file:
    infor = json.load(file)
    privateKey = infor["privKey"]
    rpc_url = infor["rpcUrl"]

web3 = Web3(HTTPProvider(rpc_url))

if args[0] == "--balance":
    if sizeM == 2:
        PINcode = args[1]
        Key = GenerateKey(PINcode)
        if Key == None:
            print("ID is not found")
        else:
            PrintBalance(Key)

if args[0] == '--cancel':
    PINcode = args[1]
    Key = GenerateKey(PINcode)

    if Key == None:
        print("ID is not found")
        sys.exit()
    (TX,res) = CancelRec(Key)
    if TX['status'] == -4:
        print("No funds to send the request")
    if TX['status'] == -3:
        print("Seems that the contract address is not the registrar contract")
    if TX['status'] == -2:
        print("No contract address")
    if TX['status'] == -1:
        print("No requests found")
    if TX['status'] == 1:
        print(res, "canceled by", TX['transactionHash'].hex())

if args[0] == '--add':
    if sizeM > 1:
        PINcode = args[1]
        if sizeM > 2:
            PhoneNum = str(args[2])
        else:
            PhoneNum = '+1'
        if not checkNumber(PhoneNum):
            print("Incorrect phone number")
            sys.exit()
        if len(PhoneNum) != 12 or PhoneNum[0] != '+':
            print("Incorrect phone number")
            sys.exit()
        Key = GenerateKey(PINcode)
        if Key == None:
            print("ID is not found")
            sys.exit()
        TX = AddNumberRequest(PINcode, Key, PhoneNum)

        if TX['status'] == -4:
            print("No funds to send the request")
        if TX['status'] == -3:
            print("Seems that the contract address is not the registrar contract")
        if TX['status'] == -2:
            print("No contract address")
        if TX['status'] == -1:
            print("Registration request already sent")
        if TX['status'] == 0:
            print("Failed but included in", TX['transactionHash'].hex())
        if TX['status'] == 1:
            print('Registration request sent by',TX['transactionHash'].hex())

if args[0] == '--del':
    if sizeM > 1:
        PINcode = args[1]
        Key = GenerateKey(PINcode)
        if Key == None:
            print("ID is not found")
            sys.exit()
        TX = DelNumberRequest(PINcode, Key)
        if TX['status'] == -5:
            print("Account is not registered yet")
        if TX['status'] == -4:
            print("No funds to send the request")
        if TX['status'] == -3:
            print("Seems that the contract address is not the registrar contract")
        if TX['status'] == -2:
            print("No contract address")
        if TX['status'] == -1:
            print("Unregistration request already sent")
        if TX['status'] == 1:
            print("Unregistration request sent by", TX['transactionHash'].hex())

if args[0] == "--send" and len(args) == 4:
    pinCode = str(args[1])
    phoneNum = str(args[2])
    value = int(args[3])
    sendFunds(pinCode, phoneNum, value)

if args[0] == '--find':
    file_name = args[1]
    checker_for_find(file_name)
    try:
       cf.person_group.get(group)
    except cf.CognitiveFaceException as err:
         if err.code == 'PersonGroupNotFound':
                print('The service is not ready')
                sys.exit()
    if cf.person_group.get(group)['userData'] == 'group_train':
        identification(file_name, group)
    elif cf.person_group.get(group)['userData'] == 'group_update':
        print('The service is not ready')
        try:
            os.remove('person.json')
        except FileNotFoundError:
            pass
        sys.exit()
    try:
        cf.person_group.get(group)
    except cf.CognitiveFaceException as err:
        if err.code == 'PersonGroupNotFound':
            print('The service is not ready')
            try:
                os.remove('person.json')
            except FileNotFoundError:
                pass
            sys.exit()

if args[0] == '--actions':
    actions = []
    naklon = ["RollRight", "RollLeft"]
    povorot = ["YawRight", "YawLeft"]
    others = ["CloseRightEye", "CloseLeftEye", "OpenMouth"]
    kolvo = random.randint(3, 4)
    kolvo_n = random.randint(0, 1)
    if kolvo_n == 0:
        kolvo_others = random.randint(3, 4)
        kolvo_p = kolvo - kolvo_others
    if kolvo_n == 1:
        kolvo_others = random.randint(2, 3)
        kolvo_p = kolvo - kolvo_n - kolvo_others
    try:
        for i in range(kolvo_n):
            num = random.randint(0, 1)
            actions.append(naklon[num])
    except:
        pass
    try:
        for i in range(kolvo_p):
            num = random.randint(0, 1)
            actions.append(povorot[num])
    except:
        pass
    for i in range(kolvo_others):
        num = random.randint(0, 2)
        actions.append(others[num])

    otvet = {"actions": actions}
    with open("actions.json","w+") as f:
        json.dump(otvet, f)
        f.write('\n')
