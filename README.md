![IH-Korupsi Banner](banner.png)

# IH-Korupsi: Anti-Corruption Data Forensic Toolkit

**IH-Korupsi** (short for **Intelligent Hunting (IH) - Korupsi**) is an open-source Python toolkit designed to detect financial anomalies and potential corruption using pure mathematical methods **without AI/Machine Learning**.

Developed by **OurCreativity Edisi Coding** to support transparency and financial accountability worldwide.

---

## Why IH-Korupsi?

Corruption harms economies and societies. IH-Korupsi provides an educational and professional tool that can be used by:
- Government internal auditors
- Investigative journalists
- Anti-corruption researchers
- Students of data forensics
- Transparency NGOs
- Anyone committed to fighting corruption

### Core Principles
1. **Transparency**: Every anomaly detection can be explained through mathematical formulas.
2. **Auditable**: No "black box" algorithms—everything is open and deterministic.
3. **Zero AI Dependency**: Pure statistics and mathematics to ensure results are legally defensible.
4. **Open Source**: Free to use, study, and improve.

---

## Key Features

### 1. The Mathematician (Statistical Detection)

#### Benford's Law
Detects manipulation in financial reports. Benford’s Law states that in natural financial data, the first leading digit follows a specific logarithmic distribution. If someone fabricates numbers, the distribution will likely deviate.

**Case Example**: Financial reports that are manipulated tend to have an unusual spike in numbers starting with digits like 5, 6, 7, or 8.

#### Relative Size Factor (RSF)
Identifies unusual transactions for a specific entity. RSF compares an entity's largest transaction to the average of its other transactions.

**Formula**: `RSF = Largest Transaction / Average of Other Transactions`

**Case Example**: A vendor that usually receives $500–$1,000 suddenly gets a contract for $50,000.

#### Z-Score & IQR
Standard statistical methods to find extreme outliers in transaction data.

---

### 2. The Connector (Network Analysis)

#### Circular Trading Detection
Finds funds that return to the original sender through multiple intermediaries.

**Case Example**: 

```

Department A → Vendor X → Sub-vendor Y → Consultant Z → Department A

```
This pattern is often used for price mark-ups or money laundering loops.

#### Centrality Analysis
Finds hidden key actors in a network using algorithms like PageRank and Betweenness Centrality.

---

### 3. The Chronologist (Time-Series Analysis)

#### Fiscal Cliff Dumping
Detects unusual spending spikes during the final month of the fiscal year (budget dumping).

**Indicator**: Ratio of December spending vs. monthly average > 2.5x.

#### Velocity Check
Detects inhuman transaction frequencies within a short period.

**Case Example**: 50 transactions in a single day for the same vendor.

---

### 4. String Detective (Name Duplication)

#### Fuzzy Name Matching
Identifies "Ghost Vendors"—entities with slightly different names but likely the same identity.

**Examples**:
- `Global Solutions Corp` vs `Global  Solutions Corp` (double space)
- `Smith & Sons Ltd` vs `Smith and Sons Ltd`

Uses the Levenshtein Distance algorithm without external NLP libraries.

---

## Installation

### Prerequisites
- Python 3.10 or newer
- Windows / Linux / MacOS

### Setup

1. Clone this repository:
```bash
git clone [https://github.com/](https://github.com/)[username]/ih-korupsi.git
cd ih-korupsi

```

2. Install dependencies:

```bash
pip install -r requirements.txt

```

---

## Usage

### Mode 1: Run with Sample Data (For Learning)

Run the toolkit with synthetic data containing injected anomalies:

```bash
python main.py --type sample --output sample_report.json --html visual_report.html

```

The system will:

1. Generate 500 rows of synthetic transaction data.
2. Inject intentional anomalies (Benford, RSF, Fiscal Cliff).
3. Execute all detection modules.
4. Generate a JSON data report and a beautiful HTML visual report.

### Mode 2: Analyze Your Own Data

#### CSV Format

Your CSV must include at least these columns:

* `amount`: Transaction value
* `vendor_name`: Vendor or recipient name
* `vendor_id`: Unique vendor ID
* `date`: Transaction date (YYYY-MM-DD)
* `sender_id`: Sender identifier
* `receiver_id`: Receiver identifier

Example:

```bash
python main.py --input my_data.csv --type csv --output my_results.json --html report.html

```

#### Optional: Remote Reporting / Blockchain Anchoring

You can automatically send the audit evidence (input file hash & output report hash) to an external server or blockchain validator using the `--report-url` flag.

```bash
python main.py --input my_data.csv --type csv --report-url <YOUR_VALIDATOR_URL>

```

*Note: This feature is only available for CSV input files (Mode 2), as generated sample data lacks a physical source file to hash.*

---

## Blockchain Validator Edition (Full Stack) [Fork Exclusive]

This repository includes a **Blockchain Validator System** designed to anchor forensic evidence onto the **Scroll Sepolia** network. This ensures that once data is audited, the results cannot be tampered with (Immutable Proof).

---

### Infrastructure Architecture

The system utilizes a secure pipeline:

1. **IH-Korupsi CLI**: Calculates SHA-256 fingerprints of the Input (CSV) and Output (JSON).
2. **Relay Service (Python)**: Receives the fingerprints, validates requests, and generates a unique `processingId` based on Blockchain Block Timestamp.
3. **Validator Node (Node.js)**: Securely manages the Keystore Wallet and interacts with the Smart Contract.
4. **EvidenceLedger (Solidity)**: A smart contract deployed on Scroll Sepolia that permanently stores the proof.

---

### How to Run the Infrastructure

The infrastructure consists of two parts: the **Validator Node** (Docker) and the **Relay Service** (Python Systemd).

#### Step 0: Generate & Setup Keystores (One-Time Setup)

For production security, we use encrypted keystores. Run this script to generate them automatically:

1. **Create Generator Script:**
In the root folder (`ih-korupsi/`), create a file named `setup-keys.js`.
*(Note: You need `ethers` installed. Run `npm install ethers` in the root first if needed).*
```javascript
const { Wallet } = require("ethers");
const fs = require("fs");
const path = require("path");

async function createKey(privateKey, password, relativePath) {
    if (!privateKey || !password) return;

    const targetPath = path.resolve(__dirname, relativePath);
    const dirName = path.dirname(targetPath);

    console.log(`Encrypting key for: ${relativePath}...`);

    // Ensure directory exists
    if (!fs.existsSync(dirName)) {
        fs.mkdirSync(dirName, { recursive: true });
    }

    const wallet = new Wallet(privateKey);
    const encryptedJson = await wallet.encrypt(password);

    fs.writeFileSync(targetPath, encryptedJson);
    console.log(`Saved to: ${relativePath}`);
    console.log(`Address: ${wallet.address}`);
    return wallet.address;
}

async function main() {
    console.log("--- IH-KORUPSI KEYSTORE SETUP ---");

    // 1. DEPLOYER WALLET -> Goes to contracts/keystore
    // Required for deploying contracts via Hardhat
    await createKey(
        "PASTE_DEPLOYER_PRIVATE_KEY_HERE", 
        "PASSWORD_FOR_DEPLOYER", 
        "./blockchain-infra/smart-contract/keystore/deployer_keystore.json"
    );

    console.log("------------------------------");

    // 2. VALIDATOR WALLET -> Goes to validator-node folder
    // Required for the Node.js Validator Worker
    await createKey(
        "PASTE_VALIDATOR_PRIVATE_KEY_HERE", 
        "PASSWORD_FOR_VALIDATOR", 
        "./blockchain-infra/validator-bot/keystore/validator_keystore.json" 
    );

    console.log("------------------------------");
    console.log("Setup Complete! Don't forget to fund the Validator Address.");
}

main().then(() => process.exit(0)).catch(console.error);

```


2. **Run & Auto-Clean:**
Execute the script to generate files and immediately remove the script (cleaning up raw keys).
```bash
# Runs the setup AND deletes the script file upon success
node setup-keys.js && rm setup-keys.js

```

*(Windows PowerShell: `node setup-keys.js; Remove-Item setup-keys.js`)*
3. **Verify Setup:**
Check that the files are created in their respective folders:
* `blockchain-infra/smart-contract/keystore/deployer_keystore.json`
* `blockchain-infra/validator-bot/keystore/validator_keystore.json`

Now, simply update your `.env` paths:
* **In `blockchain-infra/smart-contract/.env`:**
```env
KEYSTORE_PATH="./keystore/deployer_keystore.json"

```

* **In `blockchain-infra/validator-bot/.env`:**
```env
# The file is now in the root of the validator folder
KEYSTORE_FILE=usr/src/app/keystore/validator_keystore.json

```

#### Step 1: Deploy Smart Contracts

The foundation of validator. Deploys Evidence contract to blockchain.

1.  **Navigate to infrastructure:**
    ```bash
    cd blockchain-infra/smart-contract
    npm install
    ```

2.  **Configure Environment:**
    cp .env.example .env # Configure KEYSTORE_PATH, KEYSTORE_PASSWORD, RPC_URL & CONTRACT_ADDRESS

3.  **Deploy to Scroll Sepolia:**
    ```bash
    npx hardhat run scripts/Deploy-IHKorupsiEvidenceAnchor.js --network scroll
    ```

> **Note:** Save the deployed contract addresses. You will need them for the next steps.


#### Step 2: Start Validator Node (Docker)

The Validator Node interacts with the blockchain. It runs inside Docker for stability.

1.  **Navigate to infrastructure:**
    ```bash
    cd blockchain-infra
    ```

2.  **Configure Environment:**
    cp .env.example .env # Configure KEYSTORE_PATH, KEYSTORE_PASSWORD, RPC_URL & CONTRACT_ADDRESS

3.  **Launch Validator:**
    ```bash
    # Builds the image (baking in the keystore) and starts the container
    docker build -t validator-bot:latest .
    docker run -d -p 20371:20371   --name validator-bot   --init   --restart always   --env-file .env   --log-opt max-size=50m   --log-opt max-file=3   validator-bot:latest
    ```

---

#### 🐍 Step 2: Start Relay Service (Systemd)

The Relay Service handles API requests and Rate Limiting. It runs natively on the host via Systemd.

1.  **Setup Python Environment:**
    ```bash
    cd relay
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **Launch Relay:**
    ```bash
    uvicorn relay:app --host 0.0.0.0 --port 30921
    ```

---

#### 🔌 Step 3: Connect the Toolkit

Once both services are running (Validator on Docker, Relay on Systemd), you can send forensic evidence to your local endpoint.

```bash
# Go back to root
cd ..

# Run analysis and anchor evidence to blockchain
python main.py --input my_data.csv --type csv \
  --report-url http://localhost:30921/relay/anchor \
```

## Understanding the Report

The JSON report is structured as follows:

```json
{
  "metadata": {
    "total_rows": 500,
    "total_amount": 300000000,
    "currency": "IDR"
  },
  "findings": {
    "The Mathematician": { ... },
    "The Connector": { ... },
    "The Chronologist": { ... },
    "String Detective": { ... }
  }
}

```

### Interpreting Findings

#### Benford's Law (MAD Score)

* **MAD < 0.006**: High Conformity (Normal)
* **MAD 0.006–0.012**: Acceptable
* **MAD 0.012–0.015**: Marginal (Needs attention)
* **MAD > 0.015**: Non-conformity (Red flag!)

#### RSF (Relative Size Factor)

* **RSF < 5**: Normal
* **RSF 5–10**: Needs verification
* **RSF > 10**: Highly suspicious

---

## Important Notes & Limitations

1. **Not Legal Proof**: IH-Korupsi provides **indicators only**. Anomalies do not automatically mean corruption; they require further investigation.
2. **Context Matters**: Some anomalies can be legitimate (e.g., a massive infrastructure project causing a high RSF).
3. **Data Quality**: Garbage in, garbage out. Ensure your input data is clean.
4. **Ethical Use**: This toolkit is for transparency and education. Please use it responsibly.
5. **Blockchain Scope**: The blockchain anchoring proves **Data Integrity** (that the file has not been altered since the audit) and **Timestamp** (when it happened). It does **not** guarantee that the original input data was truthful or free from fabrication.

---

## About OurCreativity Edisi Coding

We are a developer community that believes technology can be a force for social good. IH-Korupsi is one of our efforts toward a more transparent and accountable future.

**Slogan**: *"Code for Justice, Data for Transparency"*

---

## License

This project is licensed under the **MIT License**.

---

**Join us in building a cleaner, more transparent world!**
