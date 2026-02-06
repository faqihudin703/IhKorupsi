import 'dotenv/config'; // Load .env otomatis
import express from 'express';
import { ethers } from 'ethers';
import Database from 'better-sqlite3';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// --- SETUP __dirname DI ES MODULES ---
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
app.use(express.json());

// --- KONFIGURASI DATABASE (BETTER-SQLITE3) ---
const DB_PATH = "./validator_audit.db";

// Pastikan folder ada
const dbDir = path.dirname(DB_PATH);
if (!fs.existsSync(dbDir)){
    fs.mkdirSync(dbDir, { recursive: true });
}

console.log(`[SQLite] Database Location: ${DB_PATH}`);

// Init DB (Synchronous - Jauh lebih cepat & simpel)
const db = new Database(DB_PATH);
db.pragma('journal_mode = WAL'); // Optimasi performa

// Create Table
db.exec(`
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        processing_id TEXT NOT NULL UNIQUE, 
        source_hash TEXT NOT NULL,
        result_hash TEXT NOT NULL,
        tx_hash TEXT,
        status TEXT DEFAULT 'PENDING',
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
`);

// --- VARIABEL GLOBAL ---
const PORT = process.env.PORT || 20371;
const BIND = process.env.BIND;
const KEYSTORE_PATH = process.env.KEYSTORE_PATH;
let wallet, contract;
let isBlockchainReady = false;

// --- START SERVER ---
async function startServer() {
    try {
        if (!fs.existsSync(KEYSTORE_PATH)) {
            throw new Error(`Keystore file missing at: ${KEYSTORE_PATH}`);
        }

        console.log("🔐 Decrypting Wallet...");
        const json = fs.readFileSync(KEYSTORE_PATH, 'utf8');
        
        // Setup Provider & Wallet (Ethers v6 Syntax)
        const provider = new ethers.JsonRpcProvider(process.env.RPC_URL);
        
        // Decrypt Keystore
        wallet = await ethers.Wallet.fromEncryptedJson(json, process.env.KEYSTORE_PASSWORD);
        wallet = wallet.connect(provider);
        
        // ABI (Hanya fungsi yang dibutuhkan)
        const abi = [
            "function anchorEvidence(bytes32 processingId, bytes32 sourceHash, bytes32 resultHash) external"
        ];
        contract = new ethers.Contract(process.env.PROXY_ADDRESS, abi, wallet);
        
        isBlockchainReady = true;
        console.log(`✅ Wallet Ready: ${wallet.address}`);

        app.listen(PORT, BIND, () => {
            console.log(`🚀 Validator running on port ${PORT}`);
        });

    } catch (error) {
        console.error("❌ Fatal Error:", error.message);
        process.exit(1);
    }
}

// --- ENDPOINTS ---
app.get('/health', (req, res) => {
    res.json({
        status: isBlockchainReady ? "ALIVE" : "STARTING",
        db_type: "better-sqlite3",
        wallet: wallet ? "UNLOCKED" : "LOCKED"
    });
});

app.post('/validate', async (req, res) => {
    const { processingId, sourceHash, resultHash } = req.body;
    
    try {
        // 1. Simpan PENDING ke DB (Synchronous - Tidak butuh await/callback)
        const insert = db.prepare(`
            INSERT OR IGNORE INTO audit_logs (processing_id, source_hash, result_hash, status) 
            VALUES (?, ?, ?, ?)
        `);
        insert.run(processingId, sourceHash, resultHash, 'PENDING');

        if (!isBlockchainReady) throw new Error("Blockchain not ready");

        console.log(`[Validator] Sending Tx: ${processingId}`);
        
        // 2. Kirim ke Blockchain
        const tx = await contract.anchorEvidence(processingId, sourceHash, resultHash);
        
        // 3. Update SUKSES
        const update = db.prepare(`
            UPDATE audit_logs SET status = 'SENT', tx_hash = ? WHERE processing_id = ?
        `);
        update.run(tx.hash, processingId);

        res.json({ status: "SUCCESS", txHash: tx.hash });

    } catch (error) {
        console.error("[Validator] Error:", error.message);
        
        // 4. Update GAGAL
        const updateFail = db.prepare(`
            UPDATE audit_logs SET status = 'FAILED' WHERE processing_id = ?
        `);
        updateFail.run(processingId);

        res.status(500).json({ status: "ERROR", message: error.message });
    }
});

startServer();