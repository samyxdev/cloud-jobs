
1. Initialiser `eb init` et créer l'environnement de EB `eb create cloudjobs-env` dans le dossier du projet Django.

2. Créer une DB RDS (qui sera hors de l'environnement de l'EB). Ne requièrt pas l'accès publique mais il faut l'ajouter au SG de l'EB. Attention, par défaut, le nom de la BD sera `postgres` (et il n'est pas possible de changer le nom dans l'interface de création, mais c'est possible à postériori).

3. Configurations:

Ajouter au fichier `.ebextensions/django.config` (créer le dossier `.ebextensions` la première fois):
````
container_commands:
  01_migrate:
    command: "source /var/app/venv/*/bin/activate && python3 manage.py migrate"
    leader_only: true
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: cloudjobs.wsgi:application
  aws:elasticbeanstalk:environment:proxy:staticfiles:
    /static: static
````

Pour installer le service postgres sur l'EC2, ajouter cela à `.ebextensions/01_packages.config`:
````
packages:
  yum:
    git: []
    postgresql-devel: []
    libjpeg-turbo-devel: []
````

Pour les settings.py pour Django:
````
ALLOWED_HOSTS = ["localhost", "127.0.0.1", <eb-address.com>]

...

if 'RDS_DB_NAME' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.environ['RDS_DB_NAME'],
            'USER': os.environ['RDS_USERNAME'],
            'PASSWORD': os.environ['RDS_PASSWORD'],
            'HOST': os.environ['RDS_HOSTNAME'],
            'PORT': os.environ['RDS_PORT'],
        }
    }
else:
    # Local credentials
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'postgres',
            'USER': 'postgres',
            'PASSWORD': 'cloudjobs',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }
````

4. Dans l'interface web (ou via la cli), ajouter toutes les variables d'environnement nécessaires à l'EB (toutes celles utilisées dans `settings.py` et `models.py`).

5. Deployer en utilisant l'interface web de l'EB (avec un .zip) ou avec `eb deploy` mais attention avec cette commande, l'eb cli ne deploy que les changements commités ou il faut ajouter `--staged` pour prendre en compte les fichiers staged (après un git add).


Notes:
Attention au profile de eb cli (peut être spécifié avec eb --profile default) comme il faut des droits spécifiques pour créer une keypair (si on souhaite pouvoir se connecter en ssh aux instances créées par EB).
eb ssh pour directement se connecter à l'instance ec2 (si la keypair à bien été configurée à l'eb init)
