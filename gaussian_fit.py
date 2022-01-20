import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from numpy import asarray, exp, sum

def gaus(x, a, x0, sigma):
    return a * exp(-(x - x0) ** 2 / (2 * sigma ** 2))

# # y = asarray([12, 21, 31, 40, 43, 40, 31, 21, 12]) / 256
# # y = asarray([4, 6, 8, 10, 13, 15, 18, 19, 21, 21, 21, 19, 18, 15, 13, 10, 8, 6, 4]) / 256
# y = asarray([13, 62, 103, 62, 13]) / 256
# # y = asarray([0,1,2,3,4,5,4,3,2,1])
# n = len(y)  # the number of data
# x = asarray(range(n))
# mean = sum(x * y) / n  # note this correction
# sigma = sum(y * (x - mean) ** 2) / n  # note this correction
#
#

#3
#
# popt, pcov = curve_fit(gaus, x, y)
#
# plt.plot(x, y, 'b+:', label='data')
# plt.plot(x, gaus(x, *popt), 'ro:', label='fit')
# plt.legend()
# plt.title('Fig. 3 - Fit for Time Constant')
# plt.xlabel('Time (s)')
# plt.ylabel('Voltage (V)')
# plt.show()

n = 7
x = asarray(range(n))
y = []
for i in x:
    y.append(gaus(i, 0.1, int(n / 2), 2)*256)
y = asarray(y).astype(int)
s = sum(y)
y = (y * 256 / s).astype(int)
plt.plot(x, y, 'b+:', label='data')
plt.show()
pass
