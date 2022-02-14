nums = Array[0, 1]
numclosures = Array.new
nums.each { |num|
    numclosures.push lambda { return num }
}
for numclosure in numclosures
    print numclosure.call, "\n"
end

# output from Ruby1.8:
# 0
# 1
