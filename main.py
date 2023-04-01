import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

HERE = Path(__file__).parent
# print(HERE)

roster = pd.read_csv(
    HERE/'roster.csv',
    converters={'NetID': str.lower,
                'Email Address': str.lower,
                },
    usecols=['NetID', 'Email Address', 'Section'],
    index_col='NetID'
)

# print(roaster.head())

HwExGrades = pd.read_csv(
    HERE/'hw_exam_grades.csv',
    converters={'SID': str.lower},
    usecols=lambda x: 'Submission' not in x,
    index_col='SID'
)

# print(HwExGrades.head())

quiz_df = pd.DataFrame()
for i in HERE.glob('quiz_*_grades.csv'):
    path = str(i).split("_")[1]
    quiz = pd.read_csv(
        i,
        converters={
            'Email': str.lower
        },
        usecols={'Email', 'Grade'},
        index_col='Email'
    ).rename(columns={"Grade": f"Grade {path}"})
    quiz_df = pd.concat([quiz_df, quiz], axis=1)
# print(quiz_df)

finaldf = pd.merge(roster,
                   HwExGrades,
                   left_index=True,
                   right_index=True)

finaldf = pd.merge(finaldf, quiz_df, right_index=True, left_on="Email Address")

no_exams = 3
for a in range(1, no_exams+1):
    score = finaldf[f"Exam {a}"]/finaldf[f"Exam {a} - Max Points"]
    finaldf[f"Exam {a} - Score"] = score
# print(finaldf)

# 15 15 30 for exam
# 40% for homework

hw_score = finaldf.filter(regex=r"^Homework \d\d?$", axis=1)
hw_max = finaldf.filter(regex=r"^Homework \d\d? -", axis=1)


sum_hw_scores = hw_score.sum(axis=1)
sum_hw_max = hw_max.sum(axis=1)
sum = sum_hw_scores/sum_hw_max
# sum = sum * 100
finaldf["Score for Homeworks"] = sum

quiz_score = finaldf.filter(regex=r"^Grade \d?$", axis=1)
quiz_max_points = pd.Series(
    {"Quiz 1": 11, "Quiz 2": 15, "Quiz 3": 17, "Quiz 4": 14, "Quiz 5": 12}
)
quiz_sum = quiz_score.sum(axis=1)
# quiz_max_sum = quiz_max_points.sum()
quiz_sum_final = quiz_sum/69
# quiz_sum_final = quiz_sum_final*100

finaldf["Percentage for Quiz"] = quiz_sum_final


weightings = pd.Series(
    {
        "Exam 1 - Score": 5,
        "Exam 2 - Score": 10,
        "Exam 3 - Score": 15,
        "Percentage for Quiz": 30,
        "Score for Homeworks": 40,

    }
)


a = (finaldf[weightings.index] * weightings).sum(axis=1)
gradecat = {
    80: "A*",
    70: "A",
    60: "B",
    50: "C",
    40: "D",
    30: "E",
    0: "F"
}

finaldf['final Score'] = (finaldf[weightings.index] * weightings).sum(axis=1)

# var = finaldf['final Score']
# var.plot.bar()
# plt.show()

finalmean = finaldf["final Score"].plot.hist(bins=20, label="grades")
print(finaldf)
plt.show()
