
import pandas as pd
import matplotlib.pyplot as plt

try:
    # Carica i dati dal file CSV
    df = pd.read_csv("error_analysis.csv")

    # Conta le occorrenze di ogni categoria di errore
    error_counts = df["Categoria_Errore"].value_counts()

    # Calcola le percentuali
    error_percentages = df["Categoria_Errore"].value_counts(normalize=True) * 100

    # Crea un DataFrame per una bella visualizzazione
    results_df = pd.DataFrame({'Conteggio': error_counts, 'Percentuale': error_percentages.round(2)})

    print("--- Analisi degli Errori ---")
    print(results_df)
    print("\n--- Tabella LaTeX da copiare nel paper ---")
    print(results_df.to_latex())

    # Bonus: Crea un grafico a barre
    fig, ax = plt.subplots()
    results_df['Conteggio'].plot(kind='bar', ax=ax)
    ax.set_title('Distribuzione delle Categorie di Errore')
    ax.set_ylabel('Numero di Occorrenze')
    ax.set_xlabel('Categoria di Errore')
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig("error_distribution.png")
    print("\nGrafico a barre salvato come error_distribution.png")

except FileNotFoundError:
    print("Errore: Il file 'error_analysis.csv' non è stato trovato.")
    print("Assicurati di aver creato il file e di eseguire lo script dalla stessa directory.")

