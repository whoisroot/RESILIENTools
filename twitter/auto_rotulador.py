import sys
import json
from os import path, stat


class AutoTagger:
    def __init__(self, infile, outfile, tag_file):
        self.infile = infile
        self.outfile = outfile
        self.tag_file = tag_file
        try:
            tags = json.load(open(self.tag_file))
            if not tags:
                print("Tag file is empty, exitting...")
                exit(0)
            self.tags = tags
            print(f"Loaded tags: {self.tags}\n\n\n")
        except FileNotFoundError:
            print(f"Tags file {tag_file} not found.")
            exit(0)

    def run(self):
        try:
            tweets = json.load(open(self.infile))
        except FileNotFoundError:
            print(
                "O arquivo não existe.\n"
                "Por favor, verifique se o arquivo existe ou se não digitou errado "
                "antes de tentar novamente."
            )
            exit(0)

        if path.exists(self.outfile):
            if stat(self.outfile).st_size > 0:
                tagged = json.load(open(self.outfile))
            else:
                tagged = []
        else:
            tagged = []

        self.tag(tweets, self.tags, tagged)
        self.save_tweets(tagged, tweets)

    def tag(self, tweets, tags, tagged):
        total = len(tweets)
        current = 0
        try:
            for i in range(0, len(tweets)):
                tweet = tweets.pop()
                tweet["tweet"] = self.normalize_tweet(tweet)
                applied_tags = [t for t in tags if t in tweet["tweet"].lower()]
                tweet["relevante"] = any(applied_tags)
                tweet["palavras_chave"] = applied_tags
                tagged.append(tweet)

                if i % 500 == 0:
                    print("\033[A                             \033[A")
                    print(f"Tagged: {current}/{total}")
                    self.save_tweets(tagged, tweets)
                current += 1

            print("\033[A                             \033[A")
            print(f"Tagged: {current}/{total}")
            self.save_tweets(tagged, tweets)

            if not tweets:
                print("Tagging completed.")
                print(
                    f"Relevant tweets: {len([t for t in tagged if t['relevante']])}/{len(tagged)}"
                )
                print(f"Irrelevant tweets: {[t['tweet'] for t in tagged if not t['relevante']]}")
            return

        except KeyboardInterrupt:
            print("Encerrando programa...\n")
            print("Salvando tweets rotulados...\n")
            tweets.append(tweet)
            self.save_tweets(tagged, tweets)
            print("Salvos!\n")
            exit(0)

    def normalize_tweet(self, tweet):
        """Add more normalization rules as needed."""
        tweet["tweet"] = tweet["tweet"].lower().replace("inundacao", "inundação")
        return tweet["tweet"]

    def save_tweets(self, tagged, left):
        json.dump(tagged, open(self.outfile, "w"))
        json.dump(left, open(self.infile, "w"))


if __name__ == "__main__":
    tag_file = "./palavras_chave.json"
    if len(sys.argv) < 2:
        print(f"\nUso: {sys.argv[0]} arquivo_com_tweets.json [arquivo_com_tags.json]\n")
        exit(0)
    elif len(sys.argv) == 3:
        tag_file = sys.argv[2]
    input_file = sys.argv[1]
    name = input_file.split("/")[-1].split(".")
    result_file = name[0] + "_tagged.json"

    tagger = AutoTagger(input_file, result_file, tag_file)
    tagger.run()
