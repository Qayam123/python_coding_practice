'''Given an integer array nums, return the sum of divisors of the integers in that array that have exactly four divisors. If there is no such integer in the array, return 0.'''
class Solution:
    def sumFourDivisors(self, nums:list) -> int:
        out=[]
        for i in nums:
            i_divisors=[k for k in range(1,i) if i%k==0]+[i]
            if len(i_divisors)>=4:
                out.append(sum(i_divisors))
            else:
                out.append(0)
        return sum(out)
print(Solution().sumFourDivisors([21,4,7]))

'''Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.'''
def func1(nlist,target):
    t_list=[]
    for i in range(len(nlist)):
        for j in range(i+1,len(nlist)):
            if nlist[i]+nlist[j]==target:
                t_list.append((i,j))
    return t_list
print(func1([2,7,11,15],9))
"Identify palindrome number"
def func1(num):
    if num < 0:
        return False
    return str(num)==str(num)[::-1]
    
print(func1(121))

"palindrome check"
def func1(num):
    if num < 0:
        return False
    return str(num)==str(num)[::-1]
    
print(func1(121))

'''Write a function to find the longest common prefix string amongst an array of strings.
If there is no common prefix, return an empty string'''
def longest_common_prefix(strs):
    if not strs:
        return ""
    strs.sort()
    first, last = strs[0], strs[-1]
    i = 0
    while i < min(len(first), len(last)) and first[i] == last[i]:
        i += 1
    return first[:i]
print(longest_common_prefix(["flower", "flow", "flight"])) 

'''Given two integer arrays list1 and list2, merge them into a single list by alternating elements from each list. If one list is longer than the other, append the remaining elements of the longer list to the end of the merged list.'''
list1 = [1,2,4]
list2 = [1,3,4]
def ftest(lst1,lst2):
    out=[]
    flist=[]
    for i in range(len(lst1)):
        for j in range(len(lst2)):
            if i==j:
                out.append([lst1[i],lst2[j]])
    for i in out:
        if isinstance(i,list):
            flist.extend(i)
        else:
            flist.append(i)
    return flist 
print(ftest(list1,list2))

'''Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid. An input string is valid if:'''
def is_valid(s: str) -> bool:
    stack = []
    matching = {')': '(', ']': '[', '}': '{'}

    for ch in s:
        if ch in matching.values():        # opening bracket
            stack.append(ch)
        elif ch in matching:               # closing bracket
            if not stack or stack[-1] != matching[ch]:
                return False
            stack.pop()
        else:
            return False

    return len(stack) == 0


# Examples
print(is_valid("(999)"))  

'''Write a function to compare two lists and return True if they are identical (same elements in the same order), otherwise return False. If the lists have different lengths, print a message indicating that they are of different structure.'''  
def ftest(lst1: list, lst2: list) -> bool:
    # First, ensure lengths are the same
    if len(lst1) != len(lst2):
        print("Two lists are of different structure")
        return False

    # Compare element by element
    for i in range(len(lst1)):
        if lst1[i] != lst2[i]:
            return False
    return True

# Test
p = [1, 2, 3]
q = [1, 2, 3]
print(ftest(p, q))
"Write apython function to split the texts into equal sized chunks"
def fixed_chunking(text, chunk_size):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
def overlapping_chunking1(text,chunk_size=5,overlap=1):
    words=text.split()
    chunks=["".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size-overlap)]
    return chunks
def overlapping_chunking2(text,chunk_size=10,overlap=5):
    words=text.split()
    chunks=[text[i:i + chunk_size] for i in range(0, len(text), chunk_size-overlap)]
    return chunks 

text="To create a scheduled Batch Transform job in Amazon SageMaker that runs every day at a specific time, you need to combine SageMaker Batch Transform with Amazon EventBridge (or CloudWatch Events) for scheduling. Here’s the step-by-step approach:"
#print(fixed_chunking(text,chunk_size))
print(overlapping_chunking1(text))
print(overlapping_chunking2(text))