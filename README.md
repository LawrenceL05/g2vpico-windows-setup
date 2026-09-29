# Connect our G2V Pico from a Windows Python notebook

This procedure is for the Pico control box **SN503159**, using a Windows laptop, Ethernet, and a VS Code Python notebook. It uses the official [G2VPico library](https://github.com/g2v-optics/G2VPico).

**Verified September 29, 2026:** the user successfully connected from the notebook and obtained **`Channels: 32`**. This verifies installation in that notebook environment, Ethernet communication, and a successful API channel-count read. The procedure below does not change illumination.

## Confirmed device details

| Item | Value |
| --- | --- |
| Control-box hostname | `SN503159` (not the API device ID) |
| Pico ID | `0000000031a0525e` — keep all leading zeros |
| Ethernet IPv4 address | `169.254.84.67` |
| Ethernet subnet mask | `255.255.0.0` (`/16`) |
| API TCP port | `50000` |
| Pico GUI version observed | `v1.8.3` |
| Successful notebook result | `Channels: 32` |
| Socket timeout in successful notebook | 20 seconds |

The Windows laptop previously showed Ethernet address `169.254.30.77/16`. That is the laptop's address, not a value to put in the Pico constructor. Check addresses again after network changes.

## 1. Connect the equipment

1. Power on the Pico and its control box.
2. Connect the Windows laptop's Ethernet port to the control box's Ethernet port.
3. Keep the normal Pico control application open on the control box.
4. Keep Windows Wi-Fi connected for downloading the Python library if needed.

No SSH login, Linux administrator password, or Git installation is needed for this workflow.

## 2. Confirm the address on the Pico control box

On the **control box's Linux terminal**, run:

```bash
ip -4 addr show eth0
```

For this setup, the output showed:

```text
inet 169.254.84.67/16
```

Use **84**, not **94**. An earlier photograph was misread and tests were mistakenly sent to `169.254.94.67`.

The Pico ID appears at the **bottom-right of the Pico application, below its version number**. It was confirmed as `0000000031a0525e`.

If the current Ethernet address differs, use that current address throughout the remaining steps. The previously observed `100.64.24.81` belongs to Wi-Fi and is not the address used in the successful Ethernet test.

## 3. Check the connection from Windows

On the **Windows laptop**, open **PowerShell** and run:

```powershell
Test-NetConnection 169.254.84.67 -Port 50000
```

Expected result:

```text
InterfaceAlias   : Ethernet
TcpTestSucceeded : True
```

The Ethernet adapter name can differ. The user confirmed that the TCP test passed with this address. If it is False, use the troubleshooting section below before running Python.

## 4. Open the notebook in VS Code

1. On the Windows laptop, open VS Code.
2. Choose **File > Open File** and select `G2Vtest0.ipynb` from your copy of the `G2VPico_test` folder. The successful laptop screenshot showed it under `C:\Users\FRG_Admin\Desktop\G2VPico_test`; use the actual location on your computer.
3. If prompted, enable/install the Microsoft Python and Jupyter extensions.
4. Use the notebook's kernel picker at the top-right to select the Python environment you intend to use.
5. Insert a **new Code cell above the existing first cell**. Hover above the first cell and select **+ Code**.

Run only the cells described below. Do not select **Run All**: the original notebook contains an old address and commands that change LED settings.

## 5. Install the library into the notebook's environment

In the new **notebook code cell**, paste this exact line:

```python
%pip install https://github.com/g2v-optics/G2VPico/archive/refs/heads/main.zip
```

Press **Shift + Enter** and wait for installation to finish successfully.

- Use `%pip` in the notebook so installation targets its active Python environment.
- Remove any `!pip install git` line. That command does not install the G2V library.
- This ZIP installation method does not require Git.
- If installation fails, resolve the displayed installation error before continuing.

Click **Restart** in the notebook toolbar and confirm the kernel restart if asked. Keep the same selected kernel.

You only need to install again if the library is missing from a different/new environment.

## 6. Run the verified connection cell

Replace the installation cell with the following, or add a separate code cell:

```python
import socket
from g2vpico import G2VPico

socket.setdefaulttimeout(20)
pico = G2VPico("169.254.84.67", "0000000031a0525e")
print("Channels:", pico.channel_count)
```

Press **Shift + Enter** to run only this cell.

Expected and observed output:

```text
Channels: 32
```

This is Python code: run it in the notebook, not directly at a PowerShell prompt. The cell reads channel information without issuing commands to turn on the fixture or alter its settings.

Once successful, press **Ctrl + S** to save the notebook. Reuse this `pico` object in subsequent cells during the same kernel session instead of creating additional connections. After restarting the kernel, run the connection cell again.

The same connection code is available in [pico_connection_example.py](pico_connection_example.py).

## 7. Handle the original notebook cells

The old notebook includes:

- `IP = '169.254.157.28'`: this is not the confirmed current address.
- Another `G2VPico(...)` constructor: unnecessary while using the working `pico` object.
- `pico.set_channel_value(1, 50)`: changes a channel setting; 50 is a raw channel value, not 50% brightness.
- Additional socket tests aimed at the old address.

Leave these cells unrun during connection verification. Remove or revise them deliberately before using the notebook for experiments. The local `scan_leds()` helper actively changes illumination and is outside this connection procedure.

## Troubleshooting

| What you see | What to do |
| --- | --- |
| `Channels: 32` | Connection succeeded. Save the notebook. |
| `ModuleNotFoundError: No module named 'g2vpico'` | Run step 5 in this notebook, restart its kernel, and retry step 6 using the same kernel. |
| `No matching distribution found for git` | Delete `!pip install git` and use the ZIP installation cell in step 5. |
| PowerShell says the `from` keyword is unsupported | Python code was pasted into PowerShell. Put it in a notebook code cell. |
| Installation download/proxy error | Check the laptop's internet connection and the exact installation error. Ethernet to the Pico alone does not supply internet access. |
| `TcpTestSucceeded: False` | Recheck the current Pico Ethernet address and cable, then use the network checks below. |
| TCP passes but Python times out | Keep the Pico app open, restart the notebook kernel to clear prior notebook connections, rerun the TCP test, then run only the connection cell. Preserve the full traceback if it still fails. |
| API reports invalid Pico ID | Recopy `0000000031a0525e` as a quoted string with all leading zeros. |
| API reports it is not enabled | Capture the exact error and consult G2V; the successful channel-count test already established API access for this unit at that time. |

### If the Ethernet port test fails

On the **Windows laptop in PowerShell**:

```powershell
ipconfig
Test-NetConnection 169.254.84.67 -Port 50000 -InformationLevel Detailed
route print 169.254.*
```

Check that the destination is the current Pico address and Windows selects the connected Ethernet adapter. Previously, the laptop was `169.254.30.77` with mask `255.255.0.0`, compatible with the Pico's `169.254.84.67/16`.

On the **Pico control box's Linux terminal**:

```bash
ip -4 addr show eth0
ss -ltn 'sport = :50000'
```

The observed listener was `0.0.0.0:50000`. This command does not require `sudo` or a password. If no listener appears, verify the Pico application is open and consult the device's support instructions.

If Windows reports `DestinationHostUnreachable`, first verify the address carefully and the physical Ethernet connection. Do not add routes or change firewall settings simply because older troubleshooting mentioned them.

## Scope and history

The successful test confirms a channel-count read; it does not validate LED scanning, spectrum control, or a full experiment. The notebook's yellow editor underlines did not prevent the successful run shown by the user.

Earlier installation and network investigations are preserved in [the historical troubleshooting record](docs/previous-troubleshooting.md). Those older unresolved-status statements are superseded by the successful test above.

Sources: [official G2VPico documentation](https://github.com/g2v-optics/G2VPico) and [API implementation](https://github.com/g2v-optics/G2VPico/blob/main/g2vpico/MainClass.py), together with the user's control-box, Windows, and notebook screenshots.
