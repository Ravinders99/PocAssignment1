import pandas as pd
import matplotlib.pyplot as plt

# Function to read CSV and generate boxplot
def plot_boxplot(filename, title):
    """Read the CSV file and plot a box plot."""
    # Load the CSV file into a DataFrame
    df = pd.read_csv(filename)

    # Plot the boxplot
    plt.figure(figsize=(8, 6))
    plt.boxplot(df['Duration (ms)'])
    plt.title(title)
    plt.ylabel("End-to-End Delay (ms)")
    plt.xlabel("Runs")
    plt.show()


def main():
    # Plot for each query
    plot_boxplot("category_query_durations.csv", "Category Query Durations (Physics, 2013-2023)")
    plot_boxplot("keyword_query_durations.csv", "Keyword Query Durations (Keyword: 'peace')")
    plot_boxplot("details_query_durations.csv", "Details Query Durations (Firstname: 'Alice', Surname: 'Munro')")


if __name__ == "__main__":
    main()
