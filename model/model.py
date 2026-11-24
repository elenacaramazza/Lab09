from database.parco_DAO import ParcoDAO
from database.escursione_DAO import EscursioneDAO
from database.punto_interesse_DAO import PuntoInteresseDAO


class Model:
    def __init__(self):
        self.escursioni_map = {} # Mappa ID escursione -> oggetti Escursione
        self.punti_interesse_map = {} # Mappa ID punto di interesse -> oggetti PuntoInteresse

        self._pacchetto_ottimo = []
        self._valore_ottimo: int = -1
        self._costo = 0

        # TODO: Aggiungere eventuali altri attributi

        self._escursioni_parco = []
        self._max_giorni: int | None = None
        self._max_budget: int | None = None

        # Caricamento
        self.load_escursioni()
        self.load_punti_interesse()
        self.load_relazioni()

    @staticmethod
    def load_parchi():
        """ Restituisce tutti i parchi disponibili """
        return ParcoDAO.get_parchi()

    def load_escursioni(self):
        """ Carica tutte le escursioni in un dizionario [id, Escursione]"""
        self.escursioni_map = EscursioneDAO.get_escursioni()

    def load_punti_interesse(self):
        """ Carica tutti i punti di interesse in un dizionario [id, PuntoInteresse]"""
        self.punti_interesse_map = PuntoInteresseDAO.get_punti_interesse()

    def load_relazioni(self):
        """
            Interroga il database per ottenere tutte le relazioni fra escursioni e punti di interesse e salvarle nelle strutture dati
            Collega escursione <-> punti di interesse.
            --> Ogni Escursione ha un set di PuntoInteresse.
            --> Ogni PuntoInteresse ha un set di Escursioni.
        """
        # TODO

        # estraggo le relazioni (escursione - punto di interesse) come una lista di dizionari {id_esc, id_puntInt}
        relazioni = EscursioneDAO.get_escursioni_punti_interesse()

        if relazioni:
            for relazione in relazioni:
                punto = self.punti_interesse_map[relazione["id_punto_interesse"]]
                escursione = self.escursioni_map[relazione["id_escursione"]]

                punto.escursioni.add(escursione)
                escursione.punti_interesse.add(punto)

    def genera_pacchetto(self, id_parco: str, max_giorni: int = None, max_budget: float = None):
        """
        Calcola il pacchetto di escursioni ottimale per un parco rispettando i vincoli di durata, budget e punti di interesse unici.
        :param id_parco: id del parco
        :param max_giorni: numero massimo di giorni (può essere None --> nessun limite)
        :param max_budget: costo massimo del pacchetto (può essere None --> nessun limite)

        :return: self._pacchetto_ottimo (una lista di oggetti Escursione)
        :return: self._costo (il costo del pacchetto)
        :return: self._valore_ottimo (il voto complessivo dei visitatori per il pacchetto)
        """
        self._pacchetto_ottimo = []
        self._costo = 0
        self._valore_ottimo = -1

        # TODO

        self._max_giorni = max_giorni
        self._max_budget = max_budget

        self._escursioni_parco = [esc for esc in self.escursioni_map.values() if esc.id_parco == id_parco]

        self._ricorsione(0,[],0,0,0.0, set() )

        return self._pacchetto_ottimo, self._costo, self._valore_ottimo

    def _ricorsione(self, start_index: int, pacchetto_parziale: list, durata_corrente: int, costo_corrente: float, valore_corrente: int, punti_usati: set):
        """ Algoritmo di ricorsione che deve trovare il pacchetto che massimizza il voto complessivo dei visitatori"""

        # TODO: è possibile cambiare i parametri formali della funzione se ritenuto opportuno

        if valore_corrente > self._valore_ottimo:
            self._valore_ottimo = valore_corrente
            self._pacchetto_ottimo = pacchetto_parziale.copy()
            self._costo = costo_corrente

        for i in range(start_index, len(self._escursioni_parco)):
            esc = self._escursioni_parco[i]

            nuova_durata = durata_corrente + esc.durata_giorni
            nuovo_costo = costo_corrente + esc.costo

            if self._vincoli_soddisfatti(esc.punti_interesse, nuova_durata, nuovo_costo, punti_usati):
                pacchetto_parziale.append(esc)
                punti_usati.update(esc.punti_interesse)
                valore_aggiunto = sum(punto.voto_visitatori for punto in esc.punti_interesse)

                self._ricorsione(
                    start_index=i + 1,
                    pacchetto_parziale=pacchetto_parziale,
                    durata_corrente=nuova_durata,
                    costo_corrente=nuovo_costo,
                    valore_corrente=valore_corrente + valore_aggiunto,
                    punti_usati=punti_usati
                )

                pacchetto_parziale.pop()
                punti_usati.difference_update(esc.punti_interesse)

    def _vincoli_soddisfatti(self, punti_interesse: set, durata_corrente: int, costo_corrente: int, punti_usati: set):
        # vincolo di tempo
        if self._max_giorni is not None and durata_corrente > self._max_giorni:
            return False

        # vincolo di costo
        if self._max_budget is not None and costo_corrente > self._max_budget:
            return False

        # vincolo sull'unicità dei punti di interesse
        if not punti_usati.isdisjoint(punti_interesse):
            return False

        return True
