#!/usr/bin/env python3

# Use the statistics CSV file and generate diagrams
#
#

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

part_ranking = ["preface", "background", "planning", "programming", "testing", "tools", "bolt_on", "offense", "appendix"]

sns.set(style="whitegrid")

dta = pd.read_csv("totalstats.csv", sep=";")

f, ax = plt.subplots(figsize=(6.5, 6.5))
ax.set_title("Detailed view")
sns.despine(f, left=True, bottom=True)
sns.scatterplot(x="part", y="words", size="level", hue="todos", data=dta, ax=ax)
plt.show()
print("-- dta")
print(dta)

# Summing up

print(dta.describe())
#print(dta.groupby("part").size())  # Number of chapters in each part

dtasum = dta.groupby("part").sum().reset_index() # Total number of words in each part
dtasum.insert(0, "chapters", dta.groupby("part").size())

print("-- dtasum")
print(dtasum)

f, ax = plt.subplots(figsize=(6.5, 6.5))
ax.set_title("Summary by part")
sns.despine(f, left=True, bottom=True)
sns.scatterplot(x="part", y="words", hue="todos", data=dtasum, ax=ax)
plt.show()
