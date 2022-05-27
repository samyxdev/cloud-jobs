from django.db import models
from django.contrib.auth.models import User
from http.client import UnimplementedFileMode
from django.db import models
import boto3
import os
import logging

logger = logging.getLogger(__name__)

JOBS_TABLE_GET = os.environ.get('JOBS_TABLE_GET')
JOBS_TABLE_SAVE = os.environ.get('JOBS_TABLE_SAVE')

AWS_REGION = os.environ.get('AWS_REGION')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

# Brutal check of the variabels
assert not AWS_REGION is None
assert not JOBS_TABLE_GET is None

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
            dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
            table = dynamodb.Table(JOBS_TABLE_GET)
        except Exception as e:
            logger.error(
                'Error connecting to database table: ' + (e.fmt if hasattr(e, 'fmt') else '') + ','.join(e.args) + ".AWS_REGION=" + AWS_REGION + ",JOBS_TABLE_GET=" + JOBS_TABLE_GET)
            return None

        # Apply query
        if filters is None:
            rep = table.scan(Limit=limit)
        else:
            # To make the search case sensitive, we'll add the two possible combinaison
            # E.g.: software engineer, Software Engineer
            filters[":title"] = [filters[":title"].lower(), " ".join([word[0].upper() + word[1:] for word in filters[":title"].split(" ")])]

            filter_expr = ["contains(title, :title)"]

            rep = table.scan(Limit=limit,
                            FilterExpression=' and '.join(filter_expr),
                            ExpressionAttributeValues=filters)

        if rep['ResponseMetadata']['HTTPStatusCode'] == 200:
            return self.process_listings(rep['Items'])

        logger.error('Error retrieving jobs from database. Reponse:'+ str(rep['ResponseMetadata']['HTTPStatusCode']))
        return None



    def save_job(self, user, link, title, company, description, skills, location, salary):
        try:
            dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY )
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
            dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
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
        logger.info(f"Env vars: {AWS_REGION}, {JOBS_TABLE_SAVE}")

        # Adding the user id to the dict
        cv_features["id"] = id

        try:
            dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
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




