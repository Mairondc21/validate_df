import pandas as pd
import pandera as pa
from contrato import MetricaFinanceiraBase, MetricaFinanceiraOut
from datetime import datetime
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine


def extrai_dados(dir_arquivo: str) -> pd.DataFrame:
    df = pd.read_csv(dir_arquivo)

    try:
        MetricaFinanceiraBase.validate(df, lazy=True)
        return df
    except pa.errors.SchemaError as exec:
        print("Error ao validar")
        print(exec)

@pa.check_output(MetricaFinanceiraOut)
def transforma_dados(df: pd.DataFrame) -> pd.DataFrame:
    df_transformado = df.copy()
    df_transformado["valor_do_imposto"] = df_transformado["percentual_de_imposto"] * df_transformado["receita_operacional"]
    df_transformado["custo_total"] = df_transformado["valor_do_imposto"] + df_transformado["custos_operacionais"]
    df_transformado["receita_liquida"] = df_transformado["receita_operacional"] - df_transformado["custo_total"]
    df_transformado["margem_operacional"] = (df_transformado["receita_liquida"] / df_transformado["receita_operacional"]) 
    df_transformado["transformado_em"] = datetime.now()

    return df_transformado

def carga_dados(df: pd.DataFrame) -> None:
    load_dotenv(".env")

    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT")
    POSTGRES_DB = os.getenv("POSTGRES_DB")

    POSTGRES_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

    engine = create_engine(POSTGRES_DATABASE_URL)

    nome_da_tabela = "metricas_financeiras" 
    try:
        df.to_sql(nome_da_tabela, engine, if_exists= "replace", index = False)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    dir_arquivo = "data/dados_financeiros.csv"
    df = extrai_dados(dir_arquivo)
    df_trasformado = transforma_dados(df)
    carga_dados(df_trasformado)
    print(carga_dados) 