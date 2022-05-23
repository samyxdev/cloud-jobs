from http.client import UnimplementedFileMode
from django.db import models
import boto3
import os
import logging

logger = logging.getLogger(__name__)

JOBS_TABLE = os.environ.get('STARTUP_SIGNUP_TABLE')

AWS_REGION = os.environ.get('AWS_REGION')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

class Jobs(models.Model):
    def get_jobs(self, filters=None, limit=100):
        """Retrieve jobs from the DynamoDB. Can use filters formatted
        by TODO:OTHERFUNCTION for the search in the DB.

        Arguments:
        filters: Jobs filters as a dict of the format {"filtered_field":"matching-re"}
        limit: Number of jobs to display
        """
        try:
            dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
            table = dynamodb.Table(JOBS_TABLE)
        except Exception as e:
            logger.error(
                'Error connecting to database table: ' + (e.fmt if hasattr(e, 'fmt') else '') + ','.join(e.args))
            return None

        # Make the query
        if filters is None:
            rep = table.scan(Limit=limit)
        else:
            raise NotImplementedError("Job filtering hasn't been implemented yet.")

        # Return response if valid
        if rep['ResponseMetadata']['HTTPStatusCode'] == 200:
            return rep['Items']

        logger.error('Error retrieving jobs from database. Reponse:'+ str(rep['ResponseMetadata']['HTTPStatusCode']))
        return None




class CV(models.Model):
    def handle_cv_upload(self, f, f_id):
        print("New CV uploaded, uuid=" + f_id)
        with open("file_" + f_id, 'wb+') as destination:
            # ... do something here with the CV
            pass

        return None



