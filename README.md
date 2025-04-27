# 🚀 Somnia Transaction Farmer

A simple automation script to interact with the **Somnia testnet**, allowing for:
- Sending STT to random addresses
- Performing PING/PONG token swaps (Currently unavailable)

---

## 📦 Prerequisites

- Python **3.9+**
- `pip` or `pipenv` for managing dependencies
- A funded **testnet wallet** (with STT and tokens like PING/PONG)
- Access to the **Somnia RPC endpoint**
- Minimum balance of 0.3 STT

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

To run this project, you need to create a configuration file.

1. Copy the example config:

```bash
cp settings/settings.toml.example settings/example.toml
```

2. Modify `example.toml` with your testnet private key, RPC endpoint, and feature flags.

---

## 🏃 Running the Program

Use the following command:

```bash
python main.py -c ./settings/example.toml
```

or

```bash
python main.py --config ./settings/example.toml
```

---

## 🧩 Configuration Schema

### `api` (ApiSettings)

| Property     | Type     | Required | Description                                |
|--------------|----------|----------|--------------------------------------------|
| `rpc_url`    | `str`    | ✅ Yes   | Full HTTP RPC URL for Somnia testnet       |
| `proxy`      | `str`    | ❌ No    | Optional HTTP proxy (e.g. `http://ip:port`)|
| `gas_price`  | `int`    | ❌ No    | Custom gas price in wei                    |

---

### `account` (AccountSettings)

| Property       | Type     | Required | Description                          |
|----------------|----------|----------|--------------------------------------|
| `private_key`  | `str`    | ✅ Yes   | Private key of the funded testnet wallet |
| `tran_count`   | `int`    | ✅ Yes   | Number of iterations for farming    |

---

### `farm` (FarmSettings)

| Property         | Type      | Required | Description                                 |
|------------------|-----------|----------|---------------------------------------------|
| `stt_send`       | `bool`    | ✅ Yes   | Enable sending STT to random addresses      |
| `ping_pong_swap` | `bool`    | ✅ Yes   | Enable PING/PONG token swap functionality   |

---

### `ping_pong` (PingPongSettings) (Optional)

| Property          | Type     | Required | Description                              |
|-------------------|----------|----------|------------------------------------------|
| `router_contract` | `str`    | ✅ Yes (if using ping/pong) | Router contract address                 |
| `ping_contract`   | `str`    | ✅ Yes (if using ping/pong) | "PING" token contract address            |
| `pong_contract`   | `str`    | ✅ Yes (if using ping/pong) | "PONG" token contract address            |
| `router_abi`      | `str`    | ✅ Yes (if using ping/pong) | ABI (JSON string) for the router contract |

> ℹ️ **Note:** The `ping_pong` block is optional unless `ping_pong_swap = true`.

---

## 🧪 Example Config (`example.toml`)

```toml
[api]
rpc_url = "https://somnia-testnet.rpc"
proxy = "http://127.0.0.1:8080"
gas_price = 1000000000  # 1 gwei

[account]
private_key = "0xabc123..."
tran_count = 5

[farm]
stt_send = true
ping_pong_swap = true

[ping_pong]
router_contract = "0xRouterContractAddress"
ping_contract = "0xPingTokenAddress"
pong_contract = "0xPongTokenAddress"
router_abi = '[{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"}]'
```

## 📝 TODO

- [x] Implement PING/PONG token swap logic
- [ ] Implement STT token transfers to Somnia team addresses
- [ ] Implement other swaps, like QuickSwap