import os

def test():
    try:
        print(os.environ['hashtag_file'])
        lines = [line.rstrip('\n') for line in open(os.environ['hashtag_file'])]
        return {'tag': [lines]}
    except:
        print("Hashtag filename not mentioned")

if __name__ == '__main__':
    # app.run()
    data = test()
