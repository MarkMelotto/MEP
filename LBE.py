


def get_dx(number_of_elements):
    h = 1.5e-3
    length = 30
    length_in_h = length*h  # meters

    return length_in_h/number_of_elements

dx = get_dx(240)

def get_highest_dt(dx):
    rho = 10427.35705
    c_p = 146.53482780433583
    lamda = 10.6976665936375
    return (rho*c_p*dx**2)/(2*lamda)

print(get_highest_dt(dx))