import os, zipfile, shutil, boto3, random

basepath = os.path.dirname(os.path.realpath(__file__))
output = os.path.join(basepath,'NetworkProvisioner')

print("[OUTPUT_FOLDER]: {}\n".format(output))
print("---------------------------------------")

if os.path.exists(output):
  print("--- Cleaning output directory...")
  shutil.rmtree(output)
print("--- Creating output folder structure...")    
os.mkdir(output)
os.mkdir(os.path.join(output, "lambda"))
os.mkdir(os.path.join(output, "templates"))


for f in os.listdir( os.path.join(basepath,'src/lambda') ):
  if f != "cfnresponse.py":    
    print("[CREATE_FILE]    {}/lambda/{}.zip".format(output,f))
    zf = zipfile.ZipFile('{}/lambda/{}.zip'.format(output,f), mode='w')

    print(f'--- [WRITE] {os.path.join(basepath,"src","lambda",f)}' )
    zf.write( os.path.join(basepath,"src","lambda",f), f )

    print(f'--- [WRITE] {os.path.join(basepath,"src","lambda","cfnresponse.py")}' )
    zf.write(os.path.join(basepath,"src","lambda","cfnresponse.py"), "cfnresponse.py")

    zf.close()

# Copy templates   --->   output
for f in os.listdir('./src/templates'):
  print( f'[COPY_FILE] {os.path.join(basepath,"src","templates",f)}   --->   {os.path.join(output,"templates",f)}')
  shutil.copyfile( os.path.join(basepath,"src","templates",f), os.path.join(output,"templates",f))