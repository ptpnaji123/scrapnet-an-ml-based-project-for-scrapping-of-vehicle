from web3 import Web3
import json
import pdfkit
from jinja2 import Template

def generate_certificate(user_name: str, dealer_name: str, vehicle_name: str, date: str, output_file: str):
    ganache_url = "http://127.0.0.1:7545"  # Use the URL provided by Ganache
    web3 = Web3(Web3.HTTPProvider(ganache_url))
    with open("blockchain/build/contracts/CertificateContract.json", "r") as f:
        contract = json.load(f)

    network_id = str(web3.net.version)
    contract_address = contract["networks"][network_id]["address"]
    contract_abi = contract["abi"]
    contract = web3.eth.contract(address=contract_address, abi=contract_abi)
    tx_hash = contract.functions.createCertificate().transact({"from": web3.eth.accounts[0]})
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    certificate_id = receipt["transactionHash"].hex()

    with open("templates/certificate_template.html", "r") as file:
        template_str = file.read()

    template = Template(template_str)
    context = {
        "vehicle": vehicle_name,
        "user": user_name,
        "dealer": dealer_name,
        "id": certificate_id,
        "date": date,
    }
    html = template.render(context)
    pdfkit.from_string(html, output_file, options={"enable-local-file-access": ""})