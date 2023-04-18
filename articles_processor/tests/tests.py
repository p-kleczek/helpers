import logging
import re
import unittest
from datetime import date
from pathlib import Path

from articles_processor.parser_types import OutputData
from articles_processor.parsers.agora_parser import WysokieObcasyHTMLParser, WyborczaHTMLParser
from articles_processor.parsers.okopress_parser import OKOPressHTMLParser
from articles_processor.parsers.polityka_parser import PolitykaHTMLParser
from articles_processor.parsers.wiez_parser import WiezHTMLParser


class TestSum(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.maxDiff = None

    def test_wiez_1(self):
        input_file_path: Path = Path(".") / """
        wiez1_Karol Wojtyła, Ekke Overbeek, pedofilia i SB - Więź.htm
        """.strip()

        with open(input_file_path, encoding='utf-8') as f:
            file_content = f.readlines()
            parser_input = ''.join(file_content)
        parser = WiezHTMLParser()
        parser.feed(parser_input)
        output: OutputData = parser.output

        self.assertEqual("Karol Wojtyła, Ekke Overbeek, pedofilia i SB", output.title)
        self.assertEqual("Marek Lasota", output.author)
        self.assertEqual(date(2023, 3, 6), output.pub_date.date())
        self.assertEqual(date(2023, 3, 6), output.last_updated.date())
        self.assertEqual('utf-8', output.charset)
        self.assertEqual("", output.description)

        lines = [
            'Podejmując się krytycznej analizy książki Ekke Overbeeka "Maxima culpa. Jan Paweł II wiedział", świadom jestem kontekstu, w jakim toczy i będzie toczyć się dyskusja wokół niej. Nie mogę jednak poprzestać jedynie na uwagach dotyczących (szczegółowo już opracowanej) metody badawczego postępowania z archiwaliami komunistycznego aparatu represji. Chciałbym też uniknąć banalizującego stwierdzenia, że podejście autora do podjętej problematyki jest ahistoryczne. Wobec stawianych przez niego pytań taka odpowiedź byłaby daleko idącym uproszczeniem.',
            'Spróbuję zatem spojrzeć na treść tej książki przede wszystkim przez pryzmat moich doświadczeń w pracy nad zachowaną dokumentacją antykościelnych struktur bezpieczeństwa PRL, zwłaszcza dotyczących Karola Wojtyły. Chcąc być w porządku wobec samego siebie, pokuszę się także o komentarz w sprawach, w których czuję się dalece mniej kompetentny, ale po konsultacjach z tymi, którzy mają wiedzę ekspercką, nie mogę nie podzielić się pewnymi refleksjami.',
            '[H] PRL – kraj nieznany (także autorowi)',
            'Tytuł książki Overbeeka nie zawiera pytania, lecz sprawia wrażenie sentencji wyroku. Dramat z suspensem; wiemy, co się stało; teraz z niepokojem, zaciekawieniem, z poczuciem uczestniczenia w rozwikłaniu mrocznej zagadki pozostaje nam podążać za narratorem ścieżką fabuły, by dotrzeć wraz z nim do pełnego poznania prawdy. I następuje rozczarowanie. Oczekiwane zaskakujące zakończenie nie następuje. Natomiast im głębiej wchodzimy w świat przedstawiony, tym częściej napotykamy różne oblicza ludzkich dramatów. Uprzedzając, przede wszystkim dramatów ofiar seksualnych nadużyć, ale zwykła uczciwość nakazuje także dostrzec dramat osoby skazanej w tytule książki.',
            '[Q] Marek Lasota: Overbeek wykazał się pośpiechem w formułowaniu wniosków. Rekonstruowanie przeszłości na podstawie jednego typu dokumentów archiwalnych jest ryzykowne i powinno nakazywać większą powściągliwość',
            'Każdy rodzaj zranienia dotykający jednostkę czy też zbiorowość rodzi pytania i wątpliwości. Czy musiało do tego dojść? Jakie były okoliczności? Kto ponosi odpowiedzialność? Czy zrobiono wszystko, by do tego nie dopuścić? Jakie są konsekwencje? I zazwyczaj niezwykle trudno jest udzielić takiej odpowiedzi, która byłaby adekwatna do miary bólu, takiej odpowiedzi, która zadowalałaby wszystkich.',
            'Gdy czyta się "Maxima culpa", trudno odnaleźć w treści choćby cień tych pytań. Wszystko bowiem jest u Overbeeka jasne albo raczej czarno-białe, jak w schematycznym kryminale. Są zbrodniarze i ich ofiary, jest czas i miejsce akcji – i jest zbrodnia, którą udało się ukrywać przez długie lata, ale dzięki odwadze, determinacji i umiejętnościom dzielnego detektywa została odkryta i ujawniona.',
            'Wyjaśnienie tej ponurej historii okazuje się zaskakująco proste. Wystarczyło bowiem sięgnąć do archiwalnych dokumentów, na które wcześniej nikt nie natrafił albo, co gorsza, nie chciał ich odnaleźć, a one zawierają wszystko, co trzeba wiedzieć o sprawcach, ofiarach i okolicznościach. Dla Overbeeka nie ma znaczenia czas akcji. Autor nie dostrzega (co w pewnym stopniu można zrozumieć) niezwykłego splątania losów ówczesnych postaci, tych wielkich i tych zwyczajnych, z momentem dziejowym, w którym snuje się ta opowieść.',
            'Rozdział noszący znamienny tytuł "Czerwoni i czarni" – wszak jedni i drudzy są ciemną stroną mocy – zaczyna się od słów: "Zanim wkroczymy na teren archidiecezji krakowskiej lat 60. i 70., poznajmy kontekst. Wydarzenia przedstawione w następnych rozdziałach rozgrywają się w kraju dla większości z nas, w tym dla młodych Polaków, nieznanym". Dodać trzeba: nieznanym także dla autora, czego sam dowodzi w pozostałych partiach tego rozdziału, które sprawiły na mnie wrażenie opracowania skopiowanego z licznych portali internetowych zawierających marne na ogół ściągi dla leniwych uczniów.',
            'By się upewnić co do swych odczuć, spojrzałem w uwidocznioną na końcu książki, zawartą w przypisach (obszerną skądinąd) bibliografię. Próżno w niej szukać jakichkolwiek poważnych syntetycznych opracowań poświęconych stosunkom państwo-Kościół w czasach PRL. A jest ich przecież niemało i większość z nich nie jest dziełem historyków kościelnych (co niektórym mogłoby służyć do snucia podejrzeń o stronniczość), lecz także cieszących się autorytetem i uznaniem profesorów prowadzących swe prace w świeckich uniwersytetach i instytutach badawczych.',
            'Co więcej, niektóre z tych opracowań precyzyjnie i wyczerpująco tworzą warsztat badawczy umożliwiający rzetelną analizę tak specyficznego źródła, jakim są dokumenty wytworzone przez komunistyczny aparat represji w latach 1945–1990. Wskazują one także, jak radzić sobie w sytuacji dość częstych braków w dokumentacji dotyczącej jakiegoś zjawiska w archiwach.',
            '[H] Jedno podstawowe pytanie',
            'Overbeek kilkakrotnie w tekście nawiązuje do tzw. TEOK-ów (Teczka Ewidencji Operacyjnej Księdza), czyli dossier każdego duchownego (diecezjalnego i zakonnego) w Polsce, podkreślając, że zniknęły one na przełomie lat 80. i 90. Sugeruje przy tym, że stało się to w wyniku zmowy władz upadającego nieuchronnie państwa komunistycznego z hegemonicznym, dzięki Janowi Pawłowi II, Kościołem w Polsce. Choć autor nie pisze tego wprost, sprawia wrażenie, że zakłada, iż teczki te zawierały oczywiście obraz moralnego zepsucia polskiego duchowieństwa, w tym znacznie liczniejsze dowody nadużyć księży.',
        ]
        out_lines = re.sub(r"\n+", "\n", output.content).split('\n')
        self.assertListEqual(lines, out_lines)

        self.assertListEqual([], output.links)

    def test_wysokieobcasy_1(self):
        input_file_path: Path = Path(".") / """
        wysokieobcasy1_Córka współzałożyciela Oddziału Zamkniętego Czułam, że jestem skazana na uzależnienia.html
        """.strip()

        with open(input_file_path, encoding='iso-8859-2') as f:
            file_content = f.readlines()
            parser_input = ''.join(file_content)
        parser = WysokieObcasyHTMLParser()
        parser.feed(parser_input)
        output: OutputData = parser.output

        self.assertEqual("Córka współzałożyciela Oddziału Zamkniętego: Czułam, że jestem skazana na uzależnienia",
                         output.title)
        self.assertEqual("Monika Redzisz", output.author)
        self.assertEqual(date(2023, 4, 16), output.pub_date.date())
        self.assertEqual(date(2023, 4, 16), output.last_updated.date())
        self.assertEqual('iso-8859-2', output.charset)
        self.assertEqual("", output.description)

        lines = [
            '//Seks, psychologia, życie: zapisz się na newslettery "Wysokich Obcasów"[L1]//',
            '[Q] Monika Redzisz: Chorujesz na chorobę dwubiegunową. Dlaczego opowiadasz o tym publicznie?',
            'Maja Laura Jaryczewska: Bo mam nadzieję, że ta opowieść komuś pomoże. Kiedy usłyszałam diagnozę, uwierzyłam, że jestem uratowana, bo wreszcie wiem, co leczyć. To wtedy coś zaczęło się zmieniać w moim życiu.',
            'Wokół choroby dwubiegunowej jest wiele szkodliwych stereotypów. Chcę z nimi walczyć. Zdarza mi się, że ludzie mnie pytają, po co biorę leki. "Taka młoda dziewczyna! Po co się tym trujesz?" – mówią. Tłumaczę im wtedy, że te leki ratują mi życie. Sprawiają, że zaczynam doświadczać szczęścia.',
            '[Q] Kiedy zaczęły się twoje problemy psychiczne?',
            'Miałam siedem lat, wyprowadziliśmy się z Warszawy. W domu zdarzały się intensywne awantury, a we mnie narastał niepokój i brak poczucia bezpieczeństwa. Kiedy rodzice się kłócili, wbiegałam między nich i próbowałam ich godzić. Pamiętam dokładnie dźwięk trzaskających szklanych drzwi. W domu było niebezpiecznie, ale jeszcze większy lęk budziła we mnie wizja bycia poza domem. Myśl, że następnego dnia muszę iść do szkoły, tak mnie stresowała, że godzinami nie mogłam zasnąć. Przez całe lata czułam głęboki wewnętrzny smutek i miałam bardzo niskie poczucie własnej wartości. Bo skoro nie zasługiwałam na kochający dom, to co byłam warta?',
            'Kiedy miałam 12 lat, rodzice się rozwiedli, a ja poczułam się pozostawiona sama sobie. Chciałam po prostu zniknąć. Zaczęłam więc poszukiwania, poszłam w duchowość.',
            '[Q] Twój ojciec Krzysztof Jaryczewski, współzałożyciel i pierwszy wokalista Oddziału Zamkniętego, legenda polskiego rocka, był przez lata uzależniony od alkoholu i narkotyków. Podobno zerwał z nałogiem, kiedy się urodziłaś.',
            'Tak. Wszyscy mi zawsze mówili, że to ja go uratowałam. Pamiętam taką scenę: mam kilka lat, a nade pochylają się ludzie i mówią: "Maju, dzięki tobie twój tata żyje! Uratowałaś go!".',
            '[Q] Rozmawiał z tobą na ten temat?',
            'Tak. Był po wielu odwykach i wiele mi o tym opowiadał. Próbował uczyć mnie zasad funkcjonowania w zdrowych relacjach, wyrażania swoich potrzeb, stawiania granic. Myślę, że to wielki skarb i niewielu go od swoich rodziców otrzymuje, bo mało kto do takiej wiedzy ma dostęp.',
            '[Q] Twoja mama była z kolei psychoterapeutką uzależnień. Nie bała się, że pójdziesz w ślady ojca?',
            'Bardzo. Powtarzała, że jestem genetycznie podatna na uzależnienia, że muszę uważać. Ten temat był wciąż obecny. Może właśnie dlatego rosła we mnie taka przekorna ciekawość i chęć, żeby spróbować. Czułam, że skoro geny o wszystkim decydują, to i tak jestem na to skazana. Spróbowałam, kiedy miałam 14 lat. Zaczęłam od razu od substancji z kategorii twardych – amfetamina, metamfetamina. No i miałam to swoje "zniknięcie". Poczułam, że złapałam Pana Boga za nogi.',
            '[Q] Mama to wychwyciła?',
            'Tak, ale byłam wtedy już tak zbuntowana, że nie było w ogóle mowy, żeby mi czegokolwiek zabronić. Tak lawirowałam, że zawsze znajdowałam jakiś sposób. Mieszkałyśmy z mamą w Lubuskiem. Byłam w gimnazjum i równolegle chodziłam do szkoły muzycznej drugiego stopnia. Miałam do niej 60 kilometrów, dojeżdżałam kilka razy w tygodniu. To był świetny pretekst, żeby się przenieść do internatu.',
            'Mama długo nie chciała się na to zgodzić, ale w końcu dopięłam swego. I poszłam w długą. Chodziło mi tylko o to, żeby mieć wolność w odcinaniu się od świata. Jednak w którymś momencie naprawdę się przestraszyłam, że narkotyki mnie zabiją, i odstawiłam te twarde. Wtedy zaczęło się picie, leki, palenie, psychodeliki i inne eksperymenty.',
            '[Q] Nie zawaliłaś przez to nauki?',
            'Nie. W szkole sobie radziłam. Brałam udział w różnych olimpiadach przedmiotowych i w konkursach w ramach szkoły muzycznej. Właściwie codziennie musiałam być w dwóch szkołach, ale taki układ dawał wiele możliwości. W jednej szkole mówiłam, że mam wiele do zrobienia w drugiej, i na odwrót.',
            'Działałam też społecznie. Miałam 12 czy 13 lat, kiedy poraziła mnie prawda o świecie, dostrzegłam, ile jest w nim cierpienia. Czułam się, jakbym odkryła jakiś wielki spisek. Wstrząsnęło mną cierpienie zwierząt i wykorzystywanie ich w różnych gałęziach przemysłu. Było to wręcz metafizyczne doświadczenie, które mnie zmotywowało do tego, żeby zmieniać świat. Początkowo działałam w Otwartych Klatkach, a potem w fundacji Efektywny Altruizm. Filozofia efektywnego altruizmu, czyli idei łączenia odruchów serca i empatii z rozsądkiem i badaniami naukowymi, wydała mi się drogą, dzięki której zdziałam najwięcej.',
            'Pod koniec gimnazjum wymyśliłam, że pójdę do liceum w Gdańsku i zamieszkam z tatą. Czułam, że ktoś musi mnie kontrolować, bo inaczej umrę. I rzeczywiście – przy nim zaczęłam się ogarniać. Tata zaprowadził mnie na terapię grupową dla uzależnionych nastolatków. Spotkałam tam chłopaków w dresach, mówiących innym językiem, ludzi z zupełnie innego świata niż ja. Ale to ja opowiadałam najgorsze historie… Straszny to był dla mnie wstyd.',
            '[Q] Dzieci z dobrych domów i uczniowie najlepszych liceów też popadają w uzależnienia.',
            'Tak, patointeligencja ma się, niestety, dobrze. Myślę, że po prostu wszyscy ludzie mają takie same problemy, niezależnie od tego, z jakiej warstwy społecznej pochodzą.',
            'W tamtym czasie zaczęłam medytować w szkole zen. Czułam, że podczas medytacji oczyszcza mi się umysł. Trafiłam też na indywidualną terapię uzależnień, na której uczyłam się, jak sobie radzić ze złymi nawykami. To wszystko mi pomagało, ale działało tylko na objawy.',
            'Istotą była depresja. Ale wtedy nie wiedziałam jeszcze, że ją mam. Byłam przesiąknięta smutkiem i wydawało mi się, że po prostu mam taki charakter.',
            '[Q] Kiedy zrozumiałaś, że chorujesz na depresję?',
            'Po śmierci mamy. Miałam 21 lat, kiedy zmarła na nowotwór piersi. A ze mną zaczęło się dziać coś bardzo złego. Miałam coraz mniej energii i coraz częściej bolała mnie głowa. Tabletki przeciwbólowe działały coraz słabiej, ból się nasilał. Czasem w nocy budziłam się sparaliżowana bólem, w pewnym momencie odebrało mi wręcz mowę. Myślałam, że mam guza mózgu…',
            'Zaczęło się chodzenie po lekarzach. Neurolog w porozumieniu z psychiatrą doszli do wniosku, że bóle głowy są objawem depresji. Nie miałam pojęcia, że depresja może prowadzić do czegoś takiego!',
            'Dostałam pierwsze leki antydepresyjne. Niestety, nie zadziałały.',
            '[Q] W tym czasie studiowałaś w akademii muzycznej fortepian jazzowy i kompozycję klasyczną. Wydałaś też swoją debiutancką płytę zatytułowaną "Bardo". Jak sobie radziłaś?',
            'Muzyka mnie ratowała. Zawsze była dla mnie ucieczką i wytchnieniem, dawała mi możliwość wyrzucenia z siebie trudnych emocji. Choroba i śmierć mamy zbiegły się z nagrywaniem płyty. Jej tytuł wymyśliłam wiele lat temu. Bardo to w buddyzmie droga, przejście między jednym życiem a drugim. Chciałam dzięki muzyce przejść z ciemności do światła.',
            'Niestety, pół roku po zdiagnozowaniu depresji przyszedł drugi kryzys. Ból głowy nie odpuszczał, paraliżował mnie. W pewnym momencie był tak straszny, że myślałam, że się zabiję. Wiedziałam, że gdy rano otworzę oczy, będzie na mnie czekał.',
            'Przerwałam na trzy miesiące wszystko: i studia, i pracę w fundacji, i nagrywanie. Nie byłam w stanie nic robić. Wyjście na ulicę wydawało mi się misją ponad siły. Siedziałam w domu i czułam, że nie mam żadnego celu, że nikt na mnie nie czeka, że nie jestem na tym świecie potrzebna. Nie byłam w stanie nawet medytować. Kiedy siadałam, natychmiast zaczynałam płakać, bo przed oczami stawała mi mama.',
            'Ktoś mi poradził, żebym poszła na akupunkturę. Chodziłam na sesje przez trzy tygodnie codziennie – nie miałam nic do stracenia, i tak nic innego nie działało. Po tygodniu ból znikł na kilka godzin. Potem na dzień. Potem na dwa dni. I tak powoli zaczęłam go odpierać.',
            '[Q] Kiedy zdiagnozowano u ciebie chorobę dwubiegunową?',
            'Trafiłam do psycholożki, która zasugerowała mi, żebym zrobiła badania pod kątem ADHD. Skierowała mnie do psychiatry, który stwierdził ADHD z nadaktywnością i impulsywnością.',
            'To on wdrożył mi lek antydepresyjny, który zaczął działać już po kilku tygodniach. Biorę go do dziś. Czułam się po nim dobrze przez kilka miesięcy. Byłam dużo bardziej stabilna emocjonalnie.',
            'A potem wystąpiła mania. Myślę, że jej epizody miałam już wcześniej, ale nigdy nie były tak silne. W zasadzie czułam się świetnie, ale byłam jakby oderwana od ziemi, od realności. Głos mi drżał, ręce się trzęsły. Mimo że spałam po trzy godziny na dobę, rano nie byłam zmęczona. Miałam tysiąc nowych pomysłów na minutę. Psychiatra zdiagnozował chorobę dwubiegunową i zmienił część leków, przepisał też dodatkowe.',
            'I nagle wróciła depresja. Przeskoczyłam w nią w jednej chwili. Znowu nie miałam siły wstać z łóżka. I znów była zmiana dawkowania leków, znów musiałam wytrzymać, być cierpliwa, mieć wiarę, że za chwilę będzie lepiej. Ale straciłam nadzieję. Co z tego, że leki zaczną działać, skoro zaraz wrócę na drugi biegun i trzeba będzie działać przeciwnie? – myślałam.',
            'Nowe leki nie działały. Zaczęło być lepiej dopiero wtedy, gdy lekarz zwiększył dawkę, mniej więcej po dwóch miesiącach.',
            '[Q] Co było gorsze, mania czy depresja?',
            'Mania. Nie miałam nad sobą kontroli. Ludzie widzieli, że zachowuję się dziwnie. Byłam wtedy prezeską fundacji Efektywny Altruizm. Uczestniczyłam w wideokonferencjach, podczas których nie wiedziałam, co mam ze sobą robić. Nie byłam w stanie wysiedzieć w jednym miejscu, wyłączałam kamerkę i chodziłam w kółko po pokoju. Ręce mi się trzęsły, głos drżał, wciąż byłam czymś podekscytowana.',
            'Wiedziałam, że muszę na siebie bardzo uważać. Słyszałam wielokrotnie, że ludzie w manii robią różne rzeczy, na przykład zaciągają kredyty. Ta wiedza pomogła mi uchronić się przed wieloma ryzykownymi sytuacjami.',
            '[Q] Jak jest dziś?',
            'Dobrze. Kolejnej manii już nie było, a depresja się spłyca. Pojawiło się za to we mnie coś nowego – coś nienasączonego tym smutkiem, który był ze mną od tylu lat. Na jakimś etapie terapii mnie to przeraziło, bo ten smutek był elementem mojej tożsamości, częścią mnie. Rosłam z nim od dziecka, to on mnie ukształtował. A tu nagle pojawiła się jakaś nowa osoba. Osoba, której nie znałam.',
            '[Q] Jaka jest ta osoba?',
            'Przede wszystkim przestała czuć ból. To dla mnie cud, że udało mi się dotrzeć do tego miejsca. Przez całe lata nie potrafiłam sobie nawet takiej rzeczywistości wyobrazić. Dlatego właśnie chcę o tym mówić. Myślę, że są miliony osób, które chorują i nie wierzą, że może być lepiej.',
            '//Maja Laura Jaryczewska ma 24 lata, jest pianistką, kompozytorką, wokalistką, autorką tekstów i producentką. W zeszłym roku zadebiutowała płytą "Bardo". Córka legendy polskiego rocka Krzysztofa Jaryczewskiego, współzałożyciela Oddziału Zamkniętego. Od lat angażuje się w działalność dobroczynną//',
        ]
        out_lines = re.sub(r"\n+", "\n", output.content).split('\n')
        self.assertListEqual(lines, out_lines)

        self.assertListEqual([
            'https://wyborcza.pl/0,166389.html'
        ], output.links)

    def test_okopress_1(self):
        input_file_path: Path = Path(".") / """
        okopress1_Iustitia Nie daliśmy się złamać przez 8 lat, wygramy. Walczymy o nowoczesne sądy i nową KRS - OKO.press.html
        """.strip()

        with open(input_file_path, encoding='utf-8') as f:
            file_content = f.readlines()
            parser_input = ''.join(file_content)
        parser = OKOPressHTMLParser()
        parser.feed(parser_input)
        output: OutputData = parser.output

        self.assertEqual("Iustitia: Nie daliśmy się złamać przez 8 lat, wygramy. Walczymy o nowoczesne sądy i nową KRS",
                         output.title)
        self.assertEqual("Mariusz Jałoszewski", output.author)
        self.assertEqual(date(2023, 4, 17), output.pub_date.date())
        self.assertEqual(date(2023, 4, 17), output.last_updated.date())
        self.assertEqual('utf-8', output.charset)
        self.assertEqual("", output.description)

        lines = [
            '[H] Iustitia: Nie daliśmy się złamać przez 8 lat, wygramy. Walczymy o nowoczesne sądy i nową KRS',
            'Największe stowarzyszenie sędziów w Polsce Iustitia mimo represji ze strony ludzi ministra Ziobry, nadal jest zjednoczone i wierzy, że obroni wolne sądy. Pracuje nad pakietem ustaw, które mają zreformować sądy. Wyśle też apel do Komisji Europejskiej, by zajęła się neo-KRS.',
            'Deklaracje walki do końca o niezależne sądy w Polsce oraz wstępne propozycje reform sądów padły na dorocznym Zebraniu Delegatów Iustitii w dniach 14-16 kwietnia 2023 roku. Iustitia to największe stowarzyszenie sędziów w Polsce. Liczy ok. 3600 członków. Wraz z mniejszym stowarzyszeniem sędziów Themis broni niezależności sądów i jest ostrym recenzentem pomysłów oraz działań ministra sprawiedliwości Zbigniewa Ziobry. ',
            'Sędziowie ze stowarzyszenia zebrali się w podwarszawskim Ołtarzewie. Mimo trwającego już osiem lat ataku władzy PiS na sądy, na sali nie było czuć defetyzmu i poczucia porażki. Wręcz przeciwnie. Czuć było energię. Padały pytania, co będzie dalej. Ale sędziowie w kuluarach mówili, że robią swoje i wierzą w powrót rządów prawa. ',
            'Dużo mówiono też o planach na przyszłość. Iustitia chce zaproponować reformy. Do wakacji powinien zostać ogłoszony pakiet ustaw reformujących wymiar sprawiedliwości. Iustitia pracuje nad nim z innymi organizacjami prawniczymi. Chodzi o pięć projektów ustaw. Iustitia z prawnikami pracuje nad nową ustawą o SN, KRS i ustawą o ustroju sądów powszechnych. Fundacja Batorego nad nową ustawą o TK, a stowarzyszenie Lex Super Omnia nad nową ustawą o prokuraturze. ',
            'Są szanse, że projekty zostaną ogłoszone na III Kongresie Prawników, który odbędzie się 24 czerwca w Gdańsku. "Witamy w wolnej Polsce, wśród niezależnych sędziów" - mówił rozpoczynając obrady prezes Iustitii prof. Krystian Markiewicz (na zdjęciu u góry). "Jesteśmy tu silniejsi. My nie pękamy, ale wygrywamy. Musimy postawić mur fali nieprawości i zbudować nowoczesne sądownictwo" - podkreślał prezes Iustitii. ',
            'Kolejny cel Iustitii to naprawa obecnej nielegalnej neo-KRS. Oprócz propozycji ustawowych sędziowie z Iustitii i będący na obradach sędziowie zagraniczni podpisali apel do Komisji Europejskiej, by wszczęła przeciwko Polsce postępowanie naruszeniowe w związku z działalnością tego niekonstytucyjnego organu. To on bowiem jest głównym źródłem problemów z praworządnością w Polsce. O apelu piszemy w dalszej części tekstu. ',
            'Tegoroczne zebranie Iustitii było szczególne. Bo były odniesienia nie tylko do obecnej sytuacji sądów w Polsce, ale i na świecie. Odczytano list uwięzionego sędziego tureckiego Murata Arslana. Solidaryzowano się z sędziami izraelskimi, których chce podporządkować tamtejsza władza. Na zebraniu wystąpili też sędziowie z Ukrainy, którzy dziękowali za wsparcie i mówili o tym, jak wojna dotyka ich sądy. ',
            'Na zebraniu byli też sędziowie zagraniczni, w tym Kees Sterk, sędzia z Niderlandów, który za zaangażowanie w obronę praworządności w Polsce został honorowym członkiem Iustitii. O tym, co działo się i co mówiono na zebraniu, piszemy w dalszej części tekstu.',
            '[H] Jak Iustitia chce zreformować sądy',
            'Na Zebraniu w niedzielę 16 kwietnia 2023 roku została przyjęta uchwała programowa. Wyznacza ona kierunek na przyszłość, w którym chce iść stowarzyszenie. Iustitia dalej będzie bronić wolnych sądów i represjonowanych sędziów. ',
            'W uchwale napisano: "Najważniejszym celem jest przywrócenie praworządności w naszym kraju w oparciu o projekty ustaw przygotowane przez Stowarzyszenie oraz podmioty, z którymi łączą nas wspólne wartości. W pierwszej kolejności należy - w granicach porządku konstytucyjnego i europejskiego - odwrócić negatywne zmiany wprowadzone od 2015 r. i rozliczyć osoby odpowiedzialne za naruszanie praworządności". ',
            'Iustitia zaczyna też debatę o tym, jak mają wyglądać sądy po erze Ziobry. Stowarzyszenie chce, by były nowoczesne i cyfrowe. Proponuje m.in. "elektroniczny system zarządzania postępowaniami sądowymi, szerokie wsparcie informatyczne kadry orzeczniczej, podnoszenie kompetencji cyfrowych sędziów i pozostałych pracowników sądów, digitalizację akt, zmianę systemów doręczeń sądowych oraz opiniowania". ',
            'W tym celu konieczne jest zwiększenie wydatków na sądy. Iustitia pisze w uchwale: "Oczekujemy uznania budowy nowoczesnego sądownictwa za cel strategiczny, istotny dla bezpieczeństwa Państwa Polskiego i przyjęcia stałego wskaźnika wydatków na sądownictwo na wzór obronności".',
            'Stowarzyszenie proponuje również zmiany ustrojowe. Już wcześniej przedstawiła je w projekcie zgłoszonym w Sejmie przez opozycję na początku 2022 roku. Ten projekt to szybki sposób na przywrócenie praworządności, poprzez cofnięcie zmian wprowadzonych przez PiS i Ziobrę. Iustitia podtrzymuje te pomysły. ',
            'To głównie likwidacja obecnej nielegalnej neo-KRS, która wadliwymi nominacjami dla neo-sędziów infekuje cały wymiar sprawiedliwości. Co potwierdziły w wyrokach ETPCz i TSUE. Miejsce neo-KRS zajęłaby KRS zgodna z Konstytucją i standardami europejskimi. Czyli na pewno niewybrana jak dziś przez polityków. Stowarzyszenie w obecnym projekcie proponuje, by do KRS były wybory (zorganizowane wśród sędziów), w których startowaliby sędziowie zgłoszeni przez środowiska prawnicze. ',
            'Iustitia podtrzymuje też pomysł cofnięcia wszystkich nominacji dla neo-sędziów. Jest ich już 2,5 - 3 tysiące. Mogliby oni ponownie wystartować w konkursie, ale przed legalną KRS. Inaczej potraktowani byliby asesorzy sądowi, oni przechodziliby tylko weryfikację. Nie byłoby jednak automatycznego podważania wydanych wyroków przez neo-sędziów. Co do zasady można by je podważać na wniosek stron procesu.',
            'Nowością są dwa pomysły. Pozbawienie nadzoru administracyjnego nad sądami ministra sprawiedliwości. Ten pomysł wraca co kilka lat. Nadzór miałaby zreformowana KRS oraz samorząd sędziowski. Nowością jest też propozycja, by sędziowie mieli jednolity status sędziego sądu powszechnego. ',
            'Dziś są trzy szczeble w karierze sędziego - sędzia rejonowy, okręgowy i apelacyjny. Ten pomysł pokrywa się z pomysłem ministra sprawiedliwości Zbigniewa Ziobry. Tyle, że pod jego płaszczykiem minister chce zlikwidować obecne sądy i powołać nowe, kontrolowane przez władzę i bez niezależnych sędziów. Iustitia chce zachować obecną strukturę sądów. Chce tylko ujednolicić status sędziego.',
            '[H] Apel do KE by zaskarżyła neo-KRS do TSUE',
            'Sędziowie z Iustitii chcą też by Komisja Europejska w końcu zajęła się nielegalną neo-KRS i wszczęła w tej sprawie przeciwko Polsce postępowanie naruszeniowe, które zakończy się skargą do TSUE. W tym celu stowarzyszenie przyjęło na zebraniu apel do Komisji. Sędziowie podpisywali się pod nim na specjalnym banerze, który ma być przekazany KE. Podpisy złożyli też sędziowie zagraniczni obecni na zebraniu, w tym Kees Sterk. ',
            'W apelu napisano, że działania KE są "niezbędne do przywrócenia praworządności w Polsce oraz zagwarantowania obywatelom Polski i innych państw członkowskich prawa do niezależnego sądu". ',
            'W apelu padają mocne słowa pod adresem neo-KRS. Napisano: "Polska neo-KRS w praktyce swojego funkcjonowania wielokrotnie udowodniła już, że jest organem realizującym oczekiwania władzy, która wybrała sędziów do jej składu. Przez ostatnie lata bezpardonowego ataku na gwarancje niezawisłości sędziów nie zajęła stanowiska w obronie tej wartości.',
            'Przeciwnie, czynnie wspierała systematyczne osłabianie niezależności władzy sądowniczej, przede wszystkim poprzez udział w nielegalnej procedurze nominacyjnej sędziów, co prowadzi do rażącego naruszenia art. 6 EKPCz i art. 47 KPP". ',
            'Ta artykuły gwarantują prawo do niezależnego sądu, ustanowionego ustawą. Co potwierdzają wyroki ETPCz. "Ponadto neo-KRS nie spełnia swojej funkcji gwaranta niezależności sędziów, stała się organem represji i politycznego podporządkowania" - napisali w apelu sędziowie. ',
            'Apel wylicza, co wskazuje na brak wypełniania przez neo-KRS obowiązków. To m.in.: ',
            '  * udział w procedurze przenoszenia sędziów w stan spoczynku, pomimo ich chęci dalszego orzekania; ',
            '  * zatwierdzanie decyzji o przenoszeniu sędziów do innych wydziałów bez ich zgody, co stanowi środek represji wobec sędziów; ',
            '  * utrudnianie złożenia odwołań w postępowaniach związanych z nominacją sędziów Sądu Najwyższego; ',
            '  * pozytywne opiniowanie aktów prawnych [obecnej władzy - red.] niszczących gwarancje niezależności sądów; ',
            '  * awansowanie nawzajem członków Rady; ',
            '  * wskazywanie do nominacji sędziowskiej kandydatów czynnie zaangażowanych politycznie lub o niewystarczających kwalifikacjach; ',
            '  * ingerencja w trwające sprawy poprzez sugerowanie wysłania na szkolenie sędzi, która wydała wyrok niewygodny dla partii rządzącej. ',
            'W apelu do KE napisano, że obecna władza nie chce rozwiązać problemu neo-KRS. Podkreślono: "Przeciwnie, utrwalane są wszystkie patologie związane z politycznym systemem powołań sędziowskich. Dewastacja państwa prawa rozszerza się. Upolityczniony Trybunał Konstytucyjny nie rozstrzyga żadnych zagadnień prawnych w duchu wspólnotowego dorobku prawnego. Z udziałem Neo-KRS powołano do tej pory 3000 sędziów, których wyroki mogą być skutecznie podważane z uwagi na wadliwość procedury nominacyjnej". ',
            'Na końcu apelu dodano: "Warunkiem koniecznym do przywrócenia praworządności w Polsce jest uzdrowienie Krajowej Rady Sądownictwa. Nie można przywrócić rządów prawa, walcząc jedynie ze skutkami, a nie z przyczynami kryzysu. Dalsze zwlekanie przez KE z wszczęciem postępowania przeciwnaruszeniowego stanowi zgodę na zatruwanie polskiego i unijnego wymiaru sprawiedliwości sędziami powołanymi niezgodnie z prawem i niszczenie rządów prawa".',
            '[H] Markiewicz: Jesteśmy silni jak nigdy',
            'Ważne były też przemówienia sędziów na Zebraniu w sobotę 15 kwietnia 2023 roku. Padły w nich deklaracje obrony praworządności i wolnych sądów do końca. Obecna władza nie ma więc co liczyć, że uda się jej spacyfikować niezależnych sędziów. ',
            'Pierwszy przemawiał prezes Iustitii, prof. Krystian Markiewicz, na co dzień sędzia Sądu Okręgowego w Katowicach. Mówił, że sędziowie walczą o to, by obywatele mieli zagwarantowane prawo do niezależnego sądu. Że sędziowie płacą za to wysoką cenę w postaci represji. ',
            'Wymienił przykłady prześladowanych przez ludzi Ziobry sędziów z Iustitii - Igora Tuleyę, Piotra Gąciarka, Macieja Ferka, Pawła Juszczyszyna, Dorotę Zabłudowską i Joannę Hetnarowicz-Sikorę. "To są osoby, z którymi walczymy o to, na czym nam zależy. Czyli o to by rządy prawa były standardem w Polsce i UE" - podkreślał Markiewicz.',
            'Mówił, że dzięki uporowi polskimi sądami zainteresowała się Komisja Europejska, która wprowadziła zasadę pieniądze za praworządność. Przypomniał, że to dzięki temu uporowi odwieszono już wszystkich bezprawnie zawieszonych przez nielegalną Izbę Dyscyplinarną sędziów. ',
            '"To nasz sukces. My jesteśmy dziś silniejsi, jesteśmy silni jak nigdy wcześniej" - zapewniał prezes Iustitii. Potem mówił, że hasłem Zebrania jest budowa nowoczesnego sądownictwa w Polsce. Budowa sądów niezależnych, sprawnych i przyjaznych dla obywatela.',
            'Markiewicz mówił, jak ważne dla polskich sędziów było wsparcie od sędziów europejskich. Przypomniał Marsz Tysiąca Tóg z 11 stycznia 2020 roku, na którym byli sędziowie z całej Europy. I dodał, że Europejskie Stowarzyszenie Sędziów wystąpiło do ONZ, by data Marszu Tysiąca Tóg była dniem niezawisłości sędziego na całym świecie. ',
            'Prezes Iustitii podkreślał jednocześnie, że doświadczenie polskich sędziów może być pomocne w obronie i budowaniu niezależności sądów na całym świecie. Nie są to słowa rzucone na wiatr. Bo to dzięki skargom i pytaniom prejudycjalnym z Polski ETPCz i TSUE wydały wiele przełomowych wyroków dotyczących wymiaru sprawiedliwości. Iustitia wraz z Themis pokazały też w praktyce, jak broni się wolnych sądów.',
            '[H] Sterk: Musimy bronić wolnego i sprawiedliwego świata',
            'Na koniec swojego wystąpienia Markiewicz wręczył honorowe członkostwo w Iustitii. Otrzymał je Kees Sterk, sędzia niderlandzki, profesor z Uniwersytetu w Maastricht. I były prezes Europejskiej Sieci Rad Sądownictwa, z której wyrzucono neo-KRS. Sterk angażuje się w obronę praworządności w Polsce. Nadanie mu honorowego członkostwa jest formą podziękowania za to zaangażowanie. ',
            '"Jest sędzią, naukowcem, ale przede wszystkim człowiekiem, który służy obywatelom całej Europy" - wyliczał Markiewicz. I dalej, że Sterk angażuje się we współpracę międzynarodową i kształtowanie europejskich standardów sądownictwa. Że walczył o polskie sądy jako prezes ENCJ. ',
            'Prezes Iustitii przypomniał, że gdy PiS w połowie 2018 roku chciał usunąć sędziów SN i byłą już I prezes SN Małgorzatę Gersdorf, Sterk przyjechał szybko do Warszawy, by pojawić się w SN i powiedzieć, że Gersdorf jest legalnym prezesem. "Tak się zachowuje wielki człowiek w trudnych chwilach. Wspomaga nas mocno, walczy o to każdego dnia. Jest prawdziwym przyjacielem Polski i polskich sędziów" - mówił Markiewicz.',
            'Kees Sterk był wzruszony. Mówił: "Jesteśmy europejskimi sędziami". W swojej przemowie mówił, co to znaczy, wspominał też, jak zaczął angażować się w obronę praworządności w Polsce. Zaczęło się to w 2015 roku, gdy stara, legalna KRS zwróciła się o pomoc do niderlandzkich sędziów. W pamięć wbiły się mu dwa słowa: "Help us". ',
            'Wspomniał, jak na prośbę władz holenderskich odwiedził ministerstwo sprawiedliwości. Odbył rozmowę z jednym z zastępców Zbigniewa Ziobry. Zapamiętał, że była na nim agresywna atmosfera. Zapamiętał też nieprzyjemny uśmiech wiceministra. Wtedy zrozumiał, że PiS nie ma szczerych intencji ws. reform sądowych. Że oni kłamią i niszczą niezawisłość sędziowską. ',
            '"To był dla mnie punkt zwrotny. Powiedziałem niderlandzkiemu ministrowi sprawiedliwości, że to nie tylko ich problem [Polski - red.], ale i nasz" - mówił Kees Sterk. Poparł apel do KE ws. neo-KRS. Uważa, że przy KE powinna powstać rada konsultacyjna ds. sądownictwa. ',
            'Mówił też o potrzebie dialogu pomiędzy sędziami europejskimi, że koncepcja takiego sędziego ciągle się rozwija. Że potrzebna jest współpraca, po to, by bronić tego, w jaki sposób chcemy żyć w "świecie wolnym i sprawiedliwym".',
            '[H] Sędzia Murat: Niech świat nie zamyka oczu na los sędziów tureckich',
            'Potem przemawiali kolejni goście. Prezes Europejskiego Stowarzyszenia Sędziów i sędzia SN Chorwacji Duro Sessa mówił, że Iustitia jest przykładem dla wielu sędziów w Europie. Deklarował poparcie dla polskich sędziów. "Walczymy o zasady nie dla nas, ale dla dobra obywateli. Musimy wyjaśniać, jakie wartości są zagrożone" - podkreślał Sessa. Mówił, że władze powinny rozpocząć dialog z sędziami i przestać atakować wartości, które są fundamentem demokracji. ',
            'Potem przemawiała prezeska europejskiego stowarzyszenia sędziów i prokuratorów MEDEL, prokurator Mariarosaria Guglielmi z Włoch. Od grudnia 2022 roku wiceprezesem stowarzyszenie MEDEL jest sędzia Monika Frąckowiak z Poznania. ',
            'Szefowa MEDEL dziękowała Iustitii za obronę niezależności sądownictwa. Mówiła, że to dzięki polskim sędziom Europa zainteresowała się praworządnością w Polsce i problemem niezawisłości sędziów. Mówiła, że potrzebny jest europejski ład prawny, który uniezależni sądy od nacisków.',
            'Podkreślała, że sędziowie wraz z prokuratorami razem muszą stawić wyzwania zagrożeniom. Bo praworządność nie jest dana raz na zawsze i jest regres rządów prawa na całym świecie. W tym kontekście przypomniała aresztowania sędziów i prokuratorów z Turcji. ',
            'Sędziowie w całej Europie ich wspierają, również polscy. Na zebraniu odczytano list sędziego Murata Arslana. Napisał go z więzienia w Ankarze. Zapowiadająca to sędzia Dorota Zabłudowska mówiła: "Dużo jest nadziei na tej sali. Sędziowie tam nie tylko stracili pracę, ale i trafili do więzień. Murat jest w nim od kilku lat". ',
            'Jego list odczytał inny turecki sędzia Orhan Karabacak, który zdążył uciec z Turcji przed aresztowaniem. Zanim zaczął czytać powiedział do sędziów z Iustitii: "Staliście się pionierami w naszej walce. Uczymy się od was jak walczyć o niezależność sądownictwa. Staliście się wzorcami dla świata". ',
            'Murat w liście do polskich sędziów napisał m.in. "Jesteście latarnią, kagankiem nadziei oraz siły dla nas wszystkich, wasz udział zmienił nasze życie". Dziękował sędziom europejskim za nagłośnie sytuacji sędziów tureckich. By świat nie zamknął oczu na ich los. "Największą wartością jest utrzymanie prawa i sprawiedliwości do końca" - napisał Murat. Jego list, podobnie jak inne wystąpienia gości nagrodzono brawami na stojąco.',
            '[H] Sędzia Prusinowski: SN jest poobijany, przetrzebiony, ale nadal istnieje',
            'Potem przemawiali legalni sędziowie polskiego Sądu Najwyższego. Wprowadzenie zrobiła sędzia Dorota Zabłudowska: "W SN wszystko się zaczęło. Dzięki prezes [Gersdorf - red.] i sędziom SN przetrwał. Choć polityczne kierownictwo robi wszystko by zlikwidować niezawisłość. Ale póki są tam sędziowie niezależni i walczący o wartości, dopóty mamy Sąd Najwyższy". ',
            'Pierwszy głos zabrał prezes Izby Pracy i Ubezpieczeń Społecznych Piotr Prusinowski. Jest jednym z obrońców represjonowanych sędziów. Robi to z prezesem Izby Karnej Michałem Laskowskim i sędzią SN Jarosławem Matrasem. ',
            'Prusinowski mówił: "Sąd Najwyższy jest poobijany, przetrzebiony. Ale nadal istnieje. Nawet jeśli będzie z nas w SN tylko jeden sędzia, to z tego żaru będzie można w przyszłości wzniecić płomień". Dostał za to brawa. ',
            'Zadeklarował, że legalni sędziowie SN zawsze będę obrońcami sędziów ściganych na drodze dyscyplinarnej. "Nie zostaniecie sami, bo wartością jest wspólnota. Sędziowie powinni stanowić wspólnotę" - deklarował sędzia Prusinowski. Mówił, by nie kierować się pesymizmem. By być otwartym, pozytywnie myśleć, nie kalkulować. ',
            'Wspominał, że w latach 80 PRL-u ktoś przekazał mu maksymę, którą kieruje się do dziś. "Wiara wbrew nadziei. Takiej wiary nie można zniszczyć i zgasić. I nawet jeśli nastaną trudne czasy, to jeśli będziemy się tej wiary trzymać i mieć ją w sercu, to damy radę. Bo tak trzeba" - mówił sędzia Prusinowski.',
            'Była I prezes SN Małgorzata Gersdorf zaczęła od ukłonu w stronę Keesa Sterka. Podkreśliła, że przyjeżdżał aż dwa razy do Warszawy, tylko po to by wyrazić dla niej poparcie, gdy PiS chciał siłą usunąć ją ze stanowiska I prezes SN. Mówiła, że nie wiedziała, co zrobi władza, czy przyjdzie i ją po prostu wyniesie z SN. ',
            'Chwaliła sędziów za zaangażowanie w obronę praworządności i zachęcała do pozytywnego myślenia. "Nie można myśleć, że przyszłość będzie zła. Będzie fantastyczna, bo są młodzi, energiczni prokuratorzy i sędziowie. Tylko trzeba wierzyć, że będzie dobrze, trzeba tylko poczekać" - mówiła była I prezes SN. ',
            'Podkreślała, by nie bać się represji, bo specjalny rzecznik dyscyplinarny Piotr Schab też zrobił jej dyscyplinarkę. Za pozwolenie sędziom na przyjęcie historycznej uchwały pełnego składu SN ze stycznia 2020 roku, w której podważono neo-KRS i Izbę Dyscyplinarną. "Cieszę się, bo jestem w gronie najlepszych" - mówiła Gersdorf.',
            'Z kolei były prezes legalnej Izby Cywilnej Dariusz Zawistowski na przykładzie tej Izby pokazał jak w praktyce wyglądają rządy neo-sędziów SN. W jego Izbie jest ich już 15. Izbą kieruje też neo-sędzia Joanna Misztal-Konecka. Legalnych sędziów zostało 10. Zawistowski mówił: ',
            '"Kiedyś czekało się u nas rok na załatwienie sprawy, a teraz nawet trzy lata. Z miesiąca na miesiąc jest coraz gorzej. Na to złożyła się wadliwość procesu nominacyjnego sędziów [nominowanie przez neo-KRS neo-sędziów SN - red.]".',
            'Zawistowski przypomniał, że legalni sędziowie SN oparli się w 2018 roku kuszeniu przez władzę PiS przejściem na wcześniejszy stan spoczynku. A teraz neo-sędziowie chcą ich wciągnąć do wspólnego orzekania i wydawania wadliwych orzeczeń. "Ale do tej pory nie wydano żadnego orzeczenia w takich mieszanych składach" – zapewniał sędzia Zawistowski. Za co dostał brawa. ',
            'Głos zabrał jeszcze prezes Krajowej Rady Radców Prawnych Włodzimierz Chróścik, który zadeklarował poparcie dla sędziów. Podobnie prokurator Dariusz Korneluk ze stowarzyszenie niezależnych prokuratorów Lex Super Omnia. Korneluk mówił: "Na ciężkie czasy trzeba silnych ludzi. Sędziowie codziennie udowadniają, że są właściwymi ludźmi dla dzisiejszej Polski".',
            '[H] Sędzia z Ukrainy: 54 sędziów walczy na froncie',
            'Na Zebraniu głos zabrali jeszcze sędziowie ukraińscy, których wspierają polscy sędziowie. To Lev Kyshakevych z ukraińskiego Sądu Najwyższego i przewodniczący Rady Etycznej Ukrainy (organ ten ma czuwać nad prawidłowością procesu nominacyjnego sędziów). Kyshakevych dziękował za wsparcie i mówił, że sędziowie ukraińscy chcą budować nowoczesne sądy z polskimi sędziami. ',
            'Z kolei Olena Żuravska sędzia Sądu Okręgowego w Kijowie i członkini ukraińskiej KRS opowiadała, jak działają sądy w czasie wojny. Mówiła, że sądy cały czas pracują, choć były problemy ze światłem. Bo po ostrzałach rosyjskimi rakietami infrastruktury energetycznej, były przerwy w dostawach prądu. Czasem był on tylko 2-3 godziny dziennie. I w takich warunkach toczyły się rozprawy. ',
            'Przez rok wojny sądy rozpoznały 2,5 miliona spraw, w tym w SN 90 tysięcy. Mówiła, że zapadają pierwsze wyroki o zbrodnie wojenne. I nawiązano współpracę z Międzynarodowym Trybunałem Karnym w Hadze, by dopilnować, by każdy zbrodniarz poniósł odpowiedzialność. ',
            'Wyliczała, że rosyjscy zbrodniarze zniszczyli 90 budynków sądów, a 54 sądy znalazły się na terytoriach tymczasowo okupowanych przez Rosję. Mówiła że sędziowie trafiają do niewoli i walczą na froncie. Mundur założyło 54 sędziów. Walczy też 326 pracowników sądowych. Zapewniała, że Ukraina chce zreformować swoje sądy. Kończąc powiedziała: "Slava Ukraini". Oboje dostali duże brawa na stojąco.',
            'Na koniec sobotniego Zebrania Iustitii głos zabrała szefowa stowarzyszenia Votum, które skupia absolwentów i aplikantów Krajowej Szkoły Sądownictwa i Prokuratury. To głównie młodzi neo-sędziowie, którzy weszli do sądów po ukończeniu KSSiP. ',
            'Wystąpienie szefowej Votum Aleksandry Sinieckiej-Kotuli było zaskoczeniem, bo Votum często wchodzi w polemikę z sędziami z Iustiii, broniąc swoich nominacji od nielegalnej neo-KRS. Iustitia w swoim projekcie ustawy robi jednak dla nich wyjątek. Nie chce automatycznie cofać ich nominacji, tylko poddać je weryfikacji. ',
            'Szefowa Votum w swoim wystąpieniu broniła nominacji dla neo-sędziów. Jest przeciwna weryfikacji. Jej zdaniem będzie to uderzać w zasadę nieusuwalności sędziów. "To będzie precedens, kolejna władza może to wykorzystać" - mówiła. Skrytykowała propozycje Iustitii w tym zakresie. Ostrzegała, że będzie to gaszenie pożaru benzyną. Apelowała też, by nie nazywać ich neo-sędziami. ',
            'Dlaczego Iustitia zaprosiła ją na swoje zebranie? Prezes Markiewicz zapewniał, że stowarzyszenie jest otwarte na dialog. Otwiera się również na to środowisko. Dlatego na Zebraniu zmieniono statut Iustitii, tak by członkami mogli zostać asesorzy sądowi. A są nimi właśnie absolwenci KSSiP.', ]
        out_lines = re.sub(r"\n+", "\n", output.content).split('\n')
        self.assertListEqual(lines, out_lines)

        self.assertListEqual([], output.links)

    def test_polityka_1(self):
        input_file_path: Path = Path(".") / """
        polityka1_„Franciszkańska 3” Marcina Gutowskiego. Karol Wojtyła wiedział o złu w Kościele. Dorabianie usprawiedliwień jest kolejnym złem.html
        """.strip()

        with open(input_file_path, encoding='utf-8') as f:
            file_content = f.readlines()
            parser_input = ''.join(file_content)
        parser = PolitykaHTMLParser()
        parser.feed(parser_input)
        output: OutputData = parser.output

        self.assertEqual("Karol Wojtyła wiedział o złu w Kościele. Dorabianie usprawiedliwień jest kolejnym złem",
                         output.title)
        self.assertEqual("Adam Szostkiewicz", output.author)
        self.assertEqual(date(2023, 3, 7), output.pub_date.date())
        self.assertEqual(date(2023, 3, 7), output.last_updated.date())
        self.assertEqual('utf-8', output.charset)
        self.assertEqual("", output.description)

        lines = [
            'Właśnie ukazał się reportaż "Franciszkańska 3" Marcina Gutowskiego. Wszystkie przedstawione w nim przykłady są bulwersujące. Mało prawdopodobne, by dzisiaj Kościół w Polsce stanął w prawdzie w tej sprawie, choć głosi, że tylko ona wyzwala.',
            'Poważna sprawa wymaga poważnego podejścia. Takim podejściem wykazał się Marcin Gutowski w reportażu śledczym pod tytułem "Franciszkańska 3" zrealizowanym dla TVN24. Pokazał, że Karol Wojtyła[L1] jeszcze jako zwierzchnik Kościoła krakowskiego wiedział o pedofilach w jego szeregach i tej wiedzy nie wykorzystał tak, jak należało się spodziewać. Miał wiele możliwości. Mógł skierować ich sprawy do kościelnego sądu, oczekując ekskomuniki, czyli wyłączenia ze wspólnoty wierzących i wydalenia ze stanu kapłańskiego. Wybrał drogę, która wpisuje się w strategię tego, co dziś nazywamy kościelną subkulturą omerty, czyli systemowego tuszowania zła, jakim jest krzywdzenie dzieci i molestowanie kleryków przez osoby duchowne.',
            '[H] Drapieżca promował drapieżcę',
            'Dorabianie do tego zła usprawiedliwień jest kolejnym złem. Nie godzi się usprawiedliwiać tego zła pretekstami historycznymi. Owszem, wiarygodność dokumentów i relacji należy weryfikować, biorąc pod uwagę kontekst polityczny. Dokumenty tajnej policji politycznej z czasów PRL wymagają analizy nie tylko dziennikarskiej, lecz także eksperckiej. To powinien być następny krok w wyjaśnianiu sprawy. Na etapie dziennikarstwa śledczego reportaż Marcina Gutowskiego dochował standardów.',
            'Pełne wyjaśnienie powinno objąć również dokumenty na temat księży krzywdzicieli w archiwach kościelnych. W tym przypadku przede wszystkim archiwum kurii krakowskiej. Jest to jednak w obecnej sytuacji politycznej niemożliwe. Kościół odmawia, a odpowiednie władze świeckie, w tym prokuratura, są mu powolne. W Kościołach w Europie Zachodniej, w Niemczech czy Francji, a także w USA, ten dostęp jest możliwy. Może kiedyś i u nas będzie, a wtedy niezależna od władz kościelnych i politycznych komisja ekspertów będzie mogła postawić drugi krok.',
            'Na razie mamy obraz niepełny. Ale choćby przypadek ks. Bolesława Sadusia już teraz pokazuje, że kardynał Wojtyła działał w jego sprawie zgodnie z zasadą omerty. Nie tylko wysłał krzywdziciela do Austrii, ale poprosił ówczesnego wiedeńskiego arcybiskupa Franza Königa o pomoc, nie informując go szczegółowo o okolicznościach. Na domiar złego miał się konsultować z Sadusiem w sprawie następcy kard. Königa. Ks. Saduś wskazał zakonnika Hansa Groëra, który po latach został oskarżony o molestowanie kleryków na masową skalę. Drapieżca promował drapieżcę, Jan Paweł II[L2] podjął decyzję po jego myśli.',
            '[H] Demitologizacja trwa',
            'Wszystkie przykłady przedstawione w reportażu są bulwersujące; wątek ks. Sadusia, na dodatek współpracownika SB, wydaje się szczególnie wymowny, jeśli chodzi o postawę kard. Wojtyły. Oczywiście czasy były politycznie i kulturowo inne, lecz to nie usprawiedliwia przyszłego świętego. Tolerowania zła w instytucji, która głosi dobro i przedstawia się jako najwyższa inkarnacja dobra, nie dało się i nie da obronić. Tak wtedy, jak teraz krzywdzenie dzieci i młodzieży jest złem, na które trzeba reagować i które trzeba ukarać. Karol Wojtyła był świadom, że w Kościele istnieje zło, ale pozwolił mu działać. Kapłan, który krzywdzi bezbronne istoty ludzkie, nie zasługuje na wysoki status społeczny, jakim tradycyjnie cieszą się duchowni. Kościół, który takich kapłanów chroni przed karą, a ich ofiary spycha na plan dalszy lub ignoruje, nie zasługuje na szacunek.',
            'Pamiętam, jak pod kurią na Franciszkańskiej 3 radosny tłum skandował podczas pierwszej wizyty Jana Pawła II: "dziękujemy, zostań z nami!". I jak wiele lat później pod tym samym "papieskim oknem" szedł tłum protestujący przeciwko drakońskim obostrzeniom w "obronie życia", które doprowadziły do śmierci Izabeli z Pszczyny. Budynek był na głucho zamknięty. To może być symbol, jak bardzo zmieniło się społeczne postrzeganie roli Kościoła i samego papieża Karola Wojtyły.',
            'Trwa demitologizacja zarówno Kościoła, jak i Jana Pawła II. To proces dla wielu katolików bolesny. Rodzi smutek, a czasem odmowę i agresję. Ale daje też szansę prawdziwego oczyszczenia i prawdziwej odnowy. Mało prawdopodobne, by dzisiaj Kościół w Polsce stanął w prawdzie w tej sprawie, choć głosi, że tylko ona wyzwala. A bez zmiany postawy Kościoła odnowy nie będzie.',
        ]
        out_lines = re.sub(r"\n+", "\n", output.content).split('\n')
        self.assertListEqual(lines, out_lines)

        self.assertListEqual([
            'https://www.polityka.pl/tematy/karol-wojtyla',
            'https://www.polityka.pl/tematy/jan-pawel-II',
        ], output.links)

    def test_wyborcza_1(self):
        input_file_path: Path = Path(".") / """
        wyborcza1_Jacek Dehnel do Marcina Matczaka Wierzący nie wierzą w niewierzących.html
        """.strip()

        with open(input_file_path, encoding='iso-8859-2') as f:
            file_content = f.readlines()
            parser_input = ''.join(file_content)
        parser = WyborczaHTMLParser()
        parser.feed(parser_input)
        output: OutputData = parser.output

        self.assertEqual("Jacek Dehnel do Marcina Matczaka: Wierzący nie wierzą w niewierzących",
                         output.title)
        self.assertEqual("Jacek Dehnel", output.author)
        self.assertEqual(date(2023, 1, 5), output.pub_date.date())
        self.assertEqual(date(2023, 1, 5), output.last_updated.date())
        self.assertEqual('iso-8859-2', output.charset)
        self.assertEqual("", output.description)

        lines = [
            'Z niejaką przyjemnością obserwuję dyskusję wokół felietonu – z tajemniczych przyczyn nazywanego przez autora "esejem" – Marcina Matczaka o wyższości świąt, które mu się podobają, nad świętami, które mu się nie podobają[L1]. Potwierdza ona bowiem moje głębokie przekonanie, że wierzący są w stanie uwierzyć w cokolwiek, tylko nie w istnienie niewierzących.',
            'Religijnym i postreligijnym Polakom – abstrahuję od tego, na ile ta religijność jest faktycznie przeżyciem metafizycznym, a na ile kulturową tożsamością – nie mieści się w głowie, że istnieją ludzie, którzy nie mają potrzeb religijnych, nie "poszukują boga", nie cierpią z powodu "braku łaski wiary", nie drżą przed żadnymi sądami ostatecznymi ani gniewem bóstw. Niedawno ultraprawicowiec, monarchista i piewca Putina Adam Wielomski napisał: "Lewak nie boi się Boga i Sądu Ostatecznego. Boi się ocieplenia klimatu". I najwyraźniej wydaje mu się to ogromnie zabawne i paradoksalne, że jacyś ludzie nie drżą przed mityczną postacią, tylko przed problemami rozpędzającymi się do wymiarów apokalipsy realnej, nie literackiej.',
            'No więc tak właśnie jest i nie jest to żaden paradoks.',
            '*',
            'Jednak to przekonanie o konieczności sacrum, że "wszyscy w coś wierzą", "ateizm to też forma wiary", że wszyscy jesteśmy tacy sami i mamy takie same potrzeby, jest rozpowszechnione od ultraprawicy po liberalne centrum, a może i dalej. Tymczasem pora przyjąć, że się od siebie na najrozmaitsze sposoby różnimy.',
            'Jasne, nie dziwię się, że Piotrowi Augustyniakowi "brakuje sacrum"[L2] – jest byłym dominikaninem, który u innego dominikanina doktoryzował się na Papieskiej Akademii Teologicznej ze średniowiecznego mistyka. Do odczuwania tego braku został wychowany i sam się do tego wychował, nawet jeśli potem podjął inne decyzje życiowe. Ma bóle fantomowe. Nie powinien ich jednak projektować na innych.',
            'Krytykom Matczaka zarzuca, że nie znają Baudrillarda i Baumana, że nie dostrzegają komercji. Ależ dostrzegamy, wiemy też, że królowa Bona umarła. Nie jest to dla nas nic nowego. Znacznie ciekawsze wydaje mi się, kiedy Augustyniak snuje wizję przeszłości, kiedy to ludzie z okazji świąt "poszukiwali w sobie i wokół siebie >>innego wymiaru<<".',
            'Chciałbym bowiem zadać pytanie: kiedy, przepraszam, były te złote czasy, kiedy to ludzie naprawdę czekali w adwencie na przyjście bóstwa? Nie mówię oczywiście o jednostkach – bo i oni o nich nie mówią – tylko o ogólnospołecznym przeżyciu. Za czasów Bacha? Za czasów Mickiewicza? W latach 80., czasach mojego dzieciństwa? Za wcześniejszego PRL-u? W międzywojniu, w miejskiej klasie średniej – wtedy znacznie mniej licznej – do której dzisiejszego odpowiednika adresuje swoje lamenty Matczak? Może na zabitej deskami wsi w latach zaborów, a niechby gdzieś i międzywojennych, kiedy wierzono jeszcze, że Maria za prowadzenie żniw w święto Wniebowzięcia zrzuca z nieba węże. Tyle że do tego świata nie ma powrotu bez przywrócenia analfabetyzmu i biedy na granicy śmierci głodowej.',
            'Kiedy to te święta, święta pełnej komory, jeszcze przed przednówkiem, kiedy w polu się nie robi i siedzi się przy ogniu, konsumując zapasy z lata i jesieni, kiedy te święta oparte na wspólnym ucztowaniu, były niekonsumpcyjne? Zakres dat bym prosił.',
            'Obawiam się bowiem, że dawno, a właściwie nigdy. Co było orgią konsumpcyjnego rozpasania w średniowieczu, kiedy nie było złowrogich galerii handlowych i bezbożnych reklam w telewizji? Jarmarki z okazji rozmaitych świąt kościelnych, powiązane z odpustami i pielgrzymkami.',
            'Wychowałem się w Gdańsku, gdzie po dziś dzień co roku setki tysięcy miejscowych i turystów nurzają się w konsumpcji na Jarmarku Dominikańskim. Ponad 750 lat temu papież Aleksander IV ustalił go bullą na prośby dawnych współbraci Piotra Augustyniaka, żeby ściągnąć wiernych na odpustową mszę w dniu św. Dominika. No ale tamta konsumpcja nie była taka straszliwa, skoro sypała dukaty do kiesy klasztoru, prawda? ',
            '*',
            'Dodam może, że to katolickie narzekanie na konsumpcjonizm uroczystości jest paradne nie tylko w przypadku świąt. Podobnie jest z pierwszą komunią: najpierw celowo i cynicznie zrobiono wokół niej indoktrynacyjny cyrk z prezentami, bo tak dzieci łatwiej wepchnąć w religijne koleiny, a potem się narzeka, że interesują je prezenty, a nie "przeżycie duchowe".',
            'Powiedziałbym na to: "Trzeba było się skupić na przeżyciu duchowym, a nie atrakcyjnych łapówkach i księżniczkowych sukniach bezach, to może byłoby inaczej". Ale bym się mylił.',
            'Dawno temu i ja "przystępowałem" w pożyczonym granatowym garniturku dziecięcym. Potem był jakiś cały tydzień chodzenia w tych strojach (dla utrwalenia i dla przedłużenia konsumpcji, bo przecież jak się już tę księżniczkową bezę ma, jak się już ten garniaczek pożyczyło czy kupiło, to bez sensu tylko raz poszpanować). Któregoś dnia, wracając z kościoła, zostałem zaczepiony przez jakichś starszych chłopaków i zapytany, co takiego dostałem na komunię, co za skarby przypadły mi w tej loterii fantów, zegarków, rowerów, gierek, w tej konsumpcyjnej bonanzie. A ja, naiwny dziewięcioletni idealista, powiedziałem im, że "liczy się przeżycie" – czym, jak można się było spodziewać, wzbudziłem wesołość czternastoletnich cyników (prawdę mówiąc, wcale tej komunii szczególnie nie przeżywałem, ale chwalenie się albumem o papieżu też nie podbiłoby moich akcji na blokowisku).',
            'Dziś, kiedy na naszych oczach katolicka hegemonia się rozpada, wiem, że to oni mieli rację. Wielu ludzi posyła dziś dziecko do komunii nie tylko przez presję ze strony dziadków, ale właśnie z uwagi na ową orgię konsumpcji, z której ich córka czy syn musieliby zostać wykluczeni. Konsumpcja jest ostatnim bastionem Kościoła – po pierwszej komunii, jak wiemy, rodzice masowo wypisują dzieci z lekcji religii. Więc nie ma co lać krokodylich łez.',
            '*',
            'Wróćmy jednak do tych, którzy nie potrafią uwierzyć, że komuś religia nie jest potrzebna. "My, spadkobiercy idei Oświecenia – zaczyna z kolei swój tekst Wojciech Maziarski[L3] – od pokoleń próbujemy znaleźć świecką alternatywę dla religii – i za każdym razem kończy się to porażką. Nie ma się co obrażać, tak po prostu jest".',
            'I znów: głębokie nieporozumienie. Owszem, XVIII-wieczni rewolucjoniści próbowali wprowadzić kult Rozumu, bo nie wyobrażali sobie świata bez jakiejś formy religii. Ale żyjemy prawie ćwierć tysiąclecia później. W mieście, w którym od niedawna mieszkam, Berlinie, dwie trzecie ludzi jest niewierzących, a ulice nie są pełne ludzi poszukujących bóstw czy spierających się o teologię jak w "Baudolinie" Eco. Za to jarmarki bożonarodzeniowe mają się świetnie.',
            'Wchodziliśmy w Oświecenie z religią, astrologią, magią i alchemią. Pierwsza, choć coraz słabiej, jeszcze się trzyma. Ale czy w związku z tym "próbujemy znaleźć alternatywę dla astrologii, magii i alchemii"? Niespecjalnie. Godzimy się po prostu z tym, że w naszym społeczeństwie są ludzie uważający, że Marek zdradził Martynę, ponieważ ma ascendent w Raku, albo że Ziuta ma pecha, bo urodziła się w schyłkowym Wodniku. Oraz z tym, że w szkole któraś z matek nalega, żeby dziecku nie zdejmowano z szyi ametystu, bo to kryształ wspomagający uczenie literek. Tylko alchemię wszyscy już chyba zarzucili. I nikt po niej nie płacze.',
            'Maziarski pisze, że jest "przekonany, że spora część mieszkańców świata postchrześcijańskiego odczuwa bóle fantomowe po dawnych wierzeniach i towarzyszących im ceremoniach". Przekonanie o czymś oczywiście nie jest żadnym argumentem – tu przydałyby się jakieś badania, konkrety, dowody.',
            'Nic bowiem nie wskazuje na to, żeby ceremonie nie mogły żyć dalej własnym życiem bez oryginalnego "wsadu metafizycznego". Prawie wszyscy siedzieliśmy przy wigilii z dodatkowym talerzem "dla wędrowca", podczas gdy jest to miejsce dla duchów przodków, które zostało nam ze słowiańskich obrzędów. Czy ktoś w związku z tym, kładąc dodatkowe nakrycie, odczuwa straszliwe bóle po braku żertwy dla duchów? A może, kładąc sianko, rozpacza, że przy okazji nie pokłonił się bóstwu zboża i pól Simargłowi? Wątpię. Skoro przez ostatnich kilka pokoleń Jezus, centralne bóstwo chrześcijaństwa, został z własnych urodzin praktycznie wyparty przez synkretycznego Świętego Mikołaja, to znaczy, że po raz kolejny kultura znakomicie sobie radzi z przemianami świata.',
            ' *',
            'W swoim niepowtarzalnym stylu Wojciech Maziarski wspominał też "o strzelaniu do Matczaka" oraz "zakrzykiwaniu, uciszaniu, psychicznym terroryzowaniu, a w końcu represjonowaniu". Wolne żarty. Autora rzekomego "eseju" nikt nie represjonuje, a tym bardziej do niego nie strzela. Jest to równie fikcyjne, co fantazje Matczaka o "przytulanych gejach" i ludziach wyrzucanych z domu za to, że są katolikami [L4](swoją drogą, trzeba mieć iście święcony tupet, żeby tak napisać w kraju, gdzie katolicy wszędzie włażą z kaloszami, a młode elgiebety są wyrzucane z domów na tyle często, że trzeba było dla nich stworzyć specjalne hostele interwencyjne, żeby ich ratować od bezdomności i samobójstw).',
            'Matczak został po prostu obiektem srogich żartów. Nie za niewinność, bo koncertowo się podłożył. Śmieszne jest to, co wspomniałem przed chwilą, śmieszne jest też, kiedy ktoś najpierw wymyśla społeczeństwu, że nie pracuje po szesnaście godzin dziennie, a potem wymyśla mu od "biednych wypalonych maszyn do pracowania w dni robocze[L5]".',
            'Tam, gdzie Matczak pisze, że "ateistyczne święta to samooszukiwanie się człowieka zagubionego w sekularnym do cna świecie", oczywiście błądzi. W świecie zsekularyzowanym ateiści mają się znakomicie, nie muszą oszukiwać ani samych siebie, ani innych, udając nabożność czy przejmowanie się religią. Mam raczej wrażenie, że to sam autor jest zagubiony, bo nasze społeczeństwo zaczęło się oddolnie i nieśmiało sekularyzować i nie kupuje już wizji państwa wyznaniowego, gdzie religijna większość narzuca całej reszcie, jak ma żyć – w tym jak ma obchodzić święta. Przy czym piętnowani za niewłaściwe użycie przesilenia zimowego są tu nie tylko ateiści, ale i ci, którzy nominalnie wierzą, ale się zeświecczają. Równia pochyła, od rzemyczka do koniczka: w tym roku za bardzo skupisz się na jedzeniu kutii, to za rok pomyślisz, że może Darwin miał rację z tą ewolucją, a za dwa zrobisz apostazję.',
            'Ale pomijając już, że jego "esej" jest śmieszny i obraźliwy dla ateistów, którym katolik Matczak obwieszcza, że ich święta to "nędzna proteza" – jest on również nie do obronienia poznawczo. Jeśli bowiem obrać go z ozdobników i – lepszych czy gorszych – streszczeń Hana, Matczak nie przeprowadza klasycznego wywodu, który, poprzez poparte danymi argumenty, doprowadza nas do wiedzy czy choćby interesującego punktu widzenia. Jest to raczej kiepsko sklejona zbieranina sylogizmów i obiegowych narzekań, ułożonych pod z góry określoną – a także doskonale nam znaną i uniwersalną – tezę: "Kiedyś to były, panie, czasy, a teraz nie ma czasów".',
            'Retorycznie wygląda to dość prosto: Marcin Matczak zestawia ze sobą trzy różne dychotomie, rozdzielając je ściśle między dwie kolumny, kolumnę dobra (to, co mu się podoba) i zła (to, co mu się nie podoba). Są to: religijność/ateistyczność, wspólnotowość/osobność, przeżycie/konsumpcjonizm. Święta dobre są religijne, wspólnotowe, przeżywane, a złe – ateistyczne, osobne, konsumpcyjne.',
            'Jest to na wiele sposobów nie tylko prostackie jak propagitowy plakat, ale też niezgodne z naszym życiowym doświadczeniem. ',
            '*',
            'Po pierwsze, te podziały są nieostre.',
            'Owszem, ateizm wyklucza się z religijnością, ale już nie z wczuwaniem się w pochodzące z różnych źródeł wigilijne opowieści. Najdłuższa, ciemna noc, od której zaczyna przybywać światła, co zwiastuje pierwsza gwiazdka; noc, w którą obdarzone nadnaturalną mocą dziecko biedaków rodzi się w żłobie; noc, w którą dobry mag leci po niebie saniami zaprzężonymi w renifery i zrzuca wszystkim prezenty; noc, w którą każde zwierzę może przemówić ludzkim głosem – to są dobre opowieści.',
            'Nie trzeba w nie wierzyć, żeby je przeżywać (podobnie jak w operze nie musimy wierzyć, że realna, historyczna Violetta naprawdę umiera, żeby się wzruszyć do łez na "Traviacie") – te cztery historie, pierwsza wzięta z astronomicznej rzeczywistości, druga z bliskowschodniej mitologii chrześcijańskiej, trzecia będąca produktem amerykańskiej reklamy, luźno opartej na postaci pewnego biskupa, czwarta wzięta z folkloru, po prostu działają.',
            'Idźmy dalej. Co z podziałem konsumpcja/przeżywanie? Jednym z moich najgłębszych przeżyć świątecznych było – jest nadal – przeżycie zdecydowanie konsumpcyjne: to, że dostaliśmy kiedyś z bratem pod choinkę statek piracki LEGO. Wówczas było to dla mnie absolutnie olśniewające, po latach doceniam to również mocno, ale z zupełnie innych przyczyn, bo jako dorosły wiem, jakim wyrzeczeniem dla moich rodziców było wówczas, na przełomie lat 80. i 90., kupienie nam tak drogiej zabawki.',
            'Więcej: konsumpcja, i to ta najbardziej ścisła, wspólne jedzenie, wspólne ucztowanie, wspólne żarcie, znajduje się w absolutnym centrum religijnej symboliki. Również katolickiej. Msza to "przystąpienie do stołu Pana", komunia to wspólne jedzenie i picie na pamiątkę ostatniego dużego posiłku Jezusa. Więcej: Jezus jest "barankiem paschalnym" – czyli kulinarnym gwoździem programu najważniejszej corocznej uczty w żydowskiej tradycji. To mniej więcej tak, jakbyśmy teraz zakładali w Polsce religię i nazwali nasze nowe bóstwo "bożonarodzeniowym bigosem" czy, ostatecznie, "niedzielnym schabowym". Nie tak daleko stąd do Latającego Potwora Spaghetti.',
            'Wreszcie podział trzeci, na wspólnotowe i osobne. Otóż dla wielu z nas wspólnoty, do których należymy, są krzywdzące i opresyjne. I właśnie dlatego święta coraz częściej stają się czasem, kiedy celebrujemy bliskość i zacieśniamy wspólnoty – ale nie te z genealogicznego rozdania, tylko z wyboru.',
            'Mam przyjaciół, dla których wcześniejsze czy późniejsze "nierodzinne wigilie" są ważniejsze niż spotkanie w wieczór 24 grudnia z zachlanym wujkiem, babką napastliwą dewotką i bratem, który właśnie wyszedł z więzienia (wszystko przykłady z życia wzięte). Albo z rodzicami, którzy powinni się byli rozwieść dwadzieścia lat temu, a zamiast tego prowadzą ze sobą wojnę podjazdową, w której nie biorą jeńców. I prowadzili ją przez wszystkie minione święta, które całej rodzinie od tego stają ością w gardle jak karp w galarecie.',
            'Czy zatem – zapytajmy – działa osobnie, a nie wspólnotowo ktoś, kto decyduje się na święta bez rodziny, za to na przykład z ulubioną przyjaciółką ze studiów i jej synem, wychowującym się bez ojca, czy, dajmy na to, z trzema byłymi i ich aktualnymi, którzy nie mogą znieść swoich rodzin (albo też, również przykład z życia, zostali z nich wyrzuceni – nie, nie za bycie katolikami)? Jeśli są to dla nich wspólnoty realne i niekrzywdzące, czemu mieliby z nich rezygnować na rzecz tradycyjnej wspólnocie rodzinnej, z całym jej negatywnym bagażem?',
            'A zatem nieufnie podchodzę już do samych tak nakreślonych dychotomii – ale tekst Matczaka jest nieuczciwy podwójnie, autor bowiem układa je w dwie kolumny, schemat o subtelności cepa. To jest już kompletnie dowolne, bazujące na jego własnych przesądach.',
            'Tymczasem święta mogą być ateistyczne lub religijne, konsumpcyjne lub przeżyciowe, wspólnotowe lub samotne i możliwe są pomiędzy nimi dowolne kombinacje.',
            'Matczak, Augustyniak i Maziarski zdają się wierzyć w świat, w którym religijna, bogobojna rodzina zbiera się w duchu miłości i wzajemnego zaufania, żeby wspólnie świętować bycie razem, opromieniona nadprzyrodzonym blaskiem; szacowny ojciec czyta rozdział z Ewangelii, dziatki głęboko przeżywają uniesienie pastuszków, nie dbając wcale o prezenty pod choinką, a cała rodzina nie kłóci się o politykę, tylko przemawia do siebie serdecznym rymem częstochowskim.',
            'Tyle że ten świat nigdy – poza komercyjnym XIX-wiecznym oleodrukiem – nie istniał. Nawoływanie "Make Christmas Great Again" wyrasta z tego samego konserwatywnego resentymentu co Trumpowskie "Make America Great Again" – i, podobnie jak ono, zestawione z realną historyczną przeszłością okazuje się kompletną fikcją.',
        ]
        out_lines = re.sub(r"\n+", "\n", output.content).split('\n')
        self.assertListEqual(lines, out_lines)

        self.assertListEqual([
            'https://wyborcza.pl/magazyn/7,124059,29283876,marcin-matczak-chrzescijanskie-symbole-tych-swiat-nie-sa-latwe.html',
            'https://wyborcza.pl/magazyn/7,124059,29320323,czyzby-krytycy-matczaka-nie-czytali-nigdy-baudrillarda-nie.html?_ga=2.54358958.723520771.1672739956-1468685601.1671409070',
            'https://wyborcza.pl/7,75968,29320395,nie-strzelajcie-do-matczaka-tylko-przeczytajcie-jeszcze-raz.html',
            'https://wyborcza.pl/magazyn/7,124059,29302507,marcin-matczak-przytulicie-znajomego-ktory-wyzna-ze-jest.html',
            'https://wyborcza.pl/magazyn/7,124059,28804796,matczak-moze-moja-boomerska-wizja-samodoskonalenia-sie-i-postepu.html',
        ], output.links)


if __name__ == '__main__':
    root = logging.getLogger()
    root.setLevel(logging.CRITICAL)

    unittest.main()
