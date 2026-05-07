def monotonic_scaffold(arr):
    stack = []

    output = len(arr) * [-1]

    for i in range(len(arr)):

        # while stack and top_of_stack OPERATOR arr[i]:
        while stack and arr[stack[-1]] < arr[i]:

            top = stack.pop()

            # do something with top here
            # next_greater_index[top] = i

        if len(stack):
            # if stack has some elements left
            # do something with top here
            # previous_greater_index[i] = stack[-1]
            pass

        # push current index to stack
        stack.append(i)

    return next_greater_index

def print_monotonic(i,arr,stack,out_index):

    stack_print = [arr[stack[i]] for i in range(len(stack))]

    out_index_print = [arr[out_index[i]] if out_index[i] > -1 else None for i in range(len(out_index))]
    print(f"Element: {arr[i]}, Stack: {stack_print}, Output: {out_index_print}")



def next_greater_index(arr):
    stack = []

    out_index = len(arr) * [-1]

    for i in range(len(arr)):

        while stack and arr[stack[-1]] < arr[i]:  # < operator

            print_monotonic(i,arr,stack,out_index)

            top_index = stack.pop()
            out_index[top_index] = i  # assign in while loop

        print_monotonic(i,arr,stack,out_index)

        # no conditional

        stack.append(i)
        print_monotonic(i,arr,stack,out_index)

    return out_index


def prev_greater_index(arr):
    stack = []

    out_index = len(arr) * [-1]

    for i in range(len(arr)):

        while stack and arr[stack[-1]] <= arr[i]:  # <= operator

            print_monotonic(i,arr,stack,out_index)

            stack.pop()
            # don't assign in while loop

        if stack:  # conditional
            out_index[i] = stack[-1]  # assign outside while loop
        print_monotonic(i,arr,stack,out_index)

        stack.append(i)
        print_monotonic(i,arr,stack,out_index)

    return out_index

# input = [13, 8, 1, 5, 2, 5, 9, 7, 6, 12]
input = [1,2,3,1]
print(f"Input: {input}")
# print(next_greater_index(input))
print(prev_greater_index(input))

# Problem      | Stack Type        | Operator in while loop | Assignment Position
# next greater | decreasing        | stack_top < current    | inside while loop
# next smaller | increasing        | stack_top > current    | inside while loop
# prev greater | decreasing strict | stack_top <= current   | outside while loop
# prev smaller | increasing strict | stack_top >= current   | outside while loop
