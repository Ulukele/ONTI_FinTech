#!/usr/bin/env python
from web3 import Web3, HTTPProvider
import json
import sys
import requests
from eth_account import Account


def GetAdres(privateKey):
    adress = Account.privateKeyToAccount("0x"+privateKey)
    return adress

def GetGas(URL, defGas):
    try:
        response = requests.get(URL).text
        gasinfo = json.loads(response)['fast']
    except:
        return defGas
    return int(gasinfo * 1000000000)

def DeployContract(abi, byte, person, GasURL):
    contract = web3.eth.contract(abi=abi, bytecode=byte)
    SignedTX = contract.constructor().buildTransaction({
    'from': person.address,
    'nonce': web3.eth.getTransactionCount(person.address),
    'gasPrice': GetGas(GasURL,defGas)
    })
    SignedTX = person.signTransaction(SignedTX)
    RawTX = web3.eth.sendRawTransaction(SignedTX.rawTransaction)
    TX = web3.eth.waitForTransactionReceipt(RawTX)

    return TX

args = (sys.argv)[1:]

with open('KYC_RegistrarByte.txt') as file:
    byteKYC = str(file.read())
    if byteKYC[-1] == '\n':
        byteKYC = byteKYC[:-1]
with open('KYC_RegistrarABI.txt') as file:
    abiKYC = file.read()
    abiKYC = json.loads(abiKYC)
with open('Payment_HandlerByte.txt') as file:
    bytePayH = str(file.read())
    if bytePayH[-1] == '\n':
        bytePayH = bytePayH[:-1]
with open('Payment_HandlerABI.txt') as file:
    abiPayH = file.read()
    abiPayH = json.loads(abiPayH)

with open('network.json') as file:
    infor = json.load(file)
    privateKey = infor["privKey"]
    RecURL = infor["rpcUrl"]
    GasURL = infor["gasPriceUrl"]
    defGas = infor["defaultGasPrice"]

adres = GetAdres(privateKey)

web3 = Web3(HTTPProvider(RecURL))


if args[0] =='--deploy':
    TX1 = DeployContract(abiKYC, byteKYC, adres, GasURL)
    TX2 = DeployContract(abiPayH, bytePayH, adres, GasURL)
    print("KYC Registrar:", TX1['contractAddress'])
    print("Payment Handler:", TX2['contractAddress'])
    with open('registrar.json', 'w') as file:
        file.write(json.dumps({"registrar": {"address": TX1['contractAddress'], "startBlock": TX1['blockNumber']}, "payments": {"address": TX2['contractAddress'], "startBlock": TX2['blockNumber']}}))



### Put your code below this comment ###
#print("Show must go on")