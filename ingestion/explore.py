import pandas as pd

# # xls = pd.ExcelFile("ingestion/rpw_dataset_2011_2025_q1.xlsx")
# # print(xls.sheet_names)


# df_recent = pd.read_excel("ingestion/rpw_dataset_2011_2025_q1.xlsx", sheet_name="Dataset (from Q2 2016)")
# print(df_recent.shape)          # (nombre de lignes, nombre de colonnes)
# print(df_recent.columns.tolist())
# print(df_recent.head(3))

# senegal = df_recent[df_recent["destination_name"] == "Senegal"]
# print(senegal.shape)
# print(senegal["source_name"].unique())   # quels pays envoient vers le Sénégal ?


# # Sur quelle période s'étalent ces données ?
# print(senegal["period"].unique())

# # Quels opérateurs sont présents ?
# print(senegal["firm"].unique())

# # Quels moyens de paiement ?
# print(senegal["payment instrument"].unique())


# df_old = pd.read_excel("ingestion/rpw_dataset_2011_2025_q1.xlsx", sheet_name="Dataset (up to Q1 2016)")
# print(df_old.shape)
# print(df_old.columns.tolist())

# senegal_old = df_old[df_old["destination_name"] == "Senegal"]
# print(senegal_old.shape)
# print(senegal_old["period"].unique() if "period" in df_old.columns else "pas de colonne period")

# cols_recent = set(df_recent.columns)
# cols_old = set(df_old.columns)

# print("Colonnes uniquement dans la feuille récente :", cols_recent - cols_old)
# print("Colonnes uniquement dans l'ancienne feuille :", cols_old - cols_recent)


import pandas as pd

df_recent = pd.read_excel("ingestion/rpw_dataset_2011_2025_q1.xlsx", sheet_name="Dataset (from Q2 2016)")
df_old = pd.read_excel("ingestion/rpw_dataset_2011_2025_q1.xlsx", sheet_name="Dataset (up to Q1 2016)")

senegal = df_recent[df_recent["destination_name"] == "Senegal"]
senegal_old = df_old[df_old["destination_name"] == "Senegal"]

mapping = {
    "product": "payment instrument",
    "sending location": "access point",
    "coverage": "receiving network coverage",
    "note1": "Standard Note",
    "pick-up method": "pickup method",
}

senegal_old_renamed = senegal_old.rename(columns=mapping)
senegal_old_renamed["pickup location"] = None

df_senegal_all = pd.concat([senegal_old_renamed, senegal], ignore_index=True)

print(df_senegal_all.shape)
print(df_senegal_all["period"].nunique(), "trimestres au total")