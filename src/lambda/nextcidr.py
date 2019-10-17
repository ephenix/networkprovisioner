import cfnresponse
import json
import boto3
import ipaddress
import decimal
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


RequiredProperties = ['DynamoDbTable', 'AwsRegion', 'MasterCidr', 'VpcSize', 'SubnetSize', 'CidrIndex']

def handler(event, context):
  logger.info(event)
  params = event['ResourceProperties']
  if event['RequestType'] == 'Create':
    #ensure required properties
    try:
      for rp in RequiredProperties:
        if rp not in event['ResourceProperties']:
          raise ValueError(
            "Required event property {0} does not exist".format(rp))
    except ValueError as p:
      cfnresponse.send(event, context, cfnresponse.FAILED, responseData={'Data': repr(p)})
      raise

  # calculate mask distances
    try:
      MasterNetwork  = ipaddress.IPv4Network(params['MasterCidr'])
      FirstVpcCidr   = ipaddress.IPv4Network(str(MasterNetwork.network_address) + "/" + params['VpcSize']).with_prefixlen
      VPCDistance    = int(params['VpcSize'])    - MasterNetwork._prefixlen
      SubnetDistance = int(params['SubnetSize']) - int(params['VpcSize'])
      if not (VPCDistance > 0 and SubnetDistance > 0 ):
        raise Exception("Subnet sizes are negative!")
    except:
      cfnresponse.send(event, context, cfnresponse.FAILED, responseData={'Data': "Failed to calculate subnets"})
      raise
    
  # init database
    try:
      dynamodb = boto3.resource('dynamodb', region_name=params['AwsRegion'])
      table    = dynamodb.Table(params['DynamoDbTable'])
      items    = table.scan()["Items"]
      if len(items) == 0:
        table.put_item(Item={
            'id': decimal.Decimal(1),
            'nextcidr': FirstVpcCidr
        })
        items = table.scan()["Items"]
      else:
        items.sort(key=lambda x: x['id'])
    except:
      cfnresponse.send(event, context, cfnresponse.FAILED, responseData={'Data': "Failed to initialize database."})
      raise
    
  # get the network we want to return. 
  #   params['CidrIndex'] : 0 = VPC Cidr, 1 = First Subnet, 2 = Second Subnet, 3 = Third Subnet.. etc
  # get the next network and post it to the db ONLY if we're getting the VPC cidr. Don't update each time we get subnets
    try:
      VpcCidr     = items[-1]['nextcidr']
      VpcNetwork  = ipaddress.IPv4Network(VpcCidr)
      Subnets     = VpcNetwork.subnets(SubnetDistance)
      SubnetCidrs = [sn.with_prefixlen for sn in Subnets]
      NextVpc     = GetNextNeighbor(VpcNetwork, MasterNetwork)
      
      if params['CidrIndex'] == '0':
        responseValue = NextVpc.with_prefixlen
        table.put_item(Item={
            'id': decimal.Decimal(len(items)+1),
            'nextcidr': NextVpc.with_prefixlen
          })
      else:
        responseValue = SubnetCidrs[int(params['CidrIndex'])-1]
    except:
      cfnresponse.send(event, context, cfnresponse.FAILED, responseData={'Data': "Failed to calculate networks."})
      raise
    responseData = {'Data': responseValue}
    cfnresponse.send(event, context, cfnresponse.SUCCESS, responseData, responseValue)
    #print(responseValue)
  else:
    #print("update")
    cfnresponse.send(event, context, cfnresponse.SUCCESS, responseData={'Data': "{} succeeded.".format(event['RequestType'])})
    
# helper function to iterate subnets and get the next one
def GetNextNeighbor(subnet, parent):
  next = False
  for n in parent.subnets(prefixlen_diff=(subnet._prefixlen - parent._prefixlen)):
    if next:
      return n
    elif n == subnet:
      next = True
    else:
      pass
  raise Exception("No networks available.")