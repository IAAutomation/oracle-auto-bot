import os
import oci
import pytz
import requests

from datetime import datetime

# =========================================================
# TELEGRAM
# =========================================================

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

# =========================================================
# SENSITIVE VALUES FROM GITHUB SECRETS
# =========================================================

FINGERPRINT = os.environ["OCI_FINGERPRINT"]

PRIVATE_KEY = os.environ["OCI_PRIVATE_KEY"]

SSH_PUBLIC_KEY = os.environ["SSH_PUBLIC_KEY"]

# =========================================================
# HARD CODED OCI VALUES
# =========================================================

USER_OCID = "ocid1.user.oc1..aaaaaaaacn36y6qx6cu4ldjefc2qbu7yaa5t2arc3yvbzt7abzjtwls4i7ha"

TENANCY_OCID = "ocid1.tenancy.oc1..aaaaaaaaxh2rr7l5fgr3wpsxjv2gddobecb2klfiboaa7nu3ry32qutzvihq"

REGION = "me-dubai-1"

SUBNET_OCID = "ocid1.subnet.oc1.me-dubai-1.aaaaaaaad27ivni7hdkuznhsgdavuaqidm3xv5naihq5w4dly4zl7dx2fbka"

AVAILABILITY_DOMAIN = "TnTd:ME-DUBAI-1-AD-1"

# =========================================================
# UBUNTU 24 ARM IMAGE
# =========================================================

IMAGE_ID = "ocid1.image.oc1.me-dubai-1.aaaaaaaab352mbi4vcyymzs4ccln576k34khc357fk2hlaqx3cuzjclgkoea"

# =========================================================
# OCI CONFIG
# =========================================================

config = {
    "user": USER_OCID,
    "key_content": PRIVATE_KEY,
    "fingerprint": FINGERPRINT,
    "tenancy": TENANCY_OCID,
    "region": REGION,
}

# =========================================================
# SHAPE PRIORITY
# =========================================================

INSTANCE_CONFIGS = [
    {
        "ocpus": 1,
        "memory": 6
    },
    {
        "ocpus": 1,
        "memory": 4
    }
]

# =========================================================
# TELEGRAM FUNCTION
# =========================================================

def send_telegram(message):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        requests.post(url, data=data, timeout=15)
    except:
        pass

# =========================================================
# SMART TIME STRATEGY
# =========================================================

pakistan = pytz.timezone("Asia/Karachi")

now = datetime.now(pakistan)

hour = now.hour
minute = now.minute

run_now = False
mode = ""

# 1AM → 8AM PKT
# Every 10 mins

if 1 <= hour < 8:

    run_now = True
    mode = "HIGH SUCCESS WINDOW"

# 8AM → 7PM PKT
# Every 20 mins

elif 8 <= hour < 19:

    if minute % 20 == 0:

        run_now = True
        mode = "LOW SUCCESS WINDOW"

# 7PM → 1AM PKT
# Every 15 mins

else:

    if minute % 15 == 0:

        run_now = True
        mode = "MEDIUM SUCCESS WINDOW"

# =========================================================
# SKIP CYCLE
# =========================================================

if not run_now:

    print("Skipping current retry cycle.")
    exit()

# =========================================================
# START MESSAGE
# =========================================================

start_message = f"""
🚀 ORACLE HUNTER STARTED

🕒 Time:
{now.strftime('%Y-%m-%d %I:%M %p PKT')}

🎯 Strategy:
{mode}

🌍 Region:
Dubai

💻 Target Shapes:
• 1 OCPU / 6 GB
• 1 OCPU / 4 GB

⚡ Starting Oracle ARM capacity search...
"""

send_telegram(start_message)

# =========================================================
# OCI CLIENT
# =========================================================

compute_client = oci.core.ComputeClient(config)

# =========================================================
# MAIN LOOP
# =========================================================

success = False

for config_item in INSTANCE_CONFIGS:

    ocpus = config_item["ocpus"]
    memory = config_item["memory"]

    try:

        attempt_message = f"""
🔄 TRYING INSTANCE

⚙️ OCPUs:
{ocpus}

🧠 Memory:
{memory} GB

⏳ Sending request to Oracle...
"""

        send_telegram(attempt_message)

        launch_details = oci.core.models.LaunchInstanceDetails(

            compartment_id=TENANCY_OCID,

            availability_domain=AVAILABILITY_DOMAIN,

            display_name=f"Hunter-{ocpus}CPU-{memory}GB",

            shape="VM.Standard.A1.Flex",

            shape_config=oci.core.models.LaunchInstanceShapeConfigDetails(
                ocpus=ocpus,
                memory_in_gbs=memory
            ),

            create_vnic_details=oci.core.models.CreateVnicDetails(
                subnet_id=SUBNET_OCID,
                assign_public_ip=True
            ),

            metadata={
                "ssh_authorized_keys": SSH_PUBLIC_KEY
            },

            source_details=oci.core.models.InstanceSourceViaImageDetails(
                source_type="image",
                image_id=IMAGE_ID
            )
        )

        response = compute_client.launch_instance(launch_details)

        success_message = f"""
🎉 INSTANCE CREATED SUCCESSFULLY

🔥 Oracle ARM capacity FOUND

⚙️ OCPUs:
{ocpus}

🧠 Memory:
{memory} GB

🆔 Instance ID:
{response.data.id}

🚀 Your server is launching now.
"""

        send_telegram(success_message)

        success = True

        break

    except Exception as error:

        fail_message = f"""
❌ INSTANCE FAILED

⚙️ OCPUs:
{ocpus}

🧠 Memory:
{memory} GB

📄 Error:
{str(error)[:400]}

🔁 Trying next configuration...
"""

        send_telegram(fail_message)

# =========================================================
# FINAL RESULT
# =========================================================

if not success:

    final_message = f"""
🚫 NO ORACLE CAPACITY AVAILABLE

🕒 Time:
{now.strftime('%Y-%m-%d %I:%M %p PKT')}

📊 Tried:
• 1 OCPU / 6 GB
• 1 OCPU / 4 GB

🔁 Hunter will retry automatically.

🧠 Strategy:
{mode}
"""

    send_telegram(final_message)
