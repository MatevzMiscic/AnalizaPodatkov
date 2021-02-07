# Analiza takmovanj na Codeforces

Analiziral sem nekaj tekmovanj na [Codeforces](https://codeforces.com).  

Na spletni trani codeforces so pogosto tekmovanja, na katerih tekmujejo programerji iz celega sveta. Na vsakem tekmovanju je nekaj nalog, ki jih morajo tekmovalci rešiti. To naredijo tako, da napišejo ustrezno kodo, ki jo zahteva naloga, in to kodo oddajo.

## Podatki

Analiziral sem rezultate na nekaterih tekmovanjih na codeforces. Od zadnjih 200 tekmovanj sem vzel tiste, ki zadoščajo nekemu formatu (morajo biti individualna ipd.), zato da lahko rezultate primerjamo.

Za vsakega **uporabnika**, ki je bil na katerem od obravnavanih tekmovanj, sem zajel:
* uporabniško ime
* rang (glede na codeforces rangiranje)
* državo iz katere je

Za vsako **nalogo** imamo shranjeno tekmovanje, na katerem se je pojavila, in zaporedno številko naloge na tem tekmovanju.

Za vsako uspešno **oddajo** imamo podane naslednje podatke:
* tekmovalec, ki je naredil oddajo
* naloga h kateri spada ta oddaja
* programski jezik
* čas od začetka tekmovanja

Poleg tega je za vsakega uporabnika in vsako tekmovanje, ki se ga je udeležil, zajeta še njegova uvrstitev na tem tekmovanju.

## Hipoteze

Cilj naloge je ovreči ali potrditi naslednje **hipoteze**:
* Najboljši tekmovalci prvo nalogo rešijo v manj kot 10 minutah
* Več kot 80 % od vseh oddaj je v jeziku c++, manj kot 5 % pa v pythonu
* Tekmovalci, ki so bili na več tekmovanjih, so bolši kot tisti, ki so bili na manj tekmovanjih

Poleg tega so nekoliko bolj podrobno obravnavans tudi naslednja vprašanja:
* Iz katerih držav so najboljši programerji?
* Ali obstaja povezava med tem, kako hitro nek tekmovalec rešuje lahke naloge in tem, kako težke naloge je sposoben rešiti?
* Kako udeležba na tekmovanjih vpliva na uspeh na tekmovanjih?

