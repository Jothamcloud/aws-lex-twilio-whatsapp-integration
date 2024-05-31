import json
import boto3

def lambda_handler(event, context):
    print("Received event:", json.dumps(event, indent=2))
    dynamodb = boto3.client('dynamodb')
    intent_name = event['sessionState']['intent']['name']

    try:
        slots = event['sessionState']['intent']['slots']
        print("Slots:", json.dumps(slots, indent=2))
    except KeyError:
        slots = None
        print("Slots not found in the event object.")

    if intent_name == 'OrderStatus':
        if slots and slots.get('OrderID'):
            order_id = slots['OrderID'].get('value', {}).get('interpretedValue', None)
        else:
            order_id = None

        if order_id is None:
            return {
                'sessionState': {
                    'dialogAction': {
                        'type': 'ElicitSlot',
                        'slotToElicit': 'OrderID'
                    },
                    'intent': {
                        'name': intent_name,
                        'slots': slots,
                        'state': 'InProgress'
                    }
                },
                'messages': [
                    {
                        'contentType': 'PlainText',
                        'content': 'Please provide your order ID.'
                    }
                ]
            }

        try:
            response = dynamodb.get_item(
                TableName='CustomerOrders',
                Key={'OrderID': {'S': order_id}}
            )
            if 'Item' in response and 'Status' in response['Item']:
                order_status = response['Item']['Status']['S']
                message = f"The status of your order {order_id} is {order_status}."
            else:
                message = f"Order ID {order_id} not found."
        except Exception as e:
            message = f"An error occurred while fetching order status: {str(e)}"
        
        return {
            'sessionState': {
                'dialogAction': {
                    'type': 'Close',
                    'fulfillmentState': 'Fulfilled'
                },
                'intent': {
                    'name': intent_name,
                    'slots': slots,
                    'state': 'Fulfilled'
                }
            },
            'messages': [
                {
                    'contentType': 'PlainText',
                    'content': message
                }
            ]
        }

    elif intent_name == 'ProductInfo':
        if slots and slots.get('ProductName'):
            product_name = slots['ProductName'].get('value', {}).get('interpretedValue', None)
        else:
            product_name = None

        if product_name is None:
            return {
                'sessionState': {
                    'dialogAction': {
                        'type': 'ElicitSlot',
                        'slotToElicit': 'ProductName'
                    },
                    'intent': {
                        'name': intent_name,
                        'slots': slots,
                        'state': 'InProgress'
                    }
                },
                'messages': [
                    {
                        'contentType': 'PlainText',
                        'content': 'Please provide the name of the product you want details for.'
                    }
                ]
            }

        try:
            response = dynamodb.get_item(
                TableName='ProductInfo',
                Key={'ProductName': {'S': product_name}}
            )
            if 'Item' in response:
                product_details = response['Item'].get('Details', {}).get('S', 'Details not available')
                message = f"The details for product {product_name} are: {product_details}"
            else:
                message = f"Product {product_name} not found."
        except Exception as e:
            message = f"An error occurred while fetching product details: {str(e)}"
        
        return {
            'sessionState': {
                'dialogAction': {
                    'type': 'Close',
                    'fulfillmentState': 'Fulfilled'
                },
                'intent': {
                    'name': intent_name,
                    'slots': slots,
                    'state': 'Fulfilled'
                }
            },
            'messages': [
                {
                    'contentType': 'PlainText',
                    'content': message
                }
            ]
        }

    else:
        return {
            'sessionState': {
                'dialogAction': {
                    'type': 'Close',
                    'fulfillmentState': 'Failed'
                },
                'intent': {
                    'name': intent_name,
                    'slots': slots,
                    'state': 'Failed'
                }
            },
            'messages': [
                {
                    'contentType': 'PlainText',
                    'content': f"Intent {intent_name} is not supported."
                }
            ]
        }