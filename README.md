# 🚀 Somnia Transaction Farmer

A simple automation script to interact with the **Somnia testnet**, allowing for:
- Sending STT to random addresses
- Performing PING/PONG token swaps
- Performing QuickSwap token swaps between STT, WSTT, and USDC

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

| Property         | Type   | Required | Description                               |
|------------------|--------|---------|-------------------------------------------|
| `stt_send`       | `bool` | ✅ Yes   | Enable sending STT to random addresses    |
| `ping_pong_swap` | `bool` | ✅ Yes   | Enable PING/PONG token swap functionality |
| `quick_swap`     | `bool` | ✅ Yes   | Enable QuickSwap functionality             |

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

### `quick_swap` (QuickSwapDexSettings) (Optional)

| Property             | Type     | Required | Description                         |
|----------------------|----------|----------|-------------------------------------|
| `router_contract`    | `str`    | ✅ Yes   | Router contract address             |
| `router_abi`         | `str`    | ✅ Yes   | Router ABI JSON string              |
| `usdc_contract`      | `str`    | ✅ Yes   | USDC token contract address         |
| `wstt_contract`      | `str`    | ✅ Yes   | WSTT (wrapped STT) token contract    |

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

[quick_swap]
router_contract = '0xE94de02e52Eaf9F0f6Bf7f16E4927FcBc2c09bC7'
router_abi = '[{"inputs":[{"components":[{"internalType":"address","name":"tokenIn","type":"address"},{"internalType":"address","name":"tokenOut","type":"address"},{"internalType":"address","name":"deployer","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMinimum","type":"uint256"},{"internalType":"uint160","name":"limitSqrtPrice","type":"uint160"}],"internalType":"struct ISwapRouter.ExactInputSingleParams","name":"params","type":"tuple"}],"name":"exactInputSingle","outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountMinimum","type":"uint256"},{"internalType":"address","name":"recipient","type":"address"}],"name":"unwrapWNativeToken","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"bytes[]","name":"data","type":"bytes[]"}],"name":"multicall","outputs":[{"internalType":"bytes[]","name":"results","type":"bytes[]"}],"stateMutability":"payable","type":"function"}]'
usdc_contract = '0xE9CC37904875B459Fa5D0FE37680d36F1ED55e38'
wstt_contract = '0x4A3BC48C156384f9564Fd65A53a2f3D534D8f2b7'
```

## 📝 TODO

- [x] Implement PING/PONG token swap logic
- [ ] Implement STT token transfers to Somnia team addresses
- [x] Implement other swaps, like QuickSwap
- [ ] Implement slippage protection on swaps