from django.db import models
from django.contrib.auth.models import User

'''
# Create your models here.
class JobDescription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.TextField(verbose_name='Title', null=True)
    company = models.TextField(verbose_name='Company', null=True)
    description = models.TextField(verbose_name='Description', null=True)
    link = models.TextField(verbose_name='link', null=True)


    def __str__(self):
        return self.user
        # TO RETURN THE DATA SAVED AND DISPLAY IT


class Meal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=10000, blank = True, null = True)
    category = models.CharField(max_length=10, blank = True, null = True)
    instructions = models.CharField(max_length=4000, blank = True, null = True)
    region = models.CharField(max_length=20, blank = True, null = True)
    slug = models.SlugField(default = 'test')
    image_url = models.CharField( max_length=10000, blank = True, null = True)

    def __str__(self):
        return self.name


'''
from http.client import UnimplementedFileMode
from django.db import models
import boto3
import os
import logging

logger = logging.getLogger(__name__)

<<<<<<< HEAD
JOBS_TABLE = 'jobs'
=======
JOBS_TABLE = os.environ.get('JOBS_TABLE')
>>>>>>> 0d708ae461f95273b657b3585cb2b953f437f2c8

#AWS_REGION = os.environ.get('AWS_REGION')
#AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
#AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

class Jobs(models.Model):
<<<<<<< HEAD
    '''
    def get_jobs(self, filters=None, limit=100):
=======
    @staticmethod
    def process_listings(listings):
        for listing in listings:
            for k in listing.keys():
                if listing[k] is None:
                    listing[k] = f"No {k} provided"

        return listings

    def get_hardcoded_jobs(self, filters=None, limit=100):
>>>>>>> 0d708ae461f95273b657b3585cb2b953f437f2c8
        # Hardcoded listenings for example
        hardcoded_jobs = [{"title":"Software Engineer",
                            "company":"TrustEn",
                            "description":"Super position in a super company",
                            "salary":"90k",
                            "location":None,
                            "link":"https://www.google.com/",
                            "skills":["Ruby", "Python"]},

                            {"title":"Smart Contract Dev",
                            "company":"Slope.fi",
                            "description":"Solidity expert with 2+ years experience related to SC developpment.",
                            "salary":None,
                            "location":"Remote",
                            "link":"https://www.google.com/",
                            "skills":["Solidity"]}]

<<<<<<< HEAD
        return hardcoded_jobs
    '''
=======
        return self.process_listings(hardcoded_jobs)
>>>>>>> 0d708ae461f95273b657b3585cb2b953f437f2c8

    def get_jobs(self, filters=None, limit=5):
        """Retrieve jobs from the DynamoDB. Can use filters formatted
         for the search in the DB.

         TODO: Search to be improved to avoid case-sensitive matching

        Arguments:
        filters: Dict {":title":"pattern_to_search_job_titles", ":tags":"tags_to_look_for_in_listings"}
        limit: Number of jobs to display
        """
        try:
            dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
            table = dynamodb.Table(JOBS_TABLE)
        except Exception as e:
            logger.error(
                'Error connecting to database table: ' + (e.fmt if hasattr(e, 'fmt') else '') + ','.join(e.args))
            return None

        # Apply query
        if filters is None:
            rep = table.scan(Limit=limit)
        else:
            filter_expr = ["contains(title, :title)"]
            rep = table.scan(Limit=limit,
                            FilterExpression=' and '.join(filter_expr),
                            ExpressionAttributeValues=filters)
            #raise NotImplementedError("Job filtering hasn't been implemented yet.")

        if rep['ResponseMetadata']['HTTPStatusCode'] == 200:
            return self.process_listings(rep['Items'])

        logger.error('Error retrieving jobs from database. Reponse:'+ str(rep['ResponseMetadata']['HTTPStatusCode']))
        return None


<<<<<<< HEAD
=======



>>>>>>> 0d708ae461f95273b657b3585cb2b953f437f2c8
class CV(models.Model):
    def handle_cv_upload(self, f, f_id):
        print("New CV uploaded, uuid=" + f_id)
        with open("file_" + f_id, 'wb+') as destination:
            # ... do something here with the CV
            pass

        return None

    def insert_cv_extractions(self, cv_features, id=None):
        """Insert the features of the CV associated to one's user
        id to the database."""
        logger.info(f"Env vars: {AWS_REGION}, {JOBS_TABLE}")

        # Adding the user id to the dict
        cv_features["id"] = id

        try:
            dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY )
            table = dynamodb.Table(JOBS_TABLE)
        except Exception as e:
            logger.error(
                'Error connecting to database table: ' + (e.fmt if hasattr(e, 'fmt') else '') + ','.join(e.args))
            return 403
        try:
            response = table.put_item(
                Item=cv_features,
                ReturnValues='ALL_OLD',
            )
        except Exception as e:
            logger.error(
                'Error adding item to database: ' + (e.fmt if hasattr(e, 'fmt') else '') + ','.join(e.args))
            return 403
        status = response['ResponseMetadata']['HTTPStatusCode']
        if status == 200:
            if 'Attributes' in response:
                logger.error('Existing item updated to database.')
                return 409
            logger.error('New item added to database.')
        else:
            logger.error('Unknown error inserting item to database.')

        return status




