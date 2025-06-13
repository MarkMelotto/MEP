'''it is important to not calculate z/h=0,-5 and +5 || plus you have to put the data in the startindex+2 zone!'''

# start_index = 14849
end_index_start = 676
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
xh = ["x/h=1", "x/h=5", "x/h=9", "x/h=13"]

def printer_function(start, list_name_variable):
    count = 0
    for name_variable in list_name_variable:
        for i in range(4):
            equation_1 = '{boussi - noG ' + xh[i] + ' ' + list_name_variable[count] + '} = '
            equation_2 = '{TB - noG ' + xh[i]  + ' ' + list_name_variable[count] + '} = '

            equation_1 += '{'+name_variable + '}' + f'[{start+i+4}]' + ' - {'+name_variable + '}' + f'[{i+start}]'
            # equation_1 += '{'+name_variable + '}' + f'[{start+i-4}]' + ' - {'+name_variable + '}' + f'[{i+start}]'
            # equation_2 += '{'+name_variable + '}' + f'[{start+i+4}]' + ' - {'+name_variable + '}' + f'[{i+start}]'
            equation_2 += '{'+name_variable + '}' + f'[{start+i+8}]' + ' - {'+name_variable + '}' + f'[{i+start}]'

            print(equation_1)
            print(equation_2)
        print("\n")
        count += 1

# xh = ["x/h=1", "x/h=5", "x/h=9", "x/h=13"]
# xh = xh[::-1]



start = 30

# print(f"--------------{xh[i]}-------------------------")
name_variable_1 = 'avg_normU'

name_variable_2 = 'avg_fluc_u_norm'

name_variable_3 = 'avg_k_res_norm'

name_variable_4 = 'avg_uv_norm'  # only LES DDES

name_variable_5 = 'avg_T_norm'

name_variable_6 = 'avg_theta_norm'

name_variable_7 = 'avg_theta_v_norm'  # only LES DDES

# RANS BOYS
list_name_variables = [name_variable_1, name_variable_2, name_variable_3, name_variable_5, name_variable_6]

# REST
list_name_variables = [ name_variable_4, name_variable_7]

printer_function(start, list_name_variables)

