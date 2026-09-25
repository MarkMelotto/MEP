'''it is important to not calculate z/h=0,-5 and +5 || plus you have to put the data in the startindex+2 zone!'''

def print_tecplot(start_index, end_index, name_of_average, name_variable):

    # z_is_0 = ((end_index-start_index)/2)+start_index
    # counter = 0
    #
    # equation = '{' + name_of_average + '} = ('
    #
    # for i in range(start_index, end_index+1):
    #     if i != z_is_0:
    #         counter += 1
    #         equation += '{'+name_variable + '}' + f'[{i}]'
    #         if i == end_index:
    #             equation += f')/{str(counter)}'
    #         else:
    #             equation += ' + '
    #
    # print(equation)

    z_is_0 = ((end_index-start_index)/2)+start_index
    counter = 0

    equation = '{' + name_of_average + '} = ('

    for i in range(start_index, end_index+1):
        if i != z_is_0:
            if i not in list_of_non_index:
                equation += '{'+name_variable + '}' + f'[{i}]'
                counter += 1
                if i == end_index or i == 656:
                    equation += f')/{str(counter)}'
                else:
                    equation += ' + '
    if equation[-2] == '+':
        equation = equation[:-3]
        equation += f')/{str(counter)}'

    print(equation)

# start_index = 14849
end_index_start = 312

# xh = ["x/h=0", "x/h=2", "x/h=4", "x/h=10"]
xh = ["x/h=2", "x/h=4", "x/h=10"]
xh = xh[::-1]


list_of_non_index = []

'''LES c'''
# list_of_non_index += range(58, 59+1)
# list_of_non_index += range(139, 252+1)
# list_of_non_index += [622]
# print(list_of_non_index)


for i in range(len(xh)):
    # if i in [0,1,2]:
    #     end_index = end_index_start - i * 101
    #     start_index = end_index - 100
    # else:
    end_index = end_index_start - i*103
    start_index = end_index - 102

    print(f"--------------{xh[i]}-------------------------")
    name_of_average = 'u_avg_z'
    name_variable = 'normalized_u'

    print_tecplot(start_index, end_index, name_of_average, name_variable)

    name_of_average = 'k_t_avg_z'
    name_variable = 'k'

    print_tecplot(start_index, end_index, name_of_average, name_variable)

    # name_of_average = 'sst tke_avg_z'
    # name_variable = 'Turbulent Kinetic Energy'
    #
    # print_tecplot(start_index, end_index, name_of_average, name_variable)

    name_of_average = 'theta_avg_z'
    name_variable = 'theta'

    print_tecplot(start_index, end_index, name_of_average, name_variable)


    name_of_average = 'theta_rms_avg_z'
    name_variable = 'theta_rms'

    print_tecplot(start_index, end_index, name_of_average, name_variable)
    #
    name_of_average = 'u_theta_avg_z'
    name_variable = 'u_theta'

    print_tecplot(start_index, end_index, name_of_average, name_variable)

    name_of_average = 'v_theta_avg_z'
    name_variable = 'v_theta'

    print_tecplot(start_index, end_index, name_of_average, name_variable)

    name_of_average = 'uv_avg_z'
    name_variable = 'uv'

    print_tecplot(start_index, end_index, name_of_average, name_variable)

    name_of_average = 'k_res_avg_z'
    name_variable = 'k_res'

    print_tecplot(start_index, end_index, name_of_average, name_variable)

    name_of_average = 'TKE_avg_z'
    name_variable = 'TKE'

    print_tecplot(start_index, end_index, name_of_average, name_variable)

    name_of_average = 'k_RANS_avg_z'
    name_variable = 'k_RANS'

    print_tecplot(start_index, end_index, name_of_average, name_variable)

    # name_of_average = 'k_sgs_avg_z'
    # name_variable = 'k_SGS'
    #
    # print_tecplot(start_index, end_index, name_of_average, name_variable)
    #
    # name_of_average = 'k_DDES_SST_avg_z'
    # name_variable = 'k_DES_SST'
    #
    # print_tecplot(start_index, end_index, name_of_average, name_variable)

    print(f"\n------------^-------------^--------------")