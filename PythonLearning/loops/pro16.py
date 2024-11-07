# Create a program to calculate the sum of the digits of an inputted integer.
# "786",   [1,2,3,4,5]
# num = input("Enter a number ")  
# sumOfNum = 0
# for i in num:
#     sumOfNum += int(i)     
# print("sum of number is ", sumOfNum)



# other method
# num = int(input("Enter a number "))  
# sumOfNum = 0                  
# while num > 0:
#     sumOfNum += num % 10          
#     num =  num // 10           
# print("sum of number is ", sumOfNum)






# Create a program to calculate the sum of the digits of an inputted integer.
    #  786
num = int(input("MY NAME IS SUMMAR "))  
sumofnum =0          
while num > 0 :
    sumofnum += num % 10 
    num = num // 10
    print("sumof num is ", sumofnum)
print("sumof num after while loop is ", sumofnum)
