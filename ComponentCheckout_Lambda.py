'''
Top-level module run on the Lambda (usually on Greengrass Core, 
sometimes on IoT Core in cloud) for the Component Checkout module.

Should make the lambda long-lived.

Code taken and modified from:

'''

import Connect_Lambda

def main():
	Connect_Lambda.connect("Component_Checkout_Image", "Component_Checkout_Response", "receivedImage.jpg", detectComponent)


# Called every time receives a publication.
def function_handler(event, context):
	print("In function_handler with publication " + event.topic + " " + event.payload)
	# Connect_Lambda.receiveImageBlock(event)
	detectComponent(None)


def detectComponent(pictureFile):
	# TODO add SimpleCV code here
	# 
	#
	#
	Connect_Lambda.publish("Resistor")

if __name__ == "__main__":
	main()
