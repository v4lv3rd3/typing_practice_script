## 1-Activate venv 

```shell
python3 -m venv .venv
source .venv/bin/activate
```
>[!Info]
>you can disable it with `deactivate`


## 2-Install requirements

```shell
pip install -p requirements.txt
```

## 3-Add words on the words.txt file to practice

`nvim words.txt` or use the script menu

>[!Warning] 
>The words to the test are inside the `words.txt` and the statistics is stored on `typing_records.db`

>[!Tip] 
>Modify `repetitions_per_word` var in function main() to change the number of times to write each word
