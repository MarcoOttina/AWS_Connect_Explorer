import json

print("start")
env = {}
with open('.env') as f:
    lines = f.readlines()
    print("read")
    
    # format: list of "key = value" pairs
    env['region'] = "eu-central-1" 
    for l in lines:
        spl = [t.strip() for t in l.strip().split('=') if t.strip() != "" ]
        if len(spl) > 0:
            #print("line: <<", l, ">>, splitted: ", spl)
            print(spl[0])
            env[spl[0]] = spl[1]
    print("processed")
    
with open('.env_new', 'w') as f:
    json.dump(env, f)
    print("dumped")
