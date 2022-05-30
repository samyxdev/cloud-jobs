from importlib.machinery import all_suffixes
from pydoc import TextRepr
from django.db import models
from django.contrib.auth.models import User
from http.client import UnimplementedFileMode
from django.db import models

import boto3
from boto3.dynamodb.conditions import Attr, Key
import os
import logging

from matplotlib.pyplot import text

from . import textract_CV

logger = logging.getLogger(__name__)

JOBS_TABLE_GET = os.environ.get('JOBS_TABLE_GET')
JOBS_TABLE_SAVE = os.environ.get('JOBS_TABLE_SAVE')
SKILLS_TABLE = 'user_skills'

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
         for the search in the DB. The search is case-sensitive for
         the jobs title.

         TODO: Factor all-case supporting function

        Arguments:
        filters: Dict {":title":"pattern_to_search_job_titles", ":skills":["tag1", "tag2"]}
        limit: Number of jobs to display
        """
        try:
            dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
            table = dynamodb.Table(JOBS_TABLE_GET)
        except Exception as e:
            logger.error(
                'Error connecting to database table: ' + (e.fmt if hasattr(e, 'fmt') else '') + ','.join(e.args) + ".AWS_REGION=" + AWS_REGION + ",JOBS_TABLE_GET=" + JOBS_TABLE_GET)
            return None

        if filters is None:
            rep = table.scan(Limit=limit)
        else:
            filter_expr = ""

            if filters[":title"] != "":
                filter_list = []
                # To make the search case sensitive, we'll add the two possible combinaison
                # E.g.: software engineer, Software Engineer
                all_case_jobs = [filters[":title"].lower(), " ".join([word[0].upper() + word[1:] for word in filters[":title"].split(" ")])]

                for i in range(len(all_case_jobs)):
                    filters[":title"+str(i)] = all_case_jobs[i]
                    filter_list += [f"contains(title, :title{str(i)})"]

                filter_expr += "(" + " or ".join(filter_list) + ")"

            if len(filter_expr) > 0:
                filter_list = []

                # If filter_expr is not empty, then a title was specified
                # In that case, we want to add first an AND condition before doing the rest
                if len(filter_expr) > 0:
                    filter_expr += " and "

                # To make the search case sensitive, we'll add the two possible combinaison for each skill
                # E.g.: python, Python
                all_case_skills = []
                for skill in filters[":skills"]:
                    all_case_skills += [skill.lower(), skill[0].upper() + skill[1:]]

                for i in range(len(all_case_skills)):
                    filters[":skills"+str(i)] = all_case_skills[i]
                    filter_list += [f"contains(skills, :skills{str(i)})"]

                filter_expr += "(" + " or ".join(filter_list) + ")"

            # To avoid unused paramters issues, whether we use them or not
            del(filters[":skills"])
            del(filters[":title"])

            logger.info(filter_expr)

            rep = table.scan(Limit=limit,
                            FilterExpression=filter_expr,
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


    '''
    def check_saved_jobs(self, user, link, filters=None, limit=5):
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
        #filters = user
        #if filters is None:
        #    rep = table.scan(Limit=limit)
        #else:
            #filter_expr = ["contains(title, :title)"]
        rep = table.scan(Limit=limit,
                        FilterExpression=Attr("user").eq(user) and Attr("link").eq(link))

                        #FilterExpression=Key.eq(user),
                        #ExpressionAttributeValues=filters)
        #raise NotImplementedError("Job filtering hasn't been implemented yet.")

        if rep['ResponseMetadata']['HTTPStatusCode'] == 200:
            return True

        logger.error('Error retrieving jobs from database. Reponse:'+ str(rep['ResponseMetadata']['HTTPStatusCode']))
        return False
    '''


    def get_saved_jobs(self, user, filters=None, limit=5):
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
        #filters = user
        #if filters is None:
        #    rep = table.scan(Limit=limit)
        #else:
            #filter_expr = ["contains(title, :title)"]
        rep = table.scan(Limit=limit,
                        FilterExpression=Attr("user").eq(user))

                        #FilterExpression=Key.eq(user),
                        #ExpressionAttributeValues=filters)
        #raise NotImplementedError("Job filtering hasn't been implemented yet.")

        if rep['ResponseMetadata']['HTTPStatusCode'] == 200:
            return self.process_listings(rep['Items'])

        logger.error('Error retrieving jobs from database. Reponse:'+ str(rep['ResponseMetadata']['HTTPStatusCode']))
        return None


class CV(models.Model):
    def handle_cv_upload(self, f, f_id, user_id):
        """Handler called by views to process the CV
        and insert the extracted skills in the DB. Returns skills
        so the upload view doesn't have to check the DB (the first itme)"""
        logger.info("New CV uploaded, uuid=" + f_id)

        skills = textract_CV.process_text_detection(None, None, f.file.read())
        status = self.insert_cv_extractions(skills, user_id)

        logger.info("CV Handling: Post DB insertion status:" + status)

        return skills

    def insert_cv_extractions(self, skills, id=None):
        """Insert the features of the CV associated to one's user
        id to the database."""
        logger.info(f"Env vars: {AWS_REGION}, {SKILLS_TABLE}")

        # Adding the user id to the dict
        cv_features = {"user":id, "skills":skills}

        try:
            dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
            table = dynamodb.Table(SKILLS_TABLE)
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

    def get_user_skills(self, user_id):
        """Retrieve skills from the DB"""
        try:
            dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
            table = dynamodb.Table(SKILLS_TABLE)
        except Exception as e:
            logger.error(
                'Error connecting to database table: ' + (e.fmt if hasattr(e, 'fmt') else '') + ','.join(e.args))
            return None

        rep = table.scan(FilterExpression=Attr("user").eq(user_id))

        if rep['ResponseMetadata']['HTTPStatusCode'] == 200:
            #logger.info(f"Retrieved following skills for {rep['Items']['user']}: " + ",".join(rep['Items']['skills']))
            return rep['Items'][0]['skills']

        logger.error('Error retrieving jobs from database. Reponse:'+ str(rep['ResponseMetadata']['HTTPStatusCode']))
        return None




