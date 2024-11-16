x = input()
print(x)
outputlist = []

for i in x:
    outputlist.append(ord(i))

outputlist.sort()
for j in outputlist:
    print(chr(j))