'''
Top-level module run on the Lambda (usually on Greengrass Core, 
sometimes on IoT Core in cloud) for the Component Checkout module.

Should make the lambda long-lived.

Code taken and modified from:

'''

import Connect-Lambda

def main():
	Connect-Lambda.connect(___, ___, ___, detectComponent)


# Called every time receives a publication.
def function_handler(event, context):
	Connect-Lambda.receiveImageBlock(event)

def detectComponent(pictureFile):
	# TODO add SimpleCV code here
	# 
	#
	#
	Connect-Lambda.publish("Resistor")

if __name__ == "__main__":
	main()