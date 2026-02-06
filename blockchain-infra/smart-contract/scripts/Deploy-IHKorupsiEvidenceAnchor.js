const { ethers, upgrades } = require("hardhat");

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deploying contracts with the account:", deployer.address);

  const EvidenceAnchor = await ethers.getContractFactory("IHKorupsiEvidenceAnchor");
  
  // Deploy Proxy + Implementation + Call Initialize
  const proxy = await upgrades.deployProxy(EvidenceAnchor, [deployer.address], { 
      initializer: 'initialize',
      kind: 'transparent' // Explicitly state transparent proxy
  });

  await proxy.waitForDeployment();
  
  console.log("IHKorupsi Anchor Proxy deployed to:", await proxy.getAddress());
}

main();