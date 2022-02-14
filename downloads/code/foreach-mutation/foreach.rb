nums = Array[0, 1]
numclosures = Array.new
for num in nums
    numclosures.push lambda { return num }
end
for numclosure in numclosures
    print numclosure.call, "\n"
end

# output from Ruby1.8
# 1
# 1
