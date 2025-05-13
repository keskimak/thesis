import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO

# Sample data extracted from the PDF
data = """
Laajuus,pvm
5,23.12.2021
3,14.09.2022
5,11.04.2022
3,03.12.2021
2,12.12.2022
3,09.12.2021
2,09.12.2021
2,25.08.2021
5,20.12.2021
4,31.08.2022
3,25.05.2022
4,20.05.2022
3,17.05.2022
3,31.03.2022
4,25.01.2022
2,15.08.2022
5,04.12.2021
5,14.12.2021
5,20.12.2021
5,10.12.2021
5,18.03.2022
5,23.03.2022
5,30.05.2022
5,30.05.2022
4,13.12.2022
3,15.05.2023
3,19.12.2022
5,19.12.2022
4,15.02.2023
4,28.08.2023
5,30.01.2024
4,13.09.2022
"""

# Read the data into a DataFrame
df = pd.read_csv(StringIO(data), parse_dates=['pvm'], dayfirst=True)

# Calculate cumulative sum of 'Laajuus'
df['cumulative_Laajuus'] = df['Laajuus'].cumsum()

# Plot the cumulative sum of 'Laajuus'
plt.figure(figsize=(10, 6))
plt.plot(df['pvm'], df['cumulative_Laajuus'], marker='o')
plt.xlabel('Date')
plt.ylabel('Cumulative Laajuus')
plt.title('Cumulative Laajuus Over Time')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()

# Save the plot as a PNG file
plt.savefig('cumulative_laajuus.png')

# Show the plot
plt.show()

