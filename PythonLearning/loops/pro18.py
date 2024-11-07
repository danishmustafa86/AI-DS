# 18. Use a loop to print numbers in reverse order within a given range.


arr = [1,2,3,4,5,6,7,8,9,10,11,12,13]
reversedArr = []
n = 5
for i in range(n):
    if i < n:
        reversedArr.append(arr[i])
end = len(arr) - 1
while end >= n:
    reversedArr.append(arr[end])
    end -= 1
print(reversedArr)

