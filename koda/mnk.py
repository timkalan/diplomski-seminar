"""
V tej skripti bo implementirana igra in agent, ki se bo v njej naučil 
igrati "križce in krožce" oz. posplošeno m,n,k-igro. (m * n plošča, 
želimo k simbolov v vrsto).
"""

# za hitrejše matrike
import numpy as np
import pickle
import os
# import numba as nb

VRSTICE = 3
STOLPCI = 3
V_VRSTO = 3
# GRAVITACIJA = False

KRIZCI = 1
KROZCI = -1

NAGRADA_ZMAGA = 1
NAGRADA_REMI = 0
NAGRADA_PORAZ = -1


# Funkcije pomagači
def ponovitve(seznam, simbol, st_ponovitev=V_VRSTO):
    """
    Funkcija v seznamu poišče, če se simbol kje ponovi st_ponovitev-krat.
    Uporabljeno pri metodi zmagovalec, da je bila posplošena na nxn plošče.
    """
    i = 0
    while i < len(seznam):
        if seznam[i] == simbol:
            if [seznam[i]] * st_ponovitev == seznam[i:i+st_ponovitev]:
                return simbol
                break
        i += 1



class Okolje:
    """
    Okolje predstavlja igralno ploščo. Vsebuje vsa pravila igre. To je:
    nastavi igralce, izrisuje, dobiva stanja, gleda legalne pozicije, 
    igra, sodi, daje nagrade.
    """

    def __init__(self, p1, p2):
        """
        Naredimo igralno ploščo kot "array" ustrezne velikosti in dimenzij, 
        shranimo igralca, 
        povemo, da igre ni konec, 
        nastavimo trenutno stanje na None in 
        povemo, kdo bo prvi igral. 

        p1 = član razreda Agent ali Clovek (p2 podobno)
        """
        self.plosca = np.zeros((VRSTICE, STOLPCI), dtype='int64')
        self.p1 = p1
        self.p2 = p2
        self.konec = False
        self.stanje = None
        self.simbol = KRIZCI    # arbitrarna odločitev


    def __str__(self):
        """
        Funkcija za izris plošče na terminal.
        """
        natis = '\n' + f'{"-" * (STOLPCI * 4 + 1)}' + '\n'
        for i in range(VRSTICE):
            for j in range(STOLPCI):
                if self.plosca[i, j] == KROZCI:
                    natis += '| ' + 'O' + ' '
                # za lepši izris dodamo presledek
                elif self.plosca[i, j] == KRIZCI:
                    natis += '| ' + 'X' + ' '
                else:
                    natis += '| ' + ' ' + ' '
            natis += '|' + '\n' + f'{"-" * (STOLPCI * 4 + 1)}' + '\n'
        return natis


    def ponastavi(self):
        """
        Funkcija, ki ponastavi igralno okolje na začetno vrednost.
        """
        self.plosca = np.zeros((VRSTICE, STOLPCI), dtype='int64')
        self.konec = False
        self.stanje = None
        self.simbol = KRIZCI


    def pridobi_stanje(self):
        """
        Pridobi trenutno stanje igralne plošče in ga shrani kot 
        enodimenzionalni seznam.
        """
        self.stanje = str(self.plosca.reshape(VRSTICE * STOLPCI))
        return self.stanje


    # morda prepiši to z numpy
    def legalne_pozicije(self):
        """
        Poišče vse legalne pozicije - torej prazna polja, 
        znotraj meja igralne plošče.
        """
        pozicije = []
        for i in range(VRSTICE):
            for j in range(STOLPCI):
                if self.plosca[i, j] == 0:
                    # pozicijo shranimo kot nabor
                    pozicije.append((i, j))
        return  pozicije


    # mogoče prepiši v naravne indekse?
    def igraj(self, pozicija):
        """
        Preveri, če je pozicija na seznamu legalnih, in če je, nanjo vpiše 
        simbol trenutnega aktivnega igralca, po uspešni vložitvi pa 
        simbol zamenja.

        pozicija = nabor oblike (x koordinata, y koordinata)
        (POZOR: prvi indeks je 0 (in ne 1))
        """
        if pozicija in self.legalne_pozicije():
            self.plosca[pozicija] = self.simbol
            
            # zamenjamo igralca po vsaki potezi
            self.simbol = KRIZCI if self.simbol == KROZCI else KROZCI
        else:
            print('To ni legalna pozicija!')


    def zmagovalec(self):
        """
        Preveri, če imamo zmagovalca in vrne njegovo številko. 
        V primeru remija vrne 0. Prav tako pove okolju, da je
        igre (epizode) konec. Z uporabo funkcije pomagača deluje 
        za poljubno velike plošče, kjer je m == n.
        """
        # vrstice
        for i in range(VRSTICE):
            if ponovitve(list(self.plosca[i, :]), 1):
                self.konec = True
                return 1
            if ponovitve(list(self.plosca[i, :]), -1):
                self.konec = True
                return -1
                
        # stolpci
        for i in range(STOLPCI):
            if ponovitve(list(self.plosca[:, i]), 1):
                self.konec = True
                return 1
            if ponovitve(list(self.plosca[:, i]), -1):
                self.konec = True
                return -1

        # diagonale
        if (V_VRSTO <= VRSTICE) or (V_VRSTO <= STOLPCI):
            diag1 = [self.plosca[j, j] for j in range(min(VRSTICE, STOLPCI))]
            diag2 = [np.flip(self.plosca, axis=1)[j, j] for 
                    j in range(min(VRSTICE, STOLPCI))]

            for i in range(max(VRSTICE, STOLPCI)):
                # to ni prilagojeno za m != n
                # razdelimo na naddiagonale, poddiagonale in diagonale
                poddiag1 = [self.plosca[min(VRSTICE, STOLPCI) - i + j, j] for 
                            j in range(min(i, min(VRSTICE, STOLPCI)))]
                naddiag1 = [self.plosca[j, min(VRSTICE, STOLPCI) - i + j] for 
                            j in range(min(i, min(VRSTICE, STOLPCI)))]

                # zrcalimo ploščo čez x os in ponovimo
                poddiag2 = [np.flip(self.plosca, axis=1)[min(VRSTICE, STOLPCI) - i + j, j] for 
                            j in range(min(i, min(VRSTICE, STOLPCI)))]
                naddiag2 = [np.flip(self.plosca, axis=1)[j, min(VRSTICE, STOLPCI) - i + j] for 
                            j in range(min(i, min(VRSTICE, STOLPCI)))]

                if (ponovitve(list(diag1), 1) or ponovitve(list(naddiag1), 1) 
                    or ponovitve(list(poddiag1), 1) or ponovitve(list(diag2), 1) 
                    or ponovitve(list(naddiag2), 1) or ponovitve(list(poddiag2), 1)):
                    self.konec = True
                    return 1

                if (ponovitve(list(diag1), -1) or ponovitve(list(naddiag1), -1) 
                    or ponovitve(list(poddiag1), -1) or ponovitve(list(diag2), -1) 
                    or ponovitve(list(naddiag2), -1) or ponovitve(list(poddiag2), -1)):
                    self.konec = True
                    return -1
            
        # izenačenje
        if len(self.legalne_pozicije()) == 0:
            self.konec = True
            return 0

        # ni konec
        self.konec = False
        return None


    def daj_nagrado(self):
        """
        Da nagrade obema igralcema glede na izid igre, 
        s številkami se lahko še malo igramo.
        """
        # nagrade pridejo samo ob koncu igre
        rezultat = self.zmagovalec()
        if rezultat == 1:
            self.p1.nagradi(NAGRADA_ZMAGA)
            self.p2.nagradi(NAGRADA_PORAZ)
        elif rezultat == -1:
            self.p1.nagradi(NAGRADA_PORAZ)
            self.p2.nagradi(NAGRADA_ZMAGA)
        else:
            self.p1.nagradi(NAGRADA_REMI)
            self.p2.nagradi(NAGRADA_REMI)


    def treniraj(self, epizode):
        """
        Vsak igralec:
        poišče možne pozicije, 
        izbere akcijo, 
        posodobi ploščo in zabeleži stanje, 
        počaka razsodbo o koncu
        """
        for i in range(epizode):
            if i % 100 == 0:
                print(f'Epizoda {i+1}')
            
            while not self.konec:
                # 1. igralec
                pozicije = self.legalne_pozicije()
                p1_akcija = p1.izberi_akcijo(pozicije, self.plosca, self.simbol)
                self.igraj(p1_akcija)
                stanje = self.pridobi_stanje()
                self.p1.dodaj_stanje(stanje)

                zmaga = self.zmagovalec()
                if zmaga is not None:
                    # zmagal je prvi ali remi
                    #print(f'Zmagal je {self.zmagovalec()}')
                    self.daj_nagrado()
                    self.p1.ponastavi()
                    self.p2.ponastavi()
                    self.ponastavi()
                    break

                else:
                    # 2. igralec
                    pozicije = self.legalne_pozicije()
                    p2_akcija = p2.izberi_akcijo(pozicije, self.plosca, self.simbol)
                    self.igraj(p2_akcija)
                    stanje = self.pridobi_stanje()
                    self.p2.dodaj_stanje(stanje)

                    zmaga = self.zmagovalec()
                    if zmaga is not None:
                        # zmagal je drugi ali remi
                        #print(f'Zmagal je {self.zmagovalec()}')
                        self.daj_nagrado()
                        self.p1.ponastavi()
                        self.p2.ponastavi()
                        self.ponastavi()
                        break

    
    def igraj_clovek(self, naravno=True):
        """
        Metoda za igranje agent - človek.
        """
        while not self.konec:
            pozicije = self.legalne_pozicije()
            p1_akcija = p1.izberi_akcijo(pozicije, self.plosca, self.simbol)
            self.igraj(p1_akcija)
            print(self)
            stanje = self.pridobi_stanje()
            self.p1.dodaj_stanje(stanje)

            zmaga = self.zmagovalec()
            if zmaga is not None:
                if zmaga == 1:
                    print(f'Zmagal je {self.p1.ime}!')

                else:
                    print('Izenačeno!')
                self.ponastavi()
                break

            else:
                pozicije = self.legalne_pozicije()
                p2_akcija = self.p2.izberi_akcijo(pozicije, naravno=naravno)
                self.igraj(p2_akcija)
                print(self)

                zmaga = self.zmagovalec()
                if zmaga is not None:
                    if zmaga == -1:
                        print(f'Zmagal je {self.p2.ime}!')
                    
                    else:
                        print('Izenačeno!')
                    self.ponastavi()
                    break


    def igraj_nakljucni(self, st_iger=1000):
        """
        Metoda za igranje agent - naključni igralec.
        """
        rezultati = {
            'zmage': 0,
            'izenačenja': 0,
            'porazi': 0
            }

        for i in range(st_iger):
            if i % 100 == 0:
                print(f'Igra {i+1}')

            while not self.konec:
                # 1. igralec
                pozicije = self.legalne_pozicije()
                p1_akcija = p1.izberi_akcijo(pozicije, self.plosca, self.simbol)
                self.igraj(p1_akcija)
                stanje = self.pridobi_stanje()
                self.p1.dodaj_stanje(stanje)

                zmaga = self.zmagovalec()
                if zmaga is not None:
                    # zmagal je prvi ali remi
                    if zmaga == 1:
                        rezultati['zmage'] += 1

                    else: 
                        rezultati['izenačenja'] += 1

                    self.ponastavi()
                    break

                else:
                    # 2. igralec
                    pozicije = self.legalne_pozicije()
                    p2_akcija = p2.izberi_akcijo(pozicije)
                    self.igraj(p2_akcija)

                    zmaga = self.zmagovalec()
                    if zmaga is not None:
                        # zmagal je drugi ali remi
                        if zmaga == -1:
                            rezultati['porazi'] += 1

                        else: 
                            rezultati['izenačenja'] += 1

                        self.ponastavi()
                        break
        print(rezultati)


    def igraj_sebi(self, st_iger=1000):
        """
        Metoda za igranje agent - agent.
        """
        rezultati = {
            'zmage': 0,
            'izenačenja': 0,
            'porazi': 0
            }

        for i in range(st_iger):
            if i % 100 == 0:
                print(f'Igra {i+1}')
            
            while not self.konec:
                # 1. igralec
                pozicije = self.legalne_pozicije()
                p1_akcija = p1.izberi_akcijo(pozicije, self.plosca, self.simbol)
                self.igraj(p1_akcija)
                stanje = self.pridobi_stanje()
                self.p1.dodaj_stanje(stanje)

                zmaga = self.zmagovalec()
                if zmaga is not None:
                    # zmagal je prvi ali remi
                    if zmaga == 1:
                        rezultati['zmage'] += 1

                    else: 
                        rezultati['izenačenja'] += 1

                    self.ponastavi()
                    break

                else:
                    # 2. igralec
                    pozicije = self.legalne_pozicije()
                    p2_akcija = p2.izberi_akcijo(pozicije, self.plosca, self.simbol)
                    self.igraj(p2_akcija)
                    stanje = self.pridobi_stanje()
                    self.p2.dodaj_stanje(stanje)

                    zmaga = self.zmagovalec()
                    if zmaga is not None:
                        # zmagal je drugi ali remi
                        if zmaga == -1:
                            rezultati['porazi'] += 1

                        else: 
                            rezultati['izenačenja'] += 1

                        self.ponastavi()
                        break
        print(rezultati)



    def igraj_splosni(self, p1, p2):
        pass



class Agent:
    """
    To je računalniški igralec; mora si shranjevati stanja, 
    jih ocenjevati in posodabljati ob koncu igre. Mora tudi
    shraniti strategijo.
    """

    def __init__(self, ime, epsilon=0.3, gama=0.9, alfa=0.2):
        """
        Agent mora beležiti vsa raziskana stanja v epizodi in 
        posodabljati vrednosti teh stanj. 

        epsilon = verjetnost da naredi naključno potezo (raziskuje)
        gama = diskontni faktor
        alfa = hitrost učenja (learning rate)
        """
        self.ime = ime
        self.stanja = []            # beleži vsa stanja
        self.epsilon = epsilon
        self.gama = gama
        self.alfa = alfa

        # začnemo s prazno - izogib prevelikim tabelam
        self.vrednosti_stanj = {}   # stanje -> vrednost

    
    def izberi_akcijo(self, pozicije, stanje, simbol):
        """
        epsilon-požrešno izbere akcijo in jo vrne.

        pozicije = možne pozicije, ki jih lahko igramo
        """
        # izberemo naključno
        if np.random.uniform(0, 1) <= self.epsilon:
            indeks =  np.random.choice(len(pozicije))
            akcija = pozicije[indeks]

        else:
            najvecja_vrednost = -1
            for pozicija in pozicije:
                naslednje_stanje = stanje.copy()
                naslednje_stanje[pozicija] = simbol
                naslednji = self.pridobi_stanje(naslednje_stanje)

                if self.vrednosti_stanj.get(naslednji) is None:
                    vrednost = 0 
                else:
                    vrednost = self.vrednosti_stanj.get(naslednji)

                if vrednost >= najvecja_vrednost:
                    najvecja_vrednost = vrednost
                    akcija = pozicija
        
        #print(f'{self.ime} igra na {akcija}')
        return akcija


    def pridobi_stanje(self, plosca):
        """
        Agent mora dobiti stanje od plošče in ga spremeniti v
        njemu razumljivo obliko.
        """
        plosca = str(plosca.reshape(VRSTICE * STOLPCI))
        return plosca


    def dodaj_stanje(self, stanje):
        self.stanja.append(stanje)


    def nagradi(self, nagrada):
        """
        Po koncu igre se posodobijo vrednosti stanj od zadaj naprej
        po pravilu spodaj. Za vrednost zadnjega stanja (ki ni dejansko 
        stanje) je vrednost kar nagrada.

        vrednost = vrednost + alfa * (gama * vrednost(naslednji) - vrednost)
        """
        for stanje in reversed(self.stanja):
            if self.vrednosti_stanj.get(stanje) is None:
                self.vrednosti_stanj[stanje] = 0

            self.vrednosti_stanj[stanje] += self.alfa * (
                self.gama * nagrada - self.vrednosti_stanj[stanje])

            nagrada = self.vrednosti_stanj[stanje]


    def ponastavi(self):
        """
        Izbriše zgodovino agentovih stanj.
        """
        self.stanja = []
        # self.vrednosti_stanj = {}

    
    def shrani_strategijo(self):
        """
        Shrani slovar vrednosti stanj za kasnejšo uporabo.
        """
        f = open('koda/strategije/strategija_' + str(self.ime), 'wb')
        pickle.dump(self.vrednosti_stanj, f)
        f.close()
    

    def nalozi_strategijo(self, datoteka):
        """
        Naloži slovar naučenih vrednosti.
        """
        f = open(datoteka, 'rb')
        self.vrednosti_stanj = pickle.load(f)
        f.close



class Clovek():
    """
    Predstavlja človeškega igralca v igri.
    """

    def __init__(self, ime):
        self.ime = ime


    def izberi_akcijo(self, legalne, naravno=True):
        """
        Dovoli človeku, da izbere akcijo, ki jo poda kot
        dve številki. Nato preverimo, če je akcija legalna
        in jo igramo.
        """
        while True:
            if naravno:
                vrstica = int(input('Izberi vrstico: ')) - 1
                stolpec = int(input('Izberi stolpec: ')) - 1

            else:
                vrstica = int(input('Izberi vrstico: '))
                stolpec = int(input('Izberi stolpec: '))

            akcija = (vrstica, stolpec)
            if akcija in legalne:
                return akcija

    
    # Spodaj so provizorične funkcije, da program deluje
    def dodaj_stanje(self, stanje):
        pass


    def nagradi(self, nagrada):
        pass


    def ponastavi(self):
        pass



class Nakljucni():
    """
    Igralec, ki se vede naključno. Uporaben za namene testiranja in treniranja.
    """

    def __init__(self, ime):
        self.ime = ime


    def izberi_akcijo(self, pozicije):
        """
        Enostavno pridobi seznam vseh legalnih pozicij in izbere naključno.
        """
        indeks =  np.random.choice(len(pozicije))
        akcija = pozicije[indeks]
        return akcija



class Minimax():
    """
    Igralec, ki s pomočjo algoritma Minimax poišče popolno strategijo. 
    Uporaben za namene testiranja.
    """
    pass

    


if __name__ == '__main__':
    # trening
#    p1 = Agent('p1', epsilon=0.01)
#    p2 = Agent('p2', epsilon=0.1)
#
#    igra = Okolje(p1, p2)
#    print('Treniram...')
#    igra.treniraj(3000)
#    p1.shrani_strategijo()

    #igraj
    p1 = Agent('agent1', epsilon=0)
    p1.nalozi_strategijo('koda/strategije/strategija_p1')
    p2 = Clovek('Tim')

    igra = Okolje(p1, p2)
    igra.igraj_clovek()




# TODO: poglej, če si povsod uporabil globalne konstante
# TODO: igraj_clovek, da lahko začne poljubni
# TODO: boljši shrani in naloži funkciji
# TODO: implementiraj nek timer (mogoče je lahko dekorator)
# TODO: "vsi" passi so nekaj
# TODO: Zmagovalec, ki deluje na m != n
# TODO: vse dobro dokumentiraj
# TODO: implementiraj gravitacijo
# TODO: implementiraj boljše algoritme
# TODO: implementiraj nevronske mreže
# TODO: refaktorizacija
# TODO: da lahko spreminjaš alfa, epsilon, ... v main
# TODO: boljši main: da lahko izbiraš, če se policy nalaga