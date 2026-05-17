import os
import time
import requests
import oci
from datetime import datetime
import pytz

# =========================================================

# OCI CONFIG

# =========================================================

USER_OCID = "ocid1.user.oc1..aaaaaaaacn36y6qx6cu4ldjefc2qbu7yaa5t2arc3yvbzt7abzjtwls4i7ha"

TENANCY_OCID = "ocid1.tenancy.oc1..aaaaaaaaxh2rr7l5fgr3wpsxjv2gddobecb2klfiboaa7nu3ry32qutzvihq"

COMPARTMENT_OCID = "ocid1.tenancy.oc1..aaaaaaaaxh2rr7l5fgr3wpsxjv2gddobecb2klfiboaa7nu3ry32qutzvihq"

SUBNET_OCID = "ocid1.subnet.oc1.me-dubai-1.aaaaaaaad27ivni7hdkuznhsgdavuaqidm3xv5naihq5w4dly4zl7dx2fbka"

REGION = "me-dubai-1"

AVAILABILITY_DOMAIN = "TnTd:ME-DUBAI-1-AD-1"

SHAPE = "VM.Standard.A1.Flex"

INSTANCE_NAME = "openclaw-arm"

IMAGE_ID = "ocid1.image.oc1.me-dubai-1.aaaaaaaab352mbi4vcyymzs4ccln576k34khc357fk2hlaqx3cuzjclgkoea"

# =========================================================

# ENV VARIABLES

# =========================================================

FINGERPRINT = os.environ["OCI_FINGERPRINT"]

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

SSH_PUBLIC_KEY = os.environ["SSH_PUBLIC_KEY"]

# =========================================================

# OCI CLIENT

# =========================================================

config = {
"user": USER_OCID,
"key_file": "oci_api_key.pem",
"fingerprint": FINGERPRINT,
"tenancy": TENANCY_OCID,
"region": REGION,
}

compute_client = oci.core.ComputeClient(config)

# =========================================================

# TELEGRAM

# =========================================================

def send_telegram(message):

```
url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

payload = {
    "chat_id": TELEGRAM_CHAT_ID,
    "text": message,
    "parse_mode": "Markdown"
}

try:
    requests.post(url, json=payload, timeout=20)
except Exception as e:
    print(f"Telegram Error: {e}")
```

# =========================================================

# RETRY WINDOW

# =========================================================

def get_retry_window():

```
dubai = pytz.timezone("Asia/Dubai")
hour = datetime.now(dubai).hour

if 0 <= hour < 7:
    return "10 minutes"

elif 7 <= hour < 18:
    return "20 minutes"

else:
    return "15 minutes"
```

# =========================================================

# CHECK EXISTING INSTANCE

# =========================================================

def instance_exists():

```
instances = compute_client.list_instances(
    compartment_id=COMPARTMENT_OCID
).data

for inst in instances:

    if inst.display_name.startswith(INSTANCE_NAME):
        return inst

return None
```

# =========================================================

# CREATE INSTANCE

# =========================================================

def launch_instance(memory):

```
details = oci.core.models.LaunchInstanceDetails(

    compartment_id=COMPARTMENT_OCID,

    availability_domain=AVAILABILITY_DOMAIN,

    shape=SHAPE,

    display_name=f"{INSTANCE_NAME}-{memory}gb",

    shape_config=oci.core.models.LaunchInstanceShapeConfigDetails(
        ocpus=1,
        memory_in_gbs=memory
    ),

    create_vnic_details=oci.core.models.CreateVnicDetails(
        subnet_id=SUBNET_OCID,
        assign_public_ip=True
    ),

    source_details=oci.core.models.InstanceSourceViaImageDetails(
        source_type="image",
        image_id=IMAGE_ID
    ),

    metadata={
        "ssh_authorized_keys": SSH_PUBLIC_KEY
    }
)

return compute_client.launch_instance(details)
```

# =========================================================

# MAIN

# =========================================================

def main():

```
retry_window = get_retry_window()

send_telegram(
```

f"""🚀 *Oracle ARM Hunter Started*

📍 Region: `{REGION}`
💻 Shape: `{SHAPE}`
🖥 Image: `Ubuntu 24.04 ARM Minimal`

📋 Attempt Order:

1️⃣ 1 OCPU / 6GB
2️⃣ 1 OCPU / 4GB

🔁 Retry Window:
`{retry_window}`

Oracle free-tier combat initiated."""
)

```
existing = instance_exists()

if existing:

    send_telegram(
```

f"""✅ *Instance Already Exists*

🖥 Name:
`{existing.display_name}`

📌 State:
`{existing.lifecycle_state}`

No further action required."""
)

```
    return

# =====================================================
# TRY 6GB
# =====================================================

send_telegram(
```

"""🟡 *Attempt #1*

Trying preferred configuration:

• 1 OCPU
• 6GB RAM
"""
)

```
try:

    response = launch_instance(6)

    send_telegram(
```

f"""🎉 *INSTANCE CREATED SUCCESSFULLY*

✅ Configuration:
• 1 OCPU
• 6GB RAM

🆔 Instance ID:
`{response.data.id}`

Human persistence defeated cloud scarcity."""
)

```
    return

except Exception as e:

    error = str(e)

    send_telegram(
```

f"""❌ *6GB Attempt Failed*

`{error[:1200]}`

⏳ Waiting 60 seconds before fallback attempt...
"""
)

```
# =====================================================
# WAIT
# =====================================================

time.sleep(60)

# =====================================================
# TRY 4GB
# =====================================================

send_telegram(
```

"""🟠 *Attempt #2*

Trying fallback configuration:

• 1 OCPU
• 4GB RAM
"""
)

```
try:

    response = launch_instance(4)

    send_telegram(
```

f"""🎉 *INSTANCE CREATED SUCCESSFULLY*

✅ Configuration:
• 1 OCPU
• 4GB RAM

🆔 Instance ID:
`{response.data.id}`

Oracle briefly allowed happiness."""
)

```
    return

except Exception as e:

    error = str(e)

    send_telegram(
```

f"""❌ *Fallback Attempt Failed*

`{error[:1200]}`

🔁 Next retry automatically in:
`{retry_window}`

Capacity remains unavailable."""
)

if **name** == "**main**":
main()
