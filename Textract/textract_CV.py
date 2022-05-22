import boto3
import re

def get_kv_map(document, client):

    response = client.analyze_document(Document={'Bytes': document}, FeatureTypes=['FORMS'])

    # Get the text blocks
    blocks=response['Blocks']
    

    # get key and value maps
    key_map = {}
    value_map = {}
    block_map = {}
    for block in blocks:
        block_id = block['Id']
        block_map[block_id] = block
        if block['BlockType'] == "KEY_VALUE_SET":
            if 'KEY' in block['EntityTypes']:
                key_map[block_id] = block
            else:
                value_map[block_id] = block

    return key_map, value_map, block_map

def print_kvs(kvs):
    for key, value in kvs.items():
        print(key, ":", value)

def process_text_detection(bucket, document):
    # Get the document from S3
    s3_connection = boto3.resource('s3')
    s3_object = s3_connection.Object(bucket, document)
    s3_response = s3_object.get()

    bytes_test = bytearray(s3_response['Body'].read())
    textract = boto3.client('textract', region_name='eu-west-1')
    
    # Call Amazon Textract
    response = textract.detect_document_text(Document={'Bytes': bytes_test})

    # Print text
    print("\nText\n========")
    text = ""
    for item in response["Blocks"]:
        if item["BlockType"] == "LINE":
            print ('\033[94m' +  item["Text"] + '\033[0m')
            text = text + " " + item["Text"]

    # Amazon Comprehend client
    comprehend = boto3.client('comprehend')

    # Detect entities
    entities =  comprehend.detect_entities(LanguageCode="en", Text=text)
    print("\nEntities\n========")
    for entity in entities["Entities"]:
        print ("{}\t=>\t{}".format(entity["Type"], entity["Text"]))

    # Put item in DynamoDB
    dynamodb = boto3.client('dynamodb')    
    dynamodb.put_item(TableName='CCBDA_Project', Item={'email':{'S':'daniel.arias2493@gmail.com'}, 'skills': {'S': str(*entity["Type"]) }})


def main():
    bucket = 'sagemaker-canvas-bucket-tutorial'
    document = 'Daniel_Arias_CV.pdf'
    
    process_text_detection(bucket, document)    

if __name__ == "__main__":
    main()                  