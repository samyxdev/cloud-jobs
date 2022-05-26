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

JOBS_TABLE_GET = os.environ.get('JOBS_TABLE_GET')
AWS_REGION_GET = os.environ.get('AWS_REGION_GET')
AWS_ACCESS_KEY_ID_GET= os.environ.get('AWS_ACCESS_KEY_ID_GET')
AWS_SECRET_ACCESS_KEY_GET = os.environ.get('AWS_SECRET_ACCESS_KEY_GET')

JOBS_TABLE_SAVE = os.environ.get('JOBS_TABLE_SAVE')
AWS_REGION_SAVE = os.environ.get('AWS_REGION_SAVE')
AWS_ACCESS_KEY_ID_SAVE = os.environ.get('AWS_ACCESS_KEY_ID_SAVE')
AWS_SECRET_ACCESS_KEY_SAVE = os.environ.get('AWS_SECRET_ACCESS_KEY_SAVE')

class Jobs(models.Model):
    @staticmethod
    def process_listings(listings):
        for listing in listings:
            for k in listing.keys():
                if listing[k] is None:
                    listing[k] = f"No {k} provided"

        return listings

    def get_jobs(self, filters=None, limit=5):
        """Retrieve jobs from the DynamoDB. Can use filters formatted
         for the search in the DB.
         TODO: Search to be improved to avoid case-sensitive matching
        Arguments:
        filters: Dict {":title":"pattern_to_search_job_titles", ":tags":"tags_to_look_for_in_listings"}
        limit: Number of jobs to display
        """
        try:
            dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION_GET)
            table = dynamodb.Table(JOBS_TABLE_GET)
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

    def save_job(self, user, link, title, company, description, skills, location, salary):
        try:
            dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION_SAVE, aws_access_key_id=AWS_ACCESS_KEY_ID_SAVE, aws_secret_access_key=AWS_SECRET_ACCESS_KEY_SAVE )
            table = dynamodb.Table(JOBS_TABLE_SAVE)
        except Exception as e:
            logger.error(
                'Error connecting to database table: ' + (e.fmt if hasattr(e, 'fmt') else '') + ','.join(e.args))
            return 403
        try:
            response = table.put_item(
                Item={
                    'user': user,
                    'link': link,
                    'title': title,
                    'company': company,
                    'description': description,
                    'skills': skills,
                    'location': location,
                    'salary': salary,

                },
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


    def get_saved_jobs(self, filters=None, limit=5):
        """Retrieve jobs from the DynamoDB. Can use filters formatted
         for the search in the DB.
         TODO: Search to be improved to avoid case-sensitive matching
        Arguments:
        filters: Dict {":title":"pattern_to_search_job_titles", ":tags":"tags_to_look_for_in_listings"}
        limit: Number of jobs to display
        """
        try:
            dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION_SAVE)
            table = dynamodb.Table(JOBS_TABLE_SAVE)
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
        logger.info(f"Env vars: {AWS_REGION_SAVE}, {JOBS_TABLE_SAVE}")

        # Adding the user id to the dict
        cv_features["id"] = id

        try:
            dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION_SAVE, aws_access_key_id=AWS_ACCESS_KEY_ID_SAVE, aws_secret_access_key=AWS_SECRET_ACCESS_KEY_SAVE)
            table = dynamodb.Table(JOBS_TABLE_SAVE)
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




