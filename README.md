# Smart-Lab-Repo
Smart Lab Project for Edge Computing (ECE 590.04). Uses AWS Greengrass.

Run with Python 2.7

Run on Lambda:
ComponentCheckout_Lambda.py - top level with handler
Connect_Lambda.py
FeatureExtractor_Lambda.py

Run on End Device Raspberry Pi:
ComponentCheckout_Pi.py - top level, run with "python ComponentCheckout_Pi.py" to start the whole system
Connect_Pi.py

Offline Training and Classification:
Classifier.py
dataset directory
trained_model_bins_normalized_700_400
