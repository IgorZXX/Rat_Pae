
from client import CLIENT

def main():
    client = CLIENT("127.0.0.1", 4000)
    client.engage()

if __name__ == "__main__":
    main()