"""The tables with which Portuguese reads an e-mail or web address (design section 4.2), for pt-PT and pt-BR.

`pt.py` takes `ELECTRONIC` into its language data and each entry of `VARIETIES` into the data of that variety.

Each symbol reads by its name in the Dicionário Priberam da Língua Portuguesa (dicionario.priberam.org): "@" is
"arroba" ("arroba": "Sinal (@) usado em endereços antes da indicação de domínio"), "." is "ponto" ("ponto", 7:
"Sinal gráfico (.)"), "-" is "hífen" ("hífen": "Sinal gráfico horizontal (-)"), "/" is "barra" ("barra", 10:
"Sinal gráfico (/) constituído por um traço oblíquo"), ":" is "dois pontos" ("dois pontos": "Sinal ortográfico
de pontuação (:)"; the Brazilian norm writes "dois-pontos", with the same sound), "~" is "til" ("til", 1: "Sinal
ortográfico (~)"), "?" is "ponto de interrogação" ("ponto de interrogação": "Sinal de pontuação (?)"), "=" is
"igual" ("igual", 6: "Sinal aritmético (=) de igualdade"), "&" is "e comercial" ("e comercial": "Sinal gráfico
(&)") and "+" is "mais" ("mais", 13: "Usa-se para indicar adição"). Wiktionary, "dot", gives "ponto" as the
Portuguese word for the dot "in URL's or email addresses".

Two names differ by variety. "_" is "traço inferior" in pt-PT (Priberam, "traço inferior": "Sinal gráfico ( _ )")
and "sublinha" in pt-BR (Ciberdúvidas, answer 10508, "O 'underscore' inglês": "pelo menos no Português do Brasil,
é denominado «sub(-)linha»"; Priberam, "sublinha": "Sinal gráfico (_)"). "#" is "cardinal" in pt-PT and
"cerquilha" in pt-BR (Ciberdúvidas, answer 30141, "O nome e o significado do símbolo #": "Em Portugal, é corrente
a denominação cardinal"; the Brazilian Houaiss "regista cerquilha").

A letter reads by its name in the Acordo Ortográfico de 1990, Base I, 1.º, which both varieties share. For "g"
and "k" the Base gives two names, "gê ou guê" and "capa ou cá", and the table takes the first. A domain of two
letters reads letter by letter, and "com" reads as a word: Ciberdúvidas, answer 19059, "A pronúncia de '.com'
(Internet)", says that the domains of countries are spelt "à portuguesa": "o domínio 'pt' é pronunciado 'pê
tê'", and it advises the reading "cõ", the Portuguese word "com".
"""

ELECTRONIC = {
    "electronic_symbols": {"@": "arroba", ".": "ponto", "-": "hífen", "/": "barra", ":": "dois pontos", "~": "til",
                           "?": "ponto de interrogação", "=": "igual", "&": "e comercial", "+": "mais"},
    "electronic_letters": dict(zip("abcdefghijklmnopqrstuvwxyz", (
        "á", "bê", "cê", "dê", "é", "efe", "gê", "agá", "i", "jota", "capa", "ele", "eme", "ene", "ó", "pê", "quê",
        "erre", "esse", "tê", "u", "vê", "dáblio", "xis", "ípsilon", "zê"))),
    "electronic_vowels": ["a", "e", "i", "o", "u"],
    "electronic_schemes": {"http": "read", "https": "read", "ftp": "read"},
    "electronic_tlds": ["pt", "br", "com", "org", "net", "eu"],
}

VARIETIES = {
    "pt-PT": {"electronic_symbols": {"_": "traço inferior", "#": "cardinal"}},
    "pt-BR": {"electronic_symbols": {"_": "sublinha", "#": "cerquilha"}},
}
