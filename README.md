# GeneticTabler
Time Table Scheduling done using [genetic algorithms](https://en.wikipedia.org/wiki/Genetic_algorithm) with a lot of logic and optimisations to achieve multiple tables at the same time.

Developed by Dipan Nanda and Ashish Shah (c) 2021

## Examples of Usage

```python
from genetic import fill_timetable

total_classes = 4
no_courses = 8
slots = 6
total_days = 7
daily_repetition = 3

table = fill_timetable(
    total_classes,
    no_courses,
    slots,
    total_days,
    daily_repetition,
)

for i in table:
    for j in i:
        print(j)
    print("-----------------------------------")
```
