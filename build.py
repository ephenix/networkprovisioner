import os, zipfile, shutil, boto3, random

buildid = ''.join([random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for x in range(5)])

print("[BUILD_ID]: {}".format(buildid))

output = './NetworkProvisioner-{}'.format(buildid)

print("[OUTPUT_FOLDER]: {}\n".format(output))
print("---------------------------------------")

os.mkdir(output)
os.mkdir(output + "/lambda")
os.mkdir(output + "/templates")

CustomResourceFunctions =  ['addpermissions.py', 'nextcidr.py', 'tokenreplacetemplate.py']
NormalFunctions = ['accepttgwattachment.py']

for f in os.listdir('./src/lambda'):

    # zip Lambda Custom Resource with cfnresponse module
    if f in CustomResourceFunctions:
        print("[CREATE_FILE]    {}/lambda/{}.zip".format(output,f))
        zf = zipfile.ZipFile('{}/lambda/{}.zip'.format(output,f), mode='w')
        print("--- [WRITE] ./src/lambda/{}.zip".format(f) )
        zf.write("./src/lambda/{}".format(f))
        print("--- [WRITE] ./src/lambda/cfnresponse.py")
        zf.write("./src/lambda/cfnresponse.py")
        zf.close()

    # bundle normal functions by themselves
    if f in NormalFunctions:
        print("[CREATE_FILE]    {}/lambda/{}.zip".format(output,f))
        zf = zipfile.ZipFile('{}/lambda/{}.zip'.format(output,f), mode='w')
        print("--- [WRITE] ./src/lambda/{0}")
        zf.write("./src/lambda/{}".format(f))
        zf.close()

# Copy templates   --->   output
for f in os.listdir('./src/templates'):
    print("Copying {}   --->   {}/templates".format(f,output))
    shutil.copyfile('./src/cloudformation/{}'.format(f), '{}/templates/{}'.format(output,f))