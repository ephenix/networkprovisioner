import cfnresponse
import boto3, json, logging, random
logger = logging.getLogger()
logger.setLevel(logging.INFO)


lambdaclient = boto3.client('lambda')

RequiredProperties = ['AccountId', 'FunctionName']
def handler(event, context):
  params = event['ResourceProperties']
  try:
    for rp in RequiredProperties:
      if rp not in params:
        raise ValueError(
          "Required event property {0} does not exist".format(rp))
  except ValueError as p:
    cfnresponse.send(event, context, cfnresponse.FAILED, responseData={'Data': repr(p)})
    raise
  logger.info(event)
  if event['RequestType'] == 'Create':
    logger.info("Create Request Recieved")
    logger.info("Generating Random String for permission SID")
    randomstring = ''.join([random.choice('abcdefghijklmnopqrstuvwxyz0123456789') for n in range(9)])
    logger.info("Random SID = " + randomstring)

    try:
      logger.info("Adding Permission to function")
      response = lambdaclient.add_permission(
        Action='lambda:InvokeFunction',
        FunctionName=params['FunctionName'],
        StatementId='xacct{}-{}'.format(params['AccountId'],randomstring),
        Principal=params['AccountId'])
      logger.info(response)
      cfnresponse.send(event, context, cfnresponse.SUCCESS, {'Data': "Success!"})
    except:
      logger.info('exception encountered.')
      cfnresponse.send(event, context, cfnresponse.FAILED, {'Data': "Failed!"}, "Couldn't add trusted entity.")
      raise
  else:
    logger.info('Nothing to update or delete. ' + event['RequestType'])
    cfnresponse.send(event, context, cfnresponse.SUCCESS, {'Data': "Success!"})