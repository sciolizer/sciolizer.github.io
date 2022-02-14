nums = [0, 1]
numclosures = []
def body(num):
    numclosures.append(lambda: num)
map(body, nums)
for numclosure in numclosures:
    print numclosure()

# output from Python 2.5.2
# 0
# 1
