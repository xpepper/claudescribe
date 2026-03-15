# Windows 11 ARM64 VM on macOS (Apple Silicon) via UTM

Step-by-step guide to set up a Windows 11 Home VM on a Mac with an M-series chip (M1/M2/M3/M4) using UTM.

---

## Prerequisites

- Mac with Apple Silicon (M1 or later)
- [UTM](https://mac.getutm.app) installed (free, open source)
- [CrystalFetch](https://apps.apple.com/app/crystalfetch-iso-downloader/id1567106460) installed (free, Mac App Store)

---

## Step 1 — Download the Windows 11 ARM64 ISO with CrystalFetch

1. Open **CrystalFetch**
2. Select **Windows 11** and architecture **arm64**
3. Select your language (e.g. English United States)
4. Click **Download** — it will build and save a `.iso` file to your Mac

> Use arm64, not amd64. The amd64 ISO will not run natively on Apple Silicon and will be extremely slow.

---

## Step 2 — Create the VM in UTM

1. Open **UTM** and click **+**
2. Select **Virtualize**
3. Select **Windows**
4. On the Windows screen:
   - Check **Install Windows 10 or higher**
   - Under **Boot ISO Image**, click **Browse** and select the `.iso` from CrystalFetch
   - Check **Install drivers and SPICE tools** (required for clipboard sharing and dynamic resolution)
   - Click **Continue**
5. **Hardware**: allocate at least **8 GB RAM** and **4 CPU cores**. Click **Continue**
6. **Storage**: allocate at least **64 GB**. Click **Continue**
7. **Shared Directory**: skip (click **Continue** without setting a path) unless you need file sharing
8. Click **Save**

---

## Step 3 — Boot and install Windows

1. Click the **Run** button (▶) in UTM
2. **If you land in a UEFI shell** instead of the Windows installer (black screen with `Shell>` prompt), type these commands one by one — no backslashes needed:
   ```
   FS0:
   cd EFI
   cd BOOT
   BOOTAA64.EFI
   ```
   > Click inside the UTM window first to capture keyboard input. The UEFI shell uses US keyboard layout regardless of your Mac's layout.

3. The Windows installer will launch. Follow the on-screen steps:
   - **Product key**: click **"I don't have a product key"** (the VM runs unactivated — fully functional for testing, just shows a watermark)
   - **Edition**: select **Windows 11 Home**
   - **Installation type**: select **Custom: Install Windows only**
   - Select the unallocated disk and click **Next**
4. Windows will install and reboot several times — this takes 10–20 minutes

---

## Step 4 — Post-install: SPICE guest tools

After Windows boots to the desktop, UTM will prompt you to install the SPICE guest tools (or they auto-install). These enable:
- Dynamic window resizing
- Clipboard sharing between Mac and VM
- Better display drivers

If they don't install automatically: open **File Explorer** inside the VM, find the mounted CD drive, and run the installer.

---

## Notes

- The VM runs **unactivated** — this is fine for testing. You cannot change wallpaper/themes but everything else works.
- Windows thinks there is no internet if SPICE network drivers are not installed. Install SPICE tools first if networking does not work.
- To escape the VM window and return to macOS: press **Control + Option** to release the mouse cursor.
