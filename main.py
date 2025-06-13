import numpy as np


def Re(U, T):
    H = 0.02
    v = np.exp(-6.4406 - 0.3958 * np.log(T) + 556.835 / T)
    v = v / (219 + 275.32 * (1 - T / 2503.7) + 511.58 * (1 - T / 2503.7) ** 0.5)
    # print(f"{v = }")
    return U * H / v


def Gr(dT, T):
    g = 9.81
    beta = 0.000226
    H = 0.02
    v = np.exp(-6.4406 - 0.3958 * np.log(T) + 556.835 / T) / 1000
    return g * beta * dT * H ** 3 / v ** 2


def Re_lbe(U, T):
    H = 0.015
    rho = 11065 - 1.293 * T
    mu = 4.94e-4 * np.exp(754.1 / T)
    v = mu / rho
    return U * H / v


def Gr_lbe(dT, T):
    g = 9.81
    beta = 1 / (8558 - T)
    H = 0.015
    rho = 11065 - 1.293 * T
    v = 4.94e-4 * np.exp(754.1 / T) / rho
    # v = 0.25e-6
    return (g * beta * dT * H ** 3) / v ** 2


def Ri_lbe(U, T, dT):
    Grashof = Gr_lbe(dT, T)
    reynolds = Re_lbe(U, T)
    return (Grashof / reynolds ** 2)


def Ri(U, T, dT):
    Grashof = Gr(dT, T)
    reynolds = Re(U, T)
    return (Grashof / reynolds ** 2)


# print(f"{Re_lbe(0.01, 347.7+273.15) = :.2e}")
#
# print(f"{Gr_lbe(72.7, 220+273.15) = :.2e}")
#
# print(f"{Ri(0.01, 347.7+273.15, 72.7) = :.2f}")
# print(f"{Re(0.51, 347.7+273.15)}")

cases_velocity = [0.2, 0.3, 0.34, 0.38, 0.51, 0.57, 0.7, 0.82, 1.01]
cases_temp = [342.7, 350.1, 349.5, 351.6, 347.7, 349.9, 344.7, 344.3, 340.8]

# for i in range(len(cases_velocity)):
#     print(f"Case {i+1}, v = {cases_velocity[i]}, T = {cases_temp[i]}")
#     reynolds = Re(cases_velocity[i], cases_temp[i]+273.15)
#     grashof = Gr(40, cases_temp[i]+273.15)
#     Richardson = Ri(cases_velocity[i], cases_temp[i]+273.15, 40)
#     print(f"Reynolds = {reynolds:.2e}")
#     print(f"Grashof = {grashof:.2e}")
#     print(f"Richardson = {Richardson:.3f}\n")
#
StaticTemperature = 220+273.15
# print(f"LBE c_p = {164.8 - 3.94e-2 * StaticTemperature + 1.25e-5 *StaticTemperature**2 - 4.56e5 *StaticTemperature**-2}")
# print(f"LBE rho = {11065 - 1.293 * StaticTemperature}")
# print(f"LBE TEC = {1/(8558-StaticTemperature)}")
# print(f"LBE thermal conductivity = {3.284 + 1.617e-2 * StaticTemperature -2.305e-6 * StaticTemperature**2}")
# print(f"LBE dynamic viscosity = {4.94e-4 * np.exp(754.1 * StaticTemperature**-1)}")


print(f"{Re_lbe(0.07288, StaticTemperature) = }")