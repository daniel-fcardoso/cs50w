def announce(f):
    def wrapper():
        print('About to run the function')
        f()
        print('Print done with the function')
    return wrapper

@announce
def hello():
    print('Hello, world!')

hello()