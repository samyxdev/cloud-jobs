import boto3

SKILLS_TABLE = 'CCBDA_test'

AWS_REGION = "eu-west-1"

databasesNames = ["DB2","MySQL","Oracle","PostgreSQL","SQLite","SQL Server","Sybase","OpenEdge SQL","RethinkDB","Berkeley DB","memcached","redis","couchDB","mongoDB","Neo4j", "DynamoDB","AWS Neptune","Sesame","AllegroGraph","RDF/triplestores"]
programmingLanguages = ["C","Java","Python","C++","C#","Visual Basic","JavaScript","PHP","SQL","Assembly language","R","Groovy"]
cloudNames = ["AWS","Microsoft Azure", "GCP", "IBM", "SaaS", "PaaS", "IaaS"]
devOpsNames = ["Docker", "Kubernetes"]
dataScience = ["Machine Learning", "AI"]

def init():
    skills = {}

    skills['DB'] = set()
    skills['PL'] = set()
    skills['CL'] = set()
    skills['DSC'] = set()
    skills['DVOPS'] = set()

    return skills


def get_entities_aws_comprehend(text):
    skills = init()
    # Amazon Comprehend client
    comprehend = boto3.client('comprehend')

    # Detect entities
    entities = comprehend.detect_entities(LanguageCode="en", Text=text)

    for entity in entities["Entities"]:
        value =  str(entity["Text"]).strip()

        if value in databasesNames:
            skills['DB'].add(value)
        if value in programmingLanguages:
            skills['PL'].add(value)
        if value in cloudNames:
            skills['CL'].add(value)
        if value in dataScience:
            skills['DSC'].add(value)
        if value in devOpsNames:
            skills['DVOPS'].add(value)

    return skills


def process_text_detection(bucket=None, document_name=None, document_bytes=None):
    """Process a CV file to return extracted skills as a list of string"""
    if not bucket is None:
        # Get the document from S3
        s3_connection = boto3.resource('s3')
        s3_object = s3_connection.Object(bucket, document_name)
        s3_response = s3_object.get()

        document_bytes = bytearray(s3_response['Body'].read())

    textract = boto3.client('textract', region_name='eu-west-1')

    # Call Amazon Textract
    response = textract.detect_document_text(Document={'Bytes': document_bytes})

    text = get_text(response)

    skills_entities_comprehend = get_entities_aws_comprehend(text)

    final_skills = []

    for _, v in skills_entities_comprehend.items():
        final_skills += v

    return final_skills


def put_skills_db(skills):
    # Put item in DynamoDB
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    table = dynamodb.Table(SKILLS_TABLE)

    response_dynamodb = table.put_item(
        Item={
            'entity': ",".join(skills),
        }
    )

    print("response", response_dynamodb)

def get_n_matchings(skills_matchs):
    return len(skills_matchs['DB']) + len(skills_matchs['PL']) + \
    len(skills_matchs['CL']) + len(skills_matchs['DSC']) + \
    len(skills_matchs['DVOPS'])

def get_text(response):
    text = ""
    for item in response["Blocks"]:
        if item["BlockType"] == "LINE":
            text = text + " " + item["Text"]
    return text

def main():
    bucket = 'sagemaker-canvas-bucket-tutorial'
    document = 'Daniel_Arias_CV.pdf'

    skills = process_text_detection(bucket, document)
    put_skills_db(skills)


if __name__ == "__main__":
    main()