'''it is important to not calculate z/h=0,-5 and +5 || plus you have to put the data in the startindex+2 zone!'''

# start_index = 14849
end_index_start = 459
start_index = end_index_start-52
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
list_of_non_index = [436, 431, 430, 426, 424, 421, 420, 419, 418, 417, 416,
                     415, 414, 413, 410, 408, 404, 403, 398]
list_of_non_index = [x + 11 - 100 +53+53 for x in list_of_non_index]
end_index = end_index_start

# xh9 part
# list_of_non_index = [498, 505, 510, 511, 515, 517, 520, 521, 522, 523, 524,
#                      525, 526, 527, 528, 531, 533, 537, 538]
# list_of_non_index = [x - 15 for x in list_of_non_index]

def printer_function(name_of_average, name_variable, normalizer):
    # z_is_0 = ((end_index-start_index)/2)+start_index+1
    # counter = 0
    #
    # equation = '{' + name_of_average + '} = ('
    #
    # for i in range(start_index+2, end_index+1):
    #     if i != z_is_0:
    #         if i not in list_of_non_index:
    #             equation += '{'+name_variable + '}' + f'[{i}]'
    #             counter += 1
    #             if i == end_index:
    #                 equation += f')/{str(counter)}'
    #             else:
    #                 equation += ' + '
    # if normalizer != 1:
    #     equation += "/(" + str(normalizer) + ")"
    # print(equation)

    # this part is for F'ed xh13
    counter = 0

    equation = '{' + name_of_average + '} = ('

    for i in [467, 468, 471, 472, 474]:


        equation += '{' + name_variable + '}' + f'[{i}]'
        counter += 1
        if i == 474:
            equation += f')/{str(counter)}'
        else:
            equation += ' + '
    if normalizer != 1:
        equation += "/(" + str(normalizer) + ")"
    print(equation)

xh = ["x/h=1", "x/h=5", "x/h=9", "x/h=13"]
xh = xh[::-1]




# print(f"--------------{xh[i]}-------------------------")
name_variable = 'normalized_x-velocity'
name_of_average = 'avg_normU'
printer_function(name_of_average, name_variable, nothing)



name_variable = 'u_fluc'
name_of_average = 'avg_fluc_u_norm'
printer_function(name_of_average, name_variable, u_j)


name_variable = 'k_res'
name_of_average = 'avg_k_res_norm'
printer_function(name_of_average, name_variable, u_j**2)


name_variable = 'normalized_temp'
name_of_average = 'avg_T_norm'
printer_function(name_of_average, name_variable, nothing)


name_variable = 'theta'
name_of_average = 'avg_theta_norm'
printer_function(name_of_average, name_variable, t_h_min_t_c)

'''if (D)DES or LES'''

name_variable = 'uv'
name_of_average = 'avg_uv_norm'
printer_function(name_of_average, name_variable, u_j**2)


name_variable = 'theta_fluc'
name_of_average = 'avg_theta_v_norm'
printer_function(name_of_average, name_variable, u_j*t_h_min_t_c)

print(f"\n------------^-------------^--------------")


