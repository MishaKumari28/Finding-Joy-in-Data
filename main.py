import pandas as pd
import seaborn as sb
import matplotlib.pyplot as plt
import streamlit as st

df=pd.read_csv("newdata.csv")
df.fillna(0, inplace=True)


df.drop(columns=["Region","Offline_School_Enrollment(%)","Online_Education_Access(%)"], inplace=True)
df.to_csv("cleandata.csv",index=False)

print("cleacned data")


print(df.columns.tolist())