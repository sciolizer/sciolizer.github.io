nums = [0, 1]
numclosures = []
for num in nums:
    numclosures.append(lambda: num)
for numclosure in numclosures:
    print numclosure()

# output from Python 2.5.2
# 1
# 1
