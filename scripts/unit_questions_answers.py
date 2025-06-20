import json

def combine_qa_to_json(questions_file: str, answers_file: str, output_file: str):
    """
    Combina perguntas e respostas de dois arquivos de texto em um dicionário
    e salva o resultado em um arquivo JSON.

    Args:
        questions_file (str): O caminho para o arquivo de perguntas.
        answers_file (str): O caminho para o arquivo de respostas.
        output_file (str): O caminho para o arquivo JSON de saída.
    """
    qa_data = {} # Inicializa o dicionário que vai armazenar pergunta: resposta

    try:
        with open(questions_file, 'r', encoding='utf-8') as q_file, \
             open(answers_file, 'r', encoding='utf-8') as a_file:

            questions = q_file.readlines()
            answers = a_file.readlines()

            # Garante que temos o mesmo número de perguntas e respostas
            if len(questions) != len(answers):
                print("Atenção: O número de perguntas e respostas não coincide!")
                # Você pode optar por levantar um erro ou continuar com o menor número
                min_lines = min(len(questions), len(answers))
                questions = questions[:min_lines]
                answers = answers[:min_lines]

            # Itera sobre as linhas e associa pergunta com resposta
            for i in range(len(questions)):
                question = questions[i].strip() # Remove espaços em branco e quebras de linha
                answer = answers[i].strip()     # Remove espaços em branco e quebras de linha
                qa_data[question] = answer

        # Salva o dicionário em um arquivo JSON
        with open(output_file, 'w', encoding='utf-8') as json_file:
            json.dump(qa_data, json_file, indent=4, ensure_ascii=False)
        
        print(f"Dados combinados salvos com sucesso em '{output_file}'")

    except FileNotFoundError:
        print("Erro: Um dos arquivos não foi encontrado. Verifique os caminhos.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

if __name__ == "__main__":
    # Chama a função para combinar e salvar
    combine_qa_to_json(r'C:\Users\fuedj\Documents\Code\RAG_Dr_Voss_v2\drvossv2\data\questions.txt', r'C:\Users\fuedj\Documents\Code\RAG_Dr_Voss_v2\drvossv2\data\answers.txt', r'C:\Users\fuedj\Documents\Code\RAG_Dr_Voss_v2\drvossv2\data\unit_qa.json')
