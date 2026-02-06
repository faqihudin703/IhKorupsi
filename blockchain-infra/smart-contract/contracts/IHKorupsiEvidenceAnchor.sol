// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/*
 * IHKorupsiEvidenceAnchor
 * --------------------------------------------------
 * Optional blockchain module for IH-Korupsi.
 * Focused on data supply chain transparency.
 */

import "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";

contract IHKorupsiEvidenceAnchor is Initializable, AccessControlUpgradeable {

    // =========================
    // ROLES
    // =========================
    bytes32 public constant ANCHOR_ROLE = keccak256("ANCHOR_ROLE");

    // =========================
    // STRUCT
    // =========================
    struct Evidence {
        bytes32 processingId; // ID Unik dari Backend
        bytes32 sourceHash;    // Hash Raw Data
        bytes32 resultHash;    // Hash Report
        address validator;    // Alamat Wallet Validator
        uint256 timestamp;
        bool transformed;     // True jika Input != Output
    }

    // =========================
    // STORAGE
    // =========================
    mapping(bytes32 => Evidence) public evidenceRecords;

    // =========================
    // EVENTS
    // =========================
    event EvidenceAnchored(
        bytes32 indexed recordId,
        bytes32 indexed processingId,
        address indexed validator,
        bool transformed,
        uint256 timestamp
    );

    // =========================
    // INITIALIZER (REPLACES CONSTRUCTOR)
    // =========================
    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    function initialize(address admin) public initializer {
        __AccessControl_init(); // Init AccessControl Logic
        
        require(admin != address(0), "Admin zero address");
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(ANCHOR_ROLE, admin);
    }

    // =========================
    // CORE LOGIC
    // =========================
    function anchorEvidence(
        bytes32 processingId,
        bytes32 sourceHash,
        bytes32 resultHash
    ) external onlyRole(ANCHOR_ROLE) {

        require(processingId != bytes32(0), "Processing ID empty");
        require(sourceHash != bytes32(0), "Source hash empty");
        require(resultHash != bytes32(0), "Result hash empty");

        // Membuat Record ID deterministik
        bytes32 recordId = keccak256(
            abi.encodePacked(
                processingId,
                sourceHash,
                resultHash,
                msg.sender
            )
        );

        require(
            evidenceRecords[recordId].timestamp == 0,
            "Record exists"
        );

        // Validasi Integritas Forensik:
        // Data hasil (Result) HARUS berbeda dengan mentahan (Source)
        bool transformed = sourceHash != resultHash;

        evidenceRecords[recordId] = Evidence({
            processingId: processingId,
            sourceHash: sourceHash,
            resultHash: resultHash,
            validator: msg.sender,
            timestamp: block.timestamp,
            transformed: transformed
        });

        emit EvidenceAnchored(
            recordId,
            processingId,
            msg.sender,
            transformed,
            block.timestamp
        );
    }

    // =========================
    // VERIFICATION
    // =========================
    function verify(
        bytes32 recordId,
        bytes32 processingId,
        bytes32 sourceHash,
        bytes32 resultHash
    ) external view returns (bool) {

        Evidence storage rec = evidenceRecords[recordId];
        if (rec.timestamp == 0) return false;

        return (
            rec.processingId == processingId &&
            rec.sourceHash == sourceHash &&
            rec.resultHash == resultHash
        );
    }

    // =========================
    // STORAGE GAP (UPGRADE SAFE)
    // =========================
    // Slot cadangan agar upgrade di masa depan tidak merusak storage layout
    uint256[50] private __gap;
}