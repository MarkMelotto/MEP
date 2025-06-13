start_string_eta = "{l_c_over_eta_avg} = ("
start_string_corsin = "{l_c_corsin_avg} = ("
number_slices = 10
start_index = 11
start_index = 4174
counter_1 = 0
counter_2 = 0
for i in range(number_slices+1):
    if i == number_slices - 1 + 1:
        start_string_eta += ("{"
                             f"l_c_over_eta"
                             "}"
                             f"[{start_index + i + 1}] ")
        counter_1 += 1
    elif i == number_slices/2:
        continue
    else:
        start_string_eta += ("{"
                             f"l_c_over_eta"
                             "}"
                             f"[{start_index + i + 1}] + ")
        counter_1 += 1
start_string_eta += ")/" + str(counter_1)
print(start_string_eta)
# print(counter_1)


print('\n')
for i in range(number_slices + 1):
    if i == number_slices - 1 + 1:
        start_string_corsin += ("{"
                             f"l_c_corsin"
                             "}"
                             f"[{start_index + i + 1}] ")
        counter_2 += 1

    elif i == number_slices / 2:
        continue
    else:
        start_string_corsin += ("{"
                             f"l_c_corsin"
                             "}"
                             f"[{start_index + i + 1}] + ")
        counter_2 += 1
start_string_corsin += ")/" + str(counter_2)
print(start_string_corsin)