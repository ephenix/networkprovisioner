import cfnresponse
import boto3
import json
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


RequiredProperties = ['S3BucketName', 'TemplateS3Key', 'TransformedTemplateS3Key', 'TokenDict']
s3client = boto3.client('s3')

def handler(event, context):
  logger.info(event)
  params = event['ResourceProperties']
  try:
    for rp in RequiredProperties:
      if rp not in event['ResourceProperties']:
        raise ValueError(
          "Required event property {0} does not exist".format(rp))
  except ValueError as p:
    cfnresponse.send(event, context, cfnresponse.FAILED, responseData={'Data': repr(p)})
    raise

  if event['RequestType'] in ['Create', 'Update']:
    try:
      templatestr = s3client.get_object( Bucket=params['S3BucketName'], Key=params['TemplateS3Key'] )['Body'].read().decode('utf-8')
    except:
      cfnresponse.send(event, context, cfnresponse.FAILED, responseData={'Data': "Failed to download template."})
      raise
    
    #token replacement
    logger.info('Replacing tokens...')
    logger.info(json.dumps(params['TokenDict']))
    for key,val in params['TokenDict'].items():
      logger.info('    ' + key + ' = ' + val)
      templatestr = templatestr.replace(key, val)
    try:
      logger.info('Uploading transformed template...')
      Transformedtemplatebytes = str.encode(templatestr)
      s3client.put_object(Bucket=params['S3BucketName'], Body=Transformedtemplatebytes, Key=params['TransformedTemplateS3Key'])
    except:
      cfnresponse.send(event, context, cfnresponse.FAILED, responseData={'Data': "Failed to upload tokenized template."})
      raise
  else:
    try:
      logger.info('Deleting transformed template...')
      s3client.delete_object(Bucket=params['S3BucketName'], Key=params['TransformedTemplateS3Key'])
    except:
      cfnresponse.send(event, context, cfnresponse.FAILED, responseData={'Data': "Failed to delete template."})
      raise
  
  url = 'https://s3.amazonaws.com/{}/{}'.format(params['S3BucketName'],params['TransformedTemplateS3Key'])
  logger.info('Object {} Complete.'.format(event['RequestType']))
  logger.info('Url:' + url)
  responseData = {'Data': 'Object {} Complete.'.format(event['RequestType'])}
  responseValue = url
  cfnresponse.send(event, context, cfnresponse.SUCCESS, responseData, responseValue)