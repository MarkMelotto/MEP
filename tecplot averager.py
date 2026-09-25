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

def printer_function(name_of_average, name_variable, normalizer):
    z_is_0 = ((end_index-start_index)/2)+start_index+1

    equation = '{' + name_of_average + '} = ('

    for i in range(start_index+2, end_index+1):
        if i != z_is_0:
            equation += '{'+name_variable + '}' + f'[{i}]'
            if i == end_index:
                equation += f')/{str(end_index-start_index-3)}'
            else:
                equation += ' + '
    if normalizer != 1:
        equation += "/(" + str(normalizer) + ")"
    print(equation)

xh = ["x/h=1", "x/h=5", "x/h=9", "x/h=13"]
xh = xh[::-1]


for i in range(4):
    end_index = end_index_start - i*103
    start_index = end_index - 102

    print(f"--------------{xh[i]}-------------------------")
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


