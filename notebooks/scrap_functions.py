beans = [[1,2,3],[1,2,3],[1,1,2],[2,6,12],[2,5,12],[2,4,3],[2,4,3],[2,3,6],[2,2,9],[3,11,12]]

filtered_beans = []

# Initialize a dictionary to group data by the first index
grouped_beans = {}

for x in beans:
    index0 = x[0]
    index1 = x[1]
    index2 = x[2]
    
    # If the group for index0 doesn't exist, create it
    if index0 not in grouped_beans:
        grouped_beans[index0] = [[], []]  # Initialize lists for index1 and index2
    
    # Check if the current index1 is the same as the last added index1 for this group
    if grouped_beans[index0][0] and index1 == grouped_beans[index0][0][-1]:
        continue  # Skip this iteration if index1 is the same as the previous one
    
    # Add index1 and index2 to their respective lists
    grouped_beans[index0][0].append(index1)
    grouped_beans[index0][1].append(index2)

# Convert the grouped dictionary into the desired list format
for key, value in grouped_beans.items():
    filtered_beans.append([key, value[0], value[1]])

print(filtered_beans)
# [[1, [2, 1], [3, 2]], [2, [6, 5, 4, 3, 2], [12, 12, 3, 6, 9]], [3, [11], [12]]]