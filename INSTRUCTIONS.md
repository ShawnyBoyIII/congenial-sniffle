# ResQCard - Beginner's Guide to Data Recovery

Welcome to ResQCard! If your memory card, USB drive, or hard drive is failing, throwing errors, or asking to be formatted, **stop trying to open it normally**. This tool is designed to safely extract whatever is left.

## Important First Steps
**Do I run this on Windows or Linux?**
While you *can* run this on Windows, it is highly recommended to run this tool on a **Linux** computer (or from a bootable Linux USB). Why? When you plug a broken memory card into Windows, Windows will try to fix it or read it aggressively, which can cause a failing card to permanently break. Linux leaves the card alone, allowing our tool to safely copy it.

If you are on Windows, use **Tab 3** to create a Bootable Linux USB, restart your computer, boot from that USB, and run this tool from there.

---

## Step 1: Making a Safe Copy (Tab 1 - "Create Image")
The golden rule of data recovery: **Never scan the broken drive directly**. We want to make a safe copy (an "image") of the card to your computer's hard drive first.

1. Plug in your broken memory card.
2. Open ResQCard and go to the **1. Create Image** tab.
3. In the **Source Device** field, you need to type the name of the broken card.
   - *On Linux:* This looks like `/dev/sdb` or `/dev/sdc`. You can find this by opening a terminal and typing `lsblk` before and after plugging in the card to see what new name appears.
   - *On Windows:* It looks like `\\\\.\\PhysicalDrive1`. You can find the drive number in Windows "Disk Management".
4. In the **Destination Image** field, click "Browse" and choose a place on your safe, healthy computer hard drive. Name the file something like `MyBrokenCard.img`.
5. Click **Start Imaging**. The tool will copy the raw data, skipping over the completely dead parts of the card. Be patient; this can take hours for a large, broken card.

---

## Step 2: Extracting Your Files (Tab 2 - "Extract Files")
Now that we have a safe `.img` copy on your computer, we will dig through that copy to find your pictures, videos, and documents.

1. Unplug your broken memory card and put it somewhere safe. We don't need it anymore!
2. Go to the **2. Extract Files** tab.
3. For the **Source Image**, click "Browse" and select the `MyBrokenCard.img` file you created in Step 1.
4. For the **Output Directory**, click "Browse" and select an empty folder on your safe computer where you want the recovered pictures and videos to go (e.g., your Desktop).
5. Click **Start Extracting**. The tool will scan the raw copy and dump any photos, PDFs, MP4s, or Word documents it finds into your folder.

---

## Tab 3: Creating a Bootable USB (For Windows Users)
If you are currently on Windows and want to create a safe Linux environment:
1. Plug in a blank, working USB drive (NOT the broken memory card!). **WARNING: Everything on this USB will be erased.**
2. Go to the **3. Create Bootable USB** tab.
3. Type the drive path of your blank USB (e.g., `\\\\.\\PhysicalDrive2`).
4. Click **Create Bootable USB**. It will download a lightweight Linux operating system and turn your USB into a bootable drive.
5. Once done, copy the ResQCard application folder to the same USB.
6. Restart your computer, enter your BIOS/Boot Menu, and boot from the USB. Once in Linux, run ResQCard from the terminal.