import boto3
import os




def load_followed_users(user_id):
    dynamodb = boto3.resource('dynamodb',region_name='us-west-2')
    user_profile = dynamodb.Table('Users').get_item(Key = {'used_id': user_id})['Item']
    return user_profile.get('followed_users', [])

def follow_user(active_user_id, follow_user_id):
    dynamodb = boto3.resource('dynamodb',region_name='us-west-2')
    user_profile = dynamodb.Table('Users').get_item(Key = {'used_id': active_user_id})['Item']
    followed_users = user_profile.get('followed_users', [])
    if follow_user_id not in followed_users:
        followed_users.append(follow_user_id)
    print(user_profile)
    user_profile['followed_users'] = followed_users
    print(user_profile)
    dynamodb.Table('Users').put_item(Item = user_profile)

