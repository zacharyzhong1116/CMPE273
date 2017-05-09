from __future__ import print_function
from boto3.dynamodb.conditions import Key, Attr

import boto3
import json

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
            dynamo = boto3.resource('dynamodb').Table(payload['TableName'])
            response = dynamo.scan(FilterExpression=Attr(payload['Attribute']).eq(payload['Value']))
            items = response['Items']
            print(items)
            return respond(None, items[0])

        elif operation == 'POST':
            payload = event['body']
            dynamo = boto3.resource('dynamodb').Table('menu')
            response = dynamo.put_item(
                Item={
                    'menu_id': payload['menu_id'],
                    'store_name': payload['store_name'],
                    'selection': payload['selection'],
                    'size': payload['size'],
                    'price': payload['price'],
                    'store_hours': payload['store_hours']
                }
            )
            return respond(None, "200,OKAY")
        elif operation == "PUT":
            payload = event['body']
            dynamo = boto3.resource('dynamodb').Table('menu')
            dynamo.update_item(
                Key={
                    'menu_id': payload['menu_id']
                },
                UpdateExpression = "set selection =:val",
                ExpressionAttributeValues={
                        ':val':payload['selection']
                },
                ReturnValues="UPDATED_NEW"
            )
            return respond(None, "200 okay")
        elif operation == "DELETE":
            payload = event['body']
            dynamo = boto3.resource('dynamodb').Table(payload['TableName'])
            response = dynamo.delete_item(
                Key={
                    'menu_id': payload['menu_id']
                }
            )
            return respond(None, "200 OKAY");
        else:
            return respond(ValueError('Unsupported PUT "{}"'.format(operation)));
    else:
        return respond(ValueError('Unsupported method "{}"'.format(operation)))