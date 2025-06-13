'''it is important to not calculate z/h=0,-5 and +5 || plus you have to put the data in the startindex+2 zone!'''

# start_index = 14849
# start_index = end_index_start-102
# name_of_average = 'temp_avg_z'
# name_variable = 'normalized_temp'
#
# name_of_average = 'xvel_avg_z'
# name_variable = 'normalized_x-velocity'

# name_of_average = 'theta_avg_z'
# name_variable = 'k_theta'
u_j = 0.51
t_h_min_t_c = 620.7 - 577.5
nothing = 1

def printer_function(name_of_average, name_variable, normalizer):
    z_is_0 = ((end_index - start_index) / 2) + start_index + 1
    counter = 0

    equation = '{' + name_of_average + '} = ('

    for i in range(start_index+2, end_index+1):

        if i not in list_of_non_index:
            equation += '{'+name_variable + '}' + f'[{i}]'
            counter += 1
            # print(i)
            if i == new_end_index:
                equation += f')/{str(counter)}'
                break
            else:
                equation += ' + '
    if normalizer != 1:
        equation += "/(" + str(normalizer) + ")"
    print(equation)


end_index = 26711
start_index = end_index - 102
new_end_index = 26701

list_of_non_index = [0, 2, 3, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 80, 81,
                     82, 83, 84, 85, 86, 87, 88, 89, 90, 93, 94, 95,
                     96, 97, 98, 99, 100, 101, 102]
list_of_non_index = [x + start_index for x in list_of_non_index]
# print(list_of_non_index)

name_variable = 'normalized_x-velocity'
name_of_average = 'avg_normU'
printer_function(name_of_average, name_variable, nothing)



name_variable = 'normalized_temp'
name_of_average = 'avg_T_norm'
printer_function(name_of_average, name_variable, nothing)




