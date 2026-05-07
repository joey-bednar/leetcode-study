# Notes

## Binary Tree

### Traversals

        1
       / \
      2   3
     / \ / \
    4  5 6  7

#### Depth First Search

##### PreOrder
    Root -> Left Subtree -> Right Subtree
    1,2,4,5,3,6,7
##### InOrder
    Left Subtree -> Root -> Right Subtree
    4,2,5,1,6,3,7
##### PostOrder
    Left Subtree -> Right Subtree -> Root
    4,5,2,6,7,3,1
#### Breadth First Search
##### LevelOrder
    Top Level -> Bottom Level (left to right)
    1,2,3,4,5,6,7

## Heap

### Indexing

|  | **Zero** | **One** |
|---|---|---|
| **Parent** | `(i-1)//2` | `i//2` |
| **Left** | `2i+1` | `2i` |
| **Right** | `2i+2` | `2i+1` |

## Python Functions
```python3
# BASIC
int_num = ord('a') # get unicode value of char ("ordinal")
int_num = int('5') # convert char to int
//: floor division, 5/2 = 2, -5/2 = -3. Use 
float("inf") or math.inf (requires import math)


"string".isalnum()
"string".lower()


# ARRAY
min_num = min(A)
max_num = max(A)
total = sum(A)
any([True False True]) # True if any in iterable are True
all([i==5 for i in arr]) # True if all in iterable are True

for a,b in zip(A,B):
for idx,val in enumerate(A):


from itertools import chain
for val in chain(A,B,C) # iterate through A then B then C
for val in chain(*matrix) # iterate through 2d array row by row

# SORT
arr.sort() # sorts arr in place
arr.sort(reverse=True)
arr.sort(key=lambda item: item.val) # sort item obj by val field
arr.sort(key=lambda x: len(x)) # sort words by length

s_arr = sorted(arr) # does not modify arr
s_arr = sorted(arr,reverse=True)

# DICT
from collections import defaultdict
ht = defaultdict(int) (default is 0)
ht = defaultdict(list) (default is []), key must be a tuple: tuple([1,2,3])
ht = defaultdict(str) (default is "")
ht = defaultdict(lambda: "empty") # define custom default

if not ht[key]:
val = ht.get(key,0) // zero if not found in dict

# QUEUE
from collections import deque

queue = deque()
.append() - insert right
.popleft() - pop left
.appendleft() - insert left
.pop() - pop right
...................................

# SET
hashset = set()
hashset = set([1,2,3])

if x in hashset:
.add(x)
.remove(x)
.contains(x)

# HEAP
import heapq
heapq.heapify([1,2,3]) # create min heap O(n)
heapq.heappush(heap,4) # push to heap
val = heapq.heappop(heap) # pop from heap
arr = heapq.nsmallest(2,heap,key=lambda x: x[1])

# Faster algos
val = heapq.heappushpop(heap,4) # push item to heap THEN pop smallest item
val = heapq.heapreplace(heap,4) # pop smallest item THEN push new item

# Max heap added in Python 3.14
heapq.heapify_max()
heapq.heappush_max()
heapq.heappop_max()
heapq.heappushpop_max()
heapq.heapreplace_max()
```
