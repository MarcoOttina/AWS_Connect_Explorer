import sys




def run_TEST__OLD_test_fn():
    print("executing OLD_test_fn.py file")
    from TEST import OLD_test_fn
    
    #OLD_test_fn.OLD_test_fn__main()
    OLD_test_fn.main()
    print("finish")
    
    
def run__config():
    from config import config as cfg
    
    print("executing config.py file")
    
    client = None
    try:
        client = cfg.new_clientConfig_from_config('.non existing env filename')
        print(client)
    except:
        client = cfg.new_clientConfig_from_config('../resources/.env')
        print(client)
    
    print("finish")
    
    
def run__t_lambda_as_par():
    from TEST import t_lambda_as_par
    t_lambda_as_par.main()
    print("finish")
    
    
    
__ALLOWED_RUNS = {
    "OLD_test_fn": run_TEST__OLD_test_fn,
    "config": run__config,
    "t_lambda_as_par": run__t_lambda_as_par
} 
        
####


if __name__ == "__main__":
    args = sys.argv
    print("started with", len(args), "arguments")
    args_map = {}
    if len(args) > 0:
        argc = len(args)
        i = 0
        while i < argc:
            a = args[i].strip()
            if a.startswith('-'):
                i += 1
                args_map[a] = args[i].strip()
                print("\t couple of args:", a, "->", args[i].strip())
            else:
                print("\t", a)
                
            i+= 1
    
    filename_keyword = '--file'
    if '-f' in args_map or filename_keyword in args_map:
        filename = args_map['-f'] if ('-f' in args_map) else args_map[filename_keyword]
    
        if filename.endswith('.py'):
            filename = filename[0 : (len(filename)-3)]


        if filename in __ALLOWED_RUNS:
            print("running", filename, "executable \"file\"")
            __ALLOWED_RUNS[filename]()
        else:
            print("unknown filename:", filename)
            
    else:
        print("nothing to run")