import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import scipy.stats as stats
from scipy.stats import pearsonr, spearmanr, ttest_ind, mannwhitneyu, f_oneway
import matplotlib.pyplot as plt

# Carregar os dados
file_original = "/home_cerberus/disk3/larissa.gomide/APDDv2/APDDv2-10023.csv"
file_new = "/home_cerberus/disk3/larissa.gomide/updated_sampled_dataset.csv"
df_original = pd.read_csv(file_original, encoding="latin1")
df_new = pd.read_csv(file_new, encoding="utf-8")

# Colunas de interesse
cols_to_compare = [
    "Total aesthetic score", "Theme and logic", "Creativity", "Layout and composition",
    "Space and perspective", "The sense of order", "Light and shadow", "Color",
    "Details and texture", "The overall", "Mood"]

# Remover entradas completamente zeradas na nova base
df_new = df_new[~(df_new[cols_to_compare] == 0).all(axis=1)]

# Ajustar índices para garantir comparação correta
df_original = df_original.reset_index(drop=True)
df_new = df_new.reset_index(drop=True)

# Criar máscara para ignorar colunas ausentes na base original por "Artistic Categories"
for col in cols_to_compare:
    if col in df_original.columns and col in df_new.columns:
        mask = df_original[col].isna()
        df_new.loc[mask, col] = np.nan

results = {}
for col in cols_to_compare:
    if df_original[col].notna().sum() > 0:  # Apenas comparar se há valores na base original
        results[col] = stats.ttest_ind(
            df_original[col].dropna(), df_new[col].dropna(), equal_var=False, nan_policy='omit'
        )

#----- Testes de Hipótese -----
print("----- Testes de Hipótese -----")

# 1. Relação entre "The overall" e "Mood" nas duas bases
# Hipótese nula ((H_0)): Não há correlação significativa entre "The overall" e "Mood".
# Hipótese alternativa ((H_1)): Existe uma correlação significativa entre "The overall" e "Mood".
def correlation_analysis(df, dataset_name):
    df = df.dropna(subset=["The overall", "Mood"])
    pearson_corr, pearson_p = pearsonr(df["The overall"], df["Mood"])
    spearman_corr, spearman_p = spearmanr(df["The overall"], df["Mood"])
    print(f"{dataset_name} - Correlação de Pearson: {pearson_corr:.3f} (p={pearson_p:.3f})")
    print(f"{dataset_name} - Correlação de Spearman: {spearman_corr:.3f} (p={spearman_p:.3f})")

correlation_analysis(df_original, "Base Original")
correlation_analysis(df_new, "Nova Base")

# 2. As imagens foram avaliadas de maneira próxima nas duas bases?
# Hipótese nula ((H_0)): As médias das notas nas categorias são estatisticamente iguais nas duas bases.
# Hipótese alternativa ((H_1)): Há diferença significativa nas médias das notas entre as bases.
for col in cols_to_compare:
    orig_col = df_original[col].dropna()
    new_col = df_new[col].dropna()
    if len(orig_col) > 1 and len(new_col) > 1:
        t_stat, t_p = ttest_ind(orig_col, new_col, equal_var=False, nan_policy='omit')
        mw_stat, mw_p = mannwhitneyu(orig_col, new_col)
        print(f"{col} - Teste t: p={t_p:.3f}, Mann-Whitney U: p={mw_p:.3f}")

# 3. ANOVA para verificar diferenças significativas entre categorias
anova_p = f_oneway(*[df_new[col].dropna() for col in cols_to_compare if col in df_new.columns])[1]
print(f"ANOVA entre categorias na nova base: p={anova_p:.3f}")

#----- Visualizações -----
print("Visualizações")

# Selecionar a coluna "Total Aesthetic Score" das duas bases
col = "Total aesthetic score"
original_scores = df_original[col].dropna()
new_scores = df_new[col].dropna()

# Criar um DataFrame para visualização
df_scores = pd.DataFrame({
    "Total Aesthetic Score": np.concatenate([original_scores, new_scores]),
    "Base": ["Original"] * len(original_scores) + ["Nova"] * len(new_scores)
})

# Criar as visualizações com Plotly
fig1 = px.histogram(df_original[cols_to_compare].melt(), x="value", color="variable", title="Distribuição das Notas - Base Original")
fig2 = px.histogram(df_new[cols_to_compare].melt(), x="value", color="variable", title="Distribuição das Notas - Nova Base")

fig1.show()
fig2.show()

# Criar a figura com Matplotlib para os Boxplots e Histogramas
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Boxplot para comparação das distribuições
sns.boxplot(x="Base", y="Total Aesthetic Score", data=df_scores, ax=axes[0])
axes[0].set_title("Boxplot - Comparação do Total Aesthetic Score")

# Histograma para comparar distribuições
sns.histplot(original_scores, color="blue", label="Original", kde=True, alpha=0.5, ax=axes[1])
sns.histplot(new_scores, color="red", label="Nova", kde=True, alpha=0.5, ax=axes[1])
axes[1].set_title("Histograma - Distribuição do Total Aesthetic Score")
axes[1].legend()

plt.tight_layout()
plt.show()

# Correlação entre "The overall" e "Mood"
sns.scatterplot(data=df_original, x="The overall", y="Mood", alpha=0.5, label='Base Original')
sns.scatterplot(data=df_new, x="The overall", y="Mood", alpha=0.5, label='Nova Base')
plt.title("Relação entre 'The overall' e 'Mood'")
plt.legend()
plt.show()

# Cálculos das médias e medianas
original_mean = original_scores.mean()
new_mean = new_scores.mean()
original_median = original_scores.median()
new_median = new_scores.median()

print(f"Média Original: {original_mean:.3f}, Média Nova: {new_mean:.3f}")
print(f"Mediana Original: {original_median:.3f}, Mediana Nova: {new_median:.3f}")

# Gráfico de radar para comparar médias
cols_to_compare = [
     "Theme and logic", "Creativity", "Layout and composition",
    "Space and perspective", "Light and shadow", "Color",
    "Details and texture", "The overall", "Mood"]

orig_means = [df_original[col].mean() for col in cols_to_compare]
new_means = [df_new[col].mean() for col in cols_to_compare]

angles = np.linspace(0, 2 * np.pi, len(cols_to_compare), endpoint=False).tolist()
orig_means += orig_means[:1]
new_means += new_means[:1]
angles += angles[:1]

fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
ax.fill(angles, orig_means, color='b', alpha=0.25, label='Base Original')
ax.fill(angles, new_means, color='r', alpha=0.25, label='Nova Base')
ax.set_xticks(angles[:-1])
ax.set_xticklabels(cols_to_compare, fontsize=10)
plt.title("Comparação das Médias das Categorias")
plt.legend()
plt.show()

