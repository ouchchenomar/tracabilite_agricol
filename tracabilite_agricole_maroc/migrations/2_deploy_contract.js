const TracabiliteAgricoleMaroc = artifacts.require("TracabiliteAgricoleMaroc");
    
module.exports = function(deployer) {
  deployer.deploy(TracabiliteAgricoleMaroc);
};