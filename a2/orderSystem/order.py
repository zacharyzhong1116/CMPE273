from __future__ import print_function
from boto3.dynamodb.conditions import Key, Attr

import boto3
import json
import time

print('Loading function')


def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def lambda_handler(event, context):
    '''Demonstrates a simple HTTP endpoint using API Gateway. You have full
    access to the request and response payload, including headers and
    status code.

    To scan a DynamoDB table, make a GET request with the TableName as a
    query string parameter. To put, update, or delete an item, make a POST,
    PUT, or DELETE request respectively, passing in the payload to the
    DynamoDB API as a JSON body.
    '''
    print("Received event: " + json.dumps(event, indent=2))

    operations = {
        'DELETE': lambda dynamo, x: dynamo.delete_item(**x),
        'GET': lambda dynamo, x: dynamo.scan(**x),
        'POST': lambda dynamo, x: dynamo.put_item(**x),
        'PUT': lambda dynamo, x: dynamo.update_item(**x),
    }

    operation = event['httpMethod']
    # if operation in operations:
    #     payload = event['queryStringParameters'] if operation == 'GET' else json.loads(event['body'])
    #     dynamo = boto3.resource('dynamodb').Table(payload['TableName'])
    #     response = dynamo.scan(FilterExpression=Attr(payload['Attribute']).eq(payload['Value']))
    #     items = response['Items']
    #     # print(items[0][payload['Attribute']])
    #     result = {'ImageName': items[0]['ImageName'], 'Content': items[0]['Content'], 'Similarity': items[0]['Similarity']};
    #     print(result)
    #     # operations[operation](dynamo, payload)
    #     return respond(None, list(result))
    # else:
    #     return respond(ValueError('Unsupported method "{}"'.format(operation)))

    if operation in operations:
        if operation == 'GET':
            payload = event['queryStringParameters']
            dynamo = boto3.resource('dynamodb').Table('orders')
            response = dynamo.scan(FilterExpression=Attr(payload['Attribute']).eq(payload['Value']))
            items = response['Items']
            print(items)
            return respond(None, items[0])

        elif operation == 'POST':
            payload = event['body']
            dyo = boto3.resource('dynamodb').Table('orders')
            responseo = dyo.put_item(
                Item={
                    'menu_id': payload['menu_id'],
                    'order_id': payload['order_id'],
                    'customer_name': payload['customer_name'],
                    'customer_email': payload['customer_email'],
                    'order_status': "processing",
                    'order':{"selection":"empty",
                             "size":"empty",
                             "costs":"empty",
                             "order_time":"empty"}
                }
            )
            dym = boto3.resource('dynamodb').Table('menu')
            responses = dym.get_item(
                Key = {"menu_id":payload['menu_id']}
            )
            item =responses['Item']
            s = item['selection']
            msg = 'Hi '+payload['customer_name']+', please choose one of these selection:  1 '+s[0]+' 2 '+s[1]+' 3 '+s[2]
            data ={'message':msg}
            jdata = json.dumps(data)
            print (data)
            return respond(None, jdata)
        elif operation == 'PUT':
            payload = event['body']
            #get the selection number
            num =int(payload['input'])
            #get the order_id and chenck its order
            order_id =event['Value']
            print (order_id)
            dyo = boto3.resource('dynamodb').Table('orders')
            oresponses = dyo.get_item(
                Key={"order_id": order_id}
            )
            oitem = oresponses['Item']
            order = oitem['order']
            print ('1111111111111111111111111111111')
            print (order['selection'])
            #get the menu detail
            menu_id = oitem['menu_id']
            dym = boto3.resource('dynamodb').Table('menu')
            mresponses = dym.get_item(
                Key={"menu_id": menu_id}
            )
            mitem = mresponses['Item']

            if order['selection'] =="empty":

                dyo.update_item(

                    Key={
                        "order_id": order_id
                    },
                    ExpressionAttributeNames={
                        "#o": "order"
                    },
                    UpdateExpression = "set #o.selection =:val",
                    ExpressionAttributeValues={
                            ':val':mitem['selection'][num-1]
                    },
                    ReturnValues="UPDATED_NEW"
                )
                s = mitem['size']
                msg = 'Which size do you want?   1 ' + s[0] + ' 2 ' + \
                      s[1] + ' 3 ' + s[2] +' 4 '+s[3] + ' 5 '+s[4]
                data = {'message': msg}
                jdata = json.dumps(data)
                print(data)
                return respond(None, jdata)

            elif order['size'] =="empty":
                localtime = time.asctime(time.localtime(time.time()))
                dyo.update_item(

                    Key={
                        "order_id": order_id
                    },
                    ExpressionAttributeNames={
                        "#o": "order"
                    },
                    UpdateExpression="set #o.size =:val",
                    ExpressionAttributeValues={
                        ':val': mitem['size'][num-1]
                    },
                    ReturnValues="UPDATED_NEW"
                )
                #get the price
                dyo.update_item(
                    Key={
                        'order_id': order_id
                    },
                    ExpressionAttributeNames={
                        "#o": "order"
                    },
                    UpdateExpression="set #o.costs =:val",
                    ExpressionAttributeValues={
                        ':val': mitem['price'][num - 1]
                    },
                    ReturnValues="UPDATED_NEW"
                )
                #get the localtime
                dyo.update_item(
                    Key={
                        'order_id': order_id
                    },
                    ExpressionAttributeNames={
                        "#o": "order"
                    },
                    UpdateExpression="set #o.order_time =:val",
                    ExpressionAttributeValues={
                        ':val': localtime
                    },
                    ReturnValues="UPDATED_NEW"
                )
                msg = 'Your order costs '+mitem['price'][num - 1]+' . We will email you when the order is ready. Thank you!'
                data = {'message': msg}
                jdata = json.dumps(data)
                print(data)
                return respond(None, jdata)

        else:
            return respond(ValueError('Unsupported PUT "{}"'.format(operation)));
    else:
        return respond(ValueError('Unsupported method "{}"'.format(operation)))