def assets_p1test(ALUNO):
    p1t_dialogue = [
    '<P1-TEST> Alô, quem é?',
    f'<{ALUNO}> Ah oi! Eu estou preso nesse corredor e não sei como sair. Eu sou um aluno de p1.',
    '<P1-TEST> P1? Agora tudo faz sentido. Deixe-me te explicar: EU SOU O P1-TEST. EU VEJO TUDO E DE MIM TU TEMES. POR SER FRACO E MEDROSO, TU SE ENCONTRAS PRESO NESTE CORREDOR.',
    f'<{ALUNO}> Ah não! Estou diante de forças terríveis além da compreensão humana.',
    '<P1-TEST> MAS AINDA HÁ ESPERAÇAS PARA TI, POBRE ALMA. NESTE LOCAL MACABRO, TU PODERÁS ENCONTRAR MINHA MAIOR FRAQUEZA SE TIVERDES SABEDORIA. CASO CONSIGA, BASTA ME DIZER E TE DEIXAREI PASSAR PELA PORTA.',
    f'<{ALUNO}> Calma ai! Como assim? Só abre a porta ai na moral.',
    '<P1-TEST> ENCONTRE A RESPOSTA.']
    return p1t_dialogue

def assets_sun(ALUNO):
    sun_boot = [
    'sunOS 1.0 (Build 1153)',
    'Initializing system modules...',
    'Loading kernel... Done.',
    'Mounting cryptograms... [OK]',
    ' ',
    'Welcome to sunOS 1.0!',
    ' ',
    'WARNING: Do NOT use ctrl C to leave the terminal. Press the DOWN arrow or ESC key if you wish so.',
    ' ',
    'Type "enigma" to open the door']
    prompt_text = f'{ALUNO}@sunOS:~$ '
    binary_text = [' ', '01100100 01101001 01100111 01101001 01110100 01100101',
            '00100000 00100010 01101100 01110101 01111010 00100010',
            '00100000 01101110 01101111 00100000 01110100 01100101',
            '01110010 01101101 01101001 01101110 01100001 01101100', ' ']

    return sun_boot, prompt_text, binary_text


def assets_eye(ALUNO):
    dalton_start = ['<DALTON> Opa! Quem é?',
    f'<{ALUNO}> Dalton???? Que alívio te ver aqui. Você sabe como sair desse corredor?? Você foi meu professor em p1.',
    '<DALTON> Se estudou p1 comigo mesmo, então certamente saberá dizer qual é a minha palavra secreta. Não dá pra sair confiando em qualquer um.',
    f'<{ALUNO}> Mas Dalton, sou eu, {ALUNO.split(".")[0]}, como assim??',
    '<DALTON> Existem inquantificáveis homônimos por aí. Diga a palavra secreta.']

    dalton_unlocked = ['<DALTON> Agora que estou vendo um pouco de luz, notei que não consigo fazer nada sem meus óculos e o pior é que não faço ideia de onde os deixei. Você os viu por ai?']

    dalton_end = ['<DALTON> Minha nossa! Você achou meus óculos dentro de um arcade antigo? Pelo menos era um dos bons?',
    '<DALTON> Bem, de qualquer jeito muito obrigado pela ajuda. E lembre-se: para passar em p1 não tem segredo, basta não se esquecer de fazer vossos testes com o OR4CUL0.']

    return dalton_start, dalton_unlocked, dalton_end