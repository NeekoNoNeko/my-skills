import pandas as pd

df = pd.read_excel('d:/workspace/test/四级真题核心词.xlsx')
print('known column dtype:', df['known'].dtype)
print('known unique values:', df['known'].unique())
print('known value at row 0:', repr(df['known'].iloc[0]))
print()

# Check if words in the JSON list exist in the Excel
word_list = ['alcohol', 'variety', 'civilized', 'launch', 'primary', 'adapt', 'content', 'plastic', 'pose', 'project']
for w in word_list:
    exists = w in df['单词'].values
    if exists:
        idx = df[df['单词'] == w].index[0]
        print(f'  {w}: FOUND at row {idx}, known={df.loc[idx, "known"]}')
    else:
        print(f'  {w}: NOT FOUND')
