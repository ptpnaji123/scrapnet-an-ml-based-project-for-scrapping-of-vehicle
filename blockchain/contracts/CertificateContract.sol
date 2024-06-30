// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

contract CertificateContract {
    mapping(address => bool) public certificates;

    event CertificateCreated(address indexed user);

    function createCertificate() public {
        certificates[msg.sender] = true;
        emit CertificateCreated(msg.sender);
    }

    function verifyCertificate(address user) public view returns (bool) {
        return certificates[user];
    }
}
