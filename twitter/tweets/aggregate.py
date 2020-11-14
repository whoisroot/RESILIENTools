import json
import csv
from os import listdir

"""
    Campos a serem removidos do arquivo final
"""
filtered_columns = [
    "created_at",
    "id",
    "conversation_id",
    "user_id",
    "username",
    "name",
    "place",
    "replies_count",
    "retweets_count",
    "likes_count",
    "hashtags",
    "cashtags",
    "quote_url",
    "video",
    "near",
    "geo",
    "source",
    "user_rt_id",
    "user_rt",
    "retweet_id",
]


"""
    Lê todos os arquivos com os tweets rotulados, previamente produzidos pelo rotulador, agrega-os e
    faz a remoção dos campos com informação inútil ao estudo ou que identifiquem os autores dos tweets
"""
def read_from_json(outfile):
    # Lista os arquivos na pasta que terminam em "tagged.json"
    files = [f for f in listdir() if f.endswith("tagged.json")]
    aggregated_items = []
    for f in files:
        print(f"Reading from file {f}...")
        items = json.load(open(f))
        print(f"Got {len(items)} in file {f}.")
        for i in items:
            filtered = {
                key: value for key, value in i.items() if key not in filtered_columns
            }
            # Há um grande numero de falsos positivos para alertas de enchente em portugal
            if not (
                "portugal" in filtered["tweet"].lower()
                or "portugal" in filtered["link"].lower()
            ):
                aggregated_items.append(filtered)
        print(f"File {f} is done.")
    json.dump(aggregated_items, open(outfile, "w"))
    return aggregated_items

"""
    Converte o arquivo JSON original para o formato CSV, simplificando a representação dos dados
"""
def write_to_csv(infile, *, items=None):
    # Caso colunas não tenham sido especificadas, utiliza todas as presentes
    if not items:
        items = json.load(open(infile))
    rownames = items[0].keys()
    with open("aggregated_tagged.csv", "w") as f:
        writer = csv.DictWriter(f, fieldnames=rownames)
        writer.writeheader()
        writer.writerows(items)
    print("Finished writing items to CSV file.")


"""
    Definição de função para permitir que o arquivo seja executado independentemente
    ou importado como módulo em outro programa que deseja utilizar suas funções
"""
def main():
    aggregate_file = "aggregated.json"

    aggregated = read_from_json(aggregate_file)
    write_to_csv(aggregate_file, items=aggregated)


if __name__ == "__main__":
    main()
