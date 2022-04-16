import datetime

import flask

from flask_caching.backends.base import BaseCache

try:
    import boto3
    from boto3.dynamodb.conditions import Attr
except ImportError as e:
    raise RuntimeError('No boto3 package found') from e

CREATED_AT_FIELD = 'created_at'
RESPONSE_FIELD = 'response'


def utcnow():
    """Return a tz-aware UTC datetime representing the current time"""
    return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)


class DynamoDbCache(BaseCache):
    """
    Implementation of flask_caching.BaseCache that uses an AWS DynamoDb table
    as the backend.

    The DynamoDB table is required to already exist.   The table must be
    defined with a hash_key of type string, and no sort key.  Additionally,
    you'll probably want to enable the TTL feature on the table, so that
    DynamoDB will automatically delete expired cache items.  The hash_key
    attribute name defaults to 'cache_key', and the ttl attribute name
    defaults to 'expiration_time'.  These defaults can be changed via
    constructor parameter, or via app config properties.

    Your server process will require dynamodb:GetItem and dynamodb:PutItem
    IAM permissions on the cache table.

    App config:  The factory method for this class uses the following app
    config attributes:

    CACHE_DYNAMODB_TABLE: (Required) the name of the DynamoDB table to use
    CACHE_DYNAMODB_KEY_FIELD: The name of the hash key attribute of the
                              table.  Defaults to 'cache_key'
    CACHE_DYNAMODB_EXPIRATION_TIME_FIELD: The name of the TTL field. Defaults
                                          to 'expiration_time'

    Additionally, the CACHE_DEFAULT_TIMEOUT attribute can be used to override
    default the cache timeout.

    Here is how you could create a DynamoDB table suitable for use by this
    class using the AWS CLI.

        TABLE_NAME=cache-table
        KEY_ATTRIBUTE=cache_key
        TTL_ATTRIBUTE=expiration_time

        aws dynamodb create-table \
            --table-name $TABLE_NAME \
            --attribute-definitions AttributeName=$KEY_ATTRIBUTE,AttributeType=S \
            --key-schema AttributeName=$KEY_ATTRIBUTE,KeyType=HASH \
            --billing-mode PAY_PER_REQUEST

        aws dynamodb update-time-to-live \
            --table-name $TABLE_NAME \
            --time-to-live-specification Enabled=true,AttributeName=$TTL_ATTRIBUTE

    If you use anything other than the default key and TTL attribute names,
    be sure to update the app config appropriately.

    Limitations: DynamoDB table items are limited to 400 KB in size.  Since
    this class stores cached items in a table, the max size of a cache entry
    will be slightly less than 400 KB, since the cache key and expiration
    time fields are also part of the item.

    :param table_name: The name of the DynamoDB table to use
    :param default_timeout: Set the timeout in seconds after which cache entries
                            expire
    :param key_field: The name of the hash_key attribute in the DynamoDb
                      table. This must be a string attribute.
    :param expiration_time_field: The name of the table attribute to store the
                                  expiration time in.  This will be an int
                                  attribute. The timestamp will be stored as
                                  seconds past the epoch.  If you configure
                                  this as the TTL field, then DynamoDB will
                                  automatically delete expired entries.
    :param dynamo: A boto3 dynamodb resource object. This is mainly for testing;
                   by default the class will create its own resource object.
    """

    def __init__(
            self,
            table_name,
            default_timeout=300,
            key_field='cache_key',
            expiration_time_field='expiration_time',
            dynamo=None
    ):
        super().__init__(default_timeout)
        self._table_name = table_name

        self._key_field = key_field
        self._expiration_time_field = expiration_time_field

        if dynamo is None:
            self._dynamo = boto3.resource('dynamodb')
        else:
            self._dynamo = dynamo

        self._table = self._dynamo.Table(self._table_name)

    @classmethod
    def factory(cls, app, config, args: list, kwargs: dict):
        args.insert(0, config['CACHE_DYNAMODB_TABLE'])
        key_field = config.get('CACHE_DYNAMODB_KEY_FIELD')
        expiration_time_field = config.get(
            'CACHE_DYNAMODB_EXPIRATION_TIME_FIELD')

        if key_field:
            kwargs.setdefault('key_field', key_field)
        if expiration_time_field:
            kwargs.setdefault('expiration_time_field', expiration_time_field)

        return cls(*args, **kwargs)

    def _get_item(self, key, attributes=None):
        """
        Get an item from the cache table, optionally limiting the returned
        attributes.

        :param key: The cache key of the item to fetch

        :param attributes: An optional list of attributes to fetch.  If not
                           given, all attributes are fetched.  The
                           expiration_time field will always be added to the
                           list of fetched attributes.
        :return: The table item for key if it exists and is not expired, else
                 None
        """
        kwargs = {}
        if attributes:
            if self._expiration_time_field not in attributes:
                attributes = list(attributes) + [self._expiration_time_field]
            kwargs = dict(ProjectionExpression=','.join(attributes))

        response = self._table.get_item(Key={self._key_field: key}, **kwargs)
        cache_item = response.get('Item')

        if cache_item:
            now = int(utcnow().timestamp())
            if cache_item[self._expiration_time_field] > now:
                return cache_item

        return None

    def get(self, key):
        """
        Get a cache item as a Flask Response

        :param key: The cache key of the item to fetch
        :return: If key is found and the item isn't expired, returns a Flask
                 response object containing the cached response body, status
                 code, and headers.  Else returns None
        """
        cache_item = self._get_item(key)
        if cache_item:
            response = cache_item[RESPONSE_FIELD]
            return flask.make_response(
                bytes(response['body']),
                int(response['statusCode']),
                response['headers'])

        return None

    def delete(self, key):
        """
        Deletes an item from the cache.  This is a no-op if the item doesn't
        exist

        :param key: Key of the item to delete.
        :return: True if the key existed and was deleted
        """
        try:
            self._table.delete_item(
                Key={self._key_field: key},
                ConditionExpression=Attr(self._key_field).exists()
            )
            return True
        except self._dynamo.meta.client.exceptions.ConditionalCheckFailedException:
            return False

    def _set(self, key, value, timeout=None, overwrite=True):
        """
        Store a cache item, with the option to not overwrite existing items

        :param key: Cache key to use
        :param value: A value returned by a flask view function
        :param timeout: The timeout in seconds for the cached item, to override
                        the default
        :param overwrite: If true, overwrite any existing cache item with key.
                          If false, the new value will only be stored if no
                          non-expired cache item exists with key.
        :return: True if the new item was stored.
        """
        now = utcnow()
        expiration_time = now + datetime.timedelta(
            seconds=self._normalize_timeout(timeout))
        response_obj = flask.make_response(value)

        cached_response = {
            'body': response_obj.get_data(),
            'statusCode': response_obj.status_code,
            'headers': dict(response_obj.headers)
        }

        kwargs = {}
        if not overwrite:
            # Cause the put to fail if a non-expired item with this key
            # already exists
            cond = Attr(self._key_field).not_exists() \
                | Attr(self._expiration_time_field).lte(int(now.timestamp()))
            kwargs = dict(ConditionExpression=cond)

        try:
            item = {
                self._key_field: key,
                self._expiration_time_field: int(expiration_time.timestamp()),
                CREATED_AT_FIELD: now.isoformat(),
                RESPONSE_FIELD: cached_response
            }
            self._table.put_item(Item=item, **kwargs)
            return True
        except self._dynamo.meta.client.exceptions.ConditionalCheckFailedException:
            return False

    def set(self, key, value, timeout=None):
        return self._set(key, value, timeout=timeout, overwrite=True)

    def add(self, key, value, timeout=None):
        return self._set(key, value, timeout=timeout, overwrite=False)

    def has(self, key):
        return self._get_item(key, [self._expiration_time_field]) is not None

    def clear(self):
        paginator = self._dynamo.meta.client.get_paginator('scan')
        pages = paginator.paginate(TableName=self._table_name,
                                   ProjectionExpression=self._key_field)

        with self._table.batch_writer() as batch:
            for page in pages:
                for item in page['Items']:
                    batch.delete_item(Key=item)

        return True
