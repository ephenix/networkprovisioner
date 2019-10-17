import json
import boto3
import ipaddress
import decimal
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
  logger.info(event)
  TgwAttachmentId = event['detail']['responseElements']['CreateTransitGatewayVpcAttachmentResponse']['transitGatewayVpcAttachment']['transitGatewayAttachmentId']
  client = boto3.client('ec2')
  response = client.accept_transit_gateway_vpc_attachment(TransitGatewayAttachmentId=TgwAttachmentId)
  logger.info(response)