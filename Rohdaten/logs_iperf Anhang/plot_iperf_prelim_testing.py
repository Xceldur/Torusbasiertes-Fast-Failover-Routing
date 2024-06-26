import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

# manual entry's of datepoints form logs
full_duplex = [(1, 140),  (2,143),   (3, 144), (4, 137), (5, 143)]
singel_flow = [(1, 89,9), (2, 90.9), (3, 91.0), (4, 90.0), (5,90.0)]

data_to_plot = [('full duplex',int(x[0]),x[1]/200) for x in full_duplex] + [('simplex', int(x[0]),x[1]/100) for x in singel_flow]
data_pd = pd.DataFrame(columns=['flow', 'try', 'relative bandwidth usage'], data=data_to_plot)


sns.pointplot(data=data_pd, hue='flow', x='try', y='relative bandwidth usage')
plt.savefig('plot_iperf_prelim_testing_full_duplex.pdf')
plt.show()