from typing import Callable

def charAt(s:str, i:int) -> str:
    return s[i]

def runOn(fn: Callable[[str,int], str], args: dict):
    print("executing ...")
    print("zipping, gives ->", zip(args))
    fn(zip(args))
    print("done")

def main():
    s = "hello world"
    i = 4
    fn = charAt
    
    print("start :D")
    
    runOn(fn, {"s": s, "i": i})
    
    print("finish")
    
if __name__ == "__main__":
    main()