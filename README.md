# Smart-Lab-Repo
Smart Lab Project for Edge Computing (ECE 590.04). Uses AWS Greengrass.

Python files ending in "_Pi" run on the end device Pi.
Python files ending in "_Lambda" run on the Lambda in Greengrass.

End Device Raspberry Pi runs ComponentCheckout_Pi.py (likely "python ComponentCheckout_Pi.py"). Run this to start the whole system.

Top level of Lambda (with handler function) is ComponentCheckout_Lambda.py
