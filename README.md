# G2VPico setup and troubleshooting on Windows

A practical lab guide and troubleshooting record for the official [G2V Optics G2VPico Python library](https://github.com/g2v-optics/G2VPico). This is a companion guide, not an official G2V release or a fork of the library.

## Current status — September 25, 2026

| Check | Observed result |
| --- | --- |
| Python environment | Python 3.11.9 in a dedicated virtual environment |
| Library installation | G2VPico 1.0.9 installed successfully from the upstream GitHub ZIP |
| Import | `from g2vpico import G2VPico` succeeded |
| Git-based installation | Not verified; successful ZIP installation bypassed Git |
| Notebook environment | Earlier notebook reported `ModuleNotFoundError`; its kernel still needs verification |
| Ethernet routing | A competing Tailscale link-local route was found; a temporary device-specific Ethernet route was added and verified |
| Device connection | Still timed out after correcting the route; no Ethernet neighbor entry was resolved for the supplied device address |
| Illumination | No commands to change light output were executed in these tests |

**Installation succeeded. Communication with the physical Pico remains unresolved.** The device address supplied during troubleshooting came from a saved notebook and has not been confirmed on the current control-box interface. The routing conflict was real, but fixing it did not establish communication. There is no evidence yet that reinstalling Miniconda is necessary.

Actual device IDs, campus addresses, usernames, and screenshots are omitted. Substitute your current device information in the commands below.

## 1. Prepare the equipment

- Power on the Pico and its control box and open the normal Pico software.
- Connect the Windows computer's Ethernet adapter to the control box.
- Use Wi-Fi for internet access during software installation if needed.
- Confirm the unit has API access enabled. G2V describes the Python API as part of its optional Variable Spectra module.
- Keep illumination off during initial connection testing.

On the **Pico control box**, record its current wired IPv4 address, subnet mask, and 16-character Pico ID. The upstream README describes finding the IP through the network icon or `ifconfig` in the control-box terminal, and the ID at the bottom-right of the Pico GUI below the version number. Preserve leading zeros.

`ifconfig` is for the control box's Linux environment. On a Windows laptop, use `ipconfig`; that shows the laptop's addresses, not the Pico's. A value copied from an old notebook may no longer be current.

## 2. Install in an isolated Python environment

Open PowerShell and list installed Python versions:

```powershell
py --list
```

Our successful installation used Python 3.11.9. This is an observed result, not an upstream compatibility guarantee. If Python is missing, install it from [python.org](https://www.python.org/downloads/windows/).

From your downloaded copy of this guide, run:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install https://github.com/g2v-optics/G2VPico/archive/refs/heads/main.zip
.\.venv\Scripts\python.exe -c "from g2vpico import G2VPico; print('G2VPico import OK')"
```

The ZIP method does not require Git. Calling the environment's Python explicitly avoids activation and PowerShell execution-policy issues. The `main` branch changes over time; record the source revision or retain the downloaded archive for reproducible future installations.

### Optional: diagnose Git installation separately

```powershell
git --version
git ls-remote https://github.com/g2v-optics/G2VPico.git HEAD
git ls-remote https://github.com/pallets/itsdangerous.git HEAD
```

The second repository is a read-only comparison for Git transport; these commands do not install or execute its code. If both remote queries fail, investigate Git, proxy, certificates, or network access. If only G2VPico fails, investigate that repository/access path. Passing these commands verifies Git transport, not Python package building.

If testing the Git-based installation is necessary, use a separate disposable environment:

```powershell
py -3.11 -m venv .venv-git-check
.\.venv-git-check\Scripts\python.exe -m pip install "git+https://github.com/g2v-optics/G2VPico.git@main"
```

Do not use `pip install git`: that does not install the Git command-line application. Get Git from [git-scm.com](https://git-scm.com/downloads/win) if it is missing.

## 3. Use the correct notebook kernel

A library installed in one Python environment is not automatically available in another notebook kernel. In the failing notebook, inspect:

```python
import sys
print(sys.executable)
```

To make the guide's environment available as a kernel:

```powershell
.\.venv\Scripts\python.exe -m pip install ipykernel
.\.venv\Scripts\python.exe -m ipykernel install --user --name g2vpico-lab --display-name "Python (G2VPico Lab)"
```

Select **Python (G2VPico Lab)** in the notebook's kernel selector, restart the kernel, and verify the import. This kernel-registration procedure is guidance; it was not performed during our session.

## 4. Check Ethernet addressing and routes

```powershell
ipconfig
route print -4
```

The laptop and Pico need different addresses in the same subnet. A directly connected pair may use link-local addresses in `169.254.0.0/16`; such an address alone does not prove a fault or confirm the peer is reachable. If the Pico uses a static address, configure the laptop's dedicated Ethernet adapter in its actual subnet using Windows Network & internet settings. Do not assume the upstream example address is a factory default.

During our session both Ethernet and a Tailscale adapter advertised `169.254.0.0/16`. Windows preferred the Tailscale route. A temporary host route directed just the Pico destination through Ethernet.

If you observe this specific conflict, use **Administrator PowerShell** after substituting the actual Pico IP and current Ethernet interface index from `route print`:

```powershell
$picoIp = "YOUR_PICO_IP"
$ethernetIndex = 44 # Example only: replace with your current Ethernet interface index.
route ADD $picoIp MASK 255.255.255.255 0.0.0.0 METRIC 1 IF $ethernetIndex
route print $picoIp
```

Expect `OK!` and a host route using the Ethernet address. This is not persistent across reboot and may disappear when the adapter changes. To remove this specific temporary route:

```powershell
route DELETE $picoIp MASK 255.255.255.255 0.0.0.0 IF $ethernetIndex
```

Do not copy another computer's interface index or disable unrelated adapters as a first step.

## 5. Test the API connection without changing output

```powershell
$picoIp = "YOUR_PICO_IP"
Test-NetConnection -ComputerName $picoIp -Port 50000
.\.venv\Scripts\python.exe .\test_pico.py --ip $picoIp --id YOUR_16_CHARACTER_PICO_ID
```

The official library uses TCP port **50000**. The included script sets a ten-second socket timeout and reads only identification and channel information. Expected success:

```text
Connected successfully
Pico ID: ...
Channel count: ...
Available channels: [...]
```

Our test instead timed out inside the library's socket connection. This occurred before an API response or channel read, so it does not establish whether the ID is correct or the API entitlement is enabled.

If it times out, verify the current device IP on the control box, power, cable endpoint, wired interface, and route. `arp -a` can help check whether a neighbor was resolved. A failed ping alone does not prove a device is offline. If TCP succeeds but API initialization fails, investigate the exact API error, ID, device software, and entitlement.

## Troubleshooting reference

| Symptom | Interpretation / next check |
| --- | --- |
| No matching distribution found for git | Git was being treated as a Python package; use ZIP installation or install the Git application |
| ModuleNotFoundError: g2vpico | Check the Python executable and notebook kernel; install into that environment |
| ProxyError during pip | Check network/proxy access; our restricted initial attempt failed, and an authorized network-enabled retry succeeded |
| Import works, socket connect times out | Installation is working; investigate addressing, routing, physical connection, and filtering |
| Connection refused | Check the API service and correct destination/port |
| Pico ID invalid | Recopy the 16-character ID with leading zeros |
| Pico API not enabled | Confirm API availability with G2V |
| route requires elevation | Run the route command in Administrator PowerShell |

Channel PWM values are not percentages: setting a channel to `50` is not equivalent to 50% global intensity. Review upstream examples before running them because they can change illumination.

## Optional SSH troubleshooting record

SSH was explored as a way to operate a separate Windows lab computer; it is **not required for Pico Ethernet control**. OpenSSH was installed and started. Local loopback and local Wi-Fi IPv4 tests on port 22 passed. The original firewall rule covered Private networks while Wi-Fi was Public. A separate Public/Wi-Fi rule restricted to the client IP was added; its enabled/profile/action fields were confirmed.

Remote connections still timed out, including a user-run test outside the assistant. Campus client isolation or another firewall policy remained possible, but neither was established as the cause. A local self-test does not prove remote reachability, and matching rule fields do not prove effective policy permits traffic. Ask network administrators to check the exact source, destination, and TCP port rather than disabling the firewall. Remove temporary access rules when no longer needed.

## Next step

Confirm the Pico's current wired address directly on the control box, then repeat the port and read-only API tests. Reinstalling Miniconda will not resolve an unreachable Ethernet destination.

## Sources

- [Official G2VPico repository and API documentation](https://github.com/g2v-optics/G2VPico)
- [API implementation](https://github.com/g2v-optics/G2VPico/blob/main/g2vpico/MainClass.py)
- [G2V product information](https://g2voptics.com/)
- [Python virtual environments](https://docs.python.org/3/library/venv.html)
- [Microsoft Windows OpenSSH setup](https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse)
- [Microsoft firewall rule documentation](https://learn.microsoft.com/en-us/powershell/module/netsecurity/new-netfirewallrule)
