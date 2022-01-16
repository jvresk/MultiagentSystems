#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from spade.message import Message
import random
import asyncio

#stanja ptice trkačice
stanje_pt_pocetno="trci"
stanje_pt_lijevo="lijevi"
stanje_pt_desno="desni"
stanje_pt_gotovo="gotovo"

#stanja kojota
stanje_prvo="planiraj"
stanje_drugo="ulov"
stanje_trece="neuspjeh"

pozicija_zamke=["zamka_na_pocetku_lijevog_tunela", "zamka_na_kraju_lijevog_tunela", 
    "zamka_na_pocetku_desnog_tunela", "zamka_na_kraju_desnog_tunela"]
ulazi=["ulaz_u_lijevi_tunel","ulaz_u_desni_tunel"]

class FSMBehav(FSMBehaviour):
    async def on_start(self):
        print(f"")

    async def on_end(self):
        print(f"")
        await self.agent.stop()



#stanja Ptice
class StanjePtPocetno(State):
    async def run(self):
        print("Ptica trkačica: Biram tunel")
        tunel=random.choice(ulazi)
        print(f"Ptica trkačica: Izabrala sam {tunel}")
        await asyncio.sleep(5)
        msg = Message(to="josipa@rec.foi.hr")       
        msg.body = f"{tunel}"
        await self.send(msg) 
        if(tunel == ulazi[0]):
            self.set_next_state(stanje_pt_lijevo)
        else:
            self.set_next_state(stanje_pt_desno)   

class StanjePtLijevo(State):
    async def run(self):
        print("Ptica trkačica: Skrenula sam u lijevi tunel")
        self.set_next_state(stanje_pt_gotovo)
           

class StanjePtDesno(State):
    async def run(self):
        print("Ptica trkačica: Skrenula sam u desni tunel")
        self.set_next_state(stanje_pt_gotovo)


class StanjePtGotovo(State):
    async def run(self):
        print("Ptica trkačica: Gotovo je")
        await self.agent.stop()
           

#stanja Kojota

class StanjePrvo(State):
    async def run(self):
        print("Kojot: Planiram")

        zamka=random.choice(pozicija_zamke)
        print(f"Kojot: Postavio sam zamku na: {zamka}")

        msg_primljena = await self.receive(timeout=10)
        

        if(msg_primljena.body == ulazi[0]):
            if(zamka == pozicija_zamke[0] or zamka == pozicija_zamke[1]):
                self.set_next_state(stanje_drugo)
            else:
                self.set_next_state(stanje_trece)
        
        else:
            if(zamka == pozicija_zamke[2] or zamka == pozicija_zamke[3]):
                self.set_next_state(stanje_drugo)
            else:
                self.set_next_state(stanje_trece)

class StanjeDrugo(State):
    async def run(self):
        print("Kojot: Ptica trkačica je ulovljena")
        await self.agent.stop()
           

class StanjeTrece(State):
    async def run(self):
        print("Kojot: Ptica trkačica je pobjegla")
        await self.agent.stop()


#agenti

class GladanKojot(Agent):
    
    async def setup(self):
        print("GladanKojot je spreman\n")
        self.fsm = FSMBehav()
        #stanja
        self.fsm.add_state(name=stanje_prvo, state=StanjePrvo(), initial=True)
        self.fsm.add_state(name=stanje_drugo, state=StanjeDrugo())
        self.fsm.add_state(name=stanje_trece, state=StanjeTrece())

        #prijelazi
        self.fsm.add_transition(source=stanje_prvo, dest=stanje_drugo)
        self.fsm.add_transition(source=stanje_prvo, dest=stanje_trece)

        
        self.add_behaviour(self.fsm)


class PticaTrkacica(Agent):
    async def setup(self):
        print("PticaTrkacica trči!")

        self.fsm = FSMBehav()

        #stanja
        self.fsm.add_state(name=stanje_pt_pocetno, state=StanjePtPocetno(), initial=True)
        self.fsm.add_state(name=stanje_pt_lijevo, state=StanjePtLijevo())
        self.fsm.add_state(name=stanje_pt_desno, state=StanjePtDesno())
        self.fsm.add_state(name=stanje_pt_gotovo, state=StanjePtGotovo())


        #prijelazi
        self.fsm.add_transition(source=stanje_pt_pocetno, dest=stanje_pt_lijevo)
        self.fsm.add_transition(source=stanje_pt_pocetno, dest=stanje_pt_desno)
        self.fsm.add_transition(source=stanje_pt_lijevo, dest=stanje_pt_gotovo)
        self.fsm.add_transition(source=stanje_pt_desno, dest=stanje_pt_gotovo)

        self.add_behaviour(self.fsm)


if __name__ == "__main__":
    PticaTrkacica = PticaTrkacica("josipa1@rec.foi.hr", "josipavas1")
    future = PticaTrkacica.start()
    future.result() 
    GladanKojot = GladanKojot("josipa@rec.foi.hr", "josipavas")
    GladanKojot.start()

    
    while PticaTrkacica.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            GladanKojot.stop()
            PticaTrkacica.stop()
            break

    print("Agenti su završili s radom")