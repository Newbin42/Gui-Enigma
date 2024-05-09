from __future__ import annotations
from random import shuffle, seed

ALPHABET = "abcdefghijklmnopqrstuvwxyz"
ALPH_REF = {**{ALPHABET[i]: str(i+1) for i in range(len(ALPHABET))}, **{ALPHABET[i].upper(): str(i+1) for i in range(len(ALPHABET))}}
NUM_REF = {**{str(i+1): ALPHABET[i] for i in range(len(ALPHABET))}, **{str(i+1): ALPHABET[i].upper() for i in range(len(ALPHABET))}}
REF = {**ALPH_REF, **NUM_REF}

def wire(a: list, b: list) -> dict:
    "Returns a dictionary of {keys : pairs} beteen a and b"
    return {a[x] : b[x] for x in range(len(a))}

def join(a: dict, b: dict) -> dict:
    "Join two dictionaries"
    return a.copy().update(b.copy())

def dict_to_string(dictionary: dict) -> str:
    output = ""
    for key, _ in dictionary.items():
        output += key
    
    output += "\n"
    for _, val in dictionary.items():
        output += val
    
    return output

class Ratchet():
    @staticmethod
    def generate(string: str, comparison: str) -> str:
        output: dict = {c: False for c in comparison.lower()}

        for char in string.lower():
            output[char] = True

        return output
    
    def __init__(self, notches: str | dict) -> None:
        if (type(notches) == dict): self.dict = notches
        else: self.dict = Ratchet.generate(notches.lower(), ALPHABET)

    def pawl(self) -> bool:
        "Return the first item in the ratchet (The position of the Pawl)."
        return self.get(0)
    
    def window(self) -> bool:
        "Return the second item in the ratchet (The position just after the Pawl, aka the Window)."
        return self.get(1)
    
    def str_window(self) -> str:
        output: str = list(self.dict)[1]
        return output.upper()
    
    def behind(self) -> bool:
        "Return the last item in the ratchet (The position just before the Pawl)."
        return self.get(len(self.dict) - 1)
    
    def get(self, index: int) -> bool:
        return self.dict[list(self.dict)[index]]
    
    def rotate_1(self, direction: int) -> None:
        temp = list(self.dict)

        if (direction == 1):
            t = temp.pop(0)
            temp.append(t)
        else:
            t = temp.pop()
            temp.insert(0, t)

        temp = {key : self.dict[key] for key in temp}
        self.dict = temp
    
    def set_orientation(self, key: str):
        key = key.lower()
        while (list(self.dict)[0] != key):
            self.rotate_1(1)

    def reset(self) -> None:
        while (list(self.dict)[0] != ALPHABET[0]):
            self.rotate_1(1)

    def to_dict(self) -> dict:
        return {key: val for key, val in self.dict.items()}

    def __eq__(self, other: Ratchet) -> bool:
        vals_1 = [val for _, val in self.dict.items()]
        vals_2 = [val for _, val in other.dict.items()]

        for i in range(len(vals_1)):
            if (vals_1[i] != vals_2[i]): return False
        
        return True
    
    def __ne__(self, other: Ratchet):
        return not self == other

    def __str__(self) -> str:
        return "".join([key for key, _ in self.dict.items()]) + "\n" + "".join([str(0) if (not val) else str(1) for _, val in self.dict.items()])

class Plugboard:
    def __init__(self):
        self.board = ALPHABET
        self.__board__ = [c for c in self.board]

    def set_keys(self, *settings: str) -> None:
        "input settings as in/out; Ex. L/R or l/r"
        swapped = ""

        for setting in settings:
            s = setting.lower().split("/")
            if (s[0] in swapped or s[1] in swapped): continue

            i = self.board.find(s[0])
            j = self.board.find(s[1])
            swapped += f'{s[0]}{s[1]}'
            
            temp = self.__board__[i]
            self.__board__[i] = self.__board__[j]
            self.__board__[j] = temp
            self.board = "".join(self.__board__)
    
    def passthrough(self, letter: str) -> str:
        "Transfer the input letter through the plugboard."
        try: return self.board[ALPHABET.index(letter)]
        except ValueError: return letter
        
    def reset(self):
        self.board = ALPHABET

class Plate:
    @staticmethod
    def new(id: int, s: int = 0):
        seed(s)
        keys_1 = ALPHABET
        keys_2 = [x for x in ALPHABET]
        shuffle(keys_2)
        keys_2 = "".join(keys_2)

        return Plate(keys_1, keys_2, id)
    
    def __init__(self, keysIn: str, keysOut: str, plateID: int) -> None:
        self.comparison: str = keysIn
        self.pins: str = keysOut
        self.pid: int = plateID

    def passthrough(self, char: str) -> str:
        "Pass a character through the plate (input - output)."
        try:
            #Input travels over wiring pattern
            comparisonIndex = self.comparison.index(char)
            return self.pins[comparisonIndex]
        except ValueError:
            return char
    
    def mirrored_passthrough(self, char: str) -> str:
        "Pass a character through the plate (output - input)."
        try:
            #Input travels over reverse wiring pattern
            pinIndex = self.pins.index(char)
            return self.comparison[pinIndex]
        except ValueError:
            return char
        
    def get_pid(self) -> int:
        return self.pid
    
    def __eq__(self, other: Plate) -> bool:
        return other != None and self.pins == other.pins
    
    def __ne__(self, other: Rotor) -> bool:
        return other == None or self != other
    
    def __str__(self) -> str:
        return f'Plate {self.pid}:\n{self.pins}'

class Rotor(Plate):
    @staticmethod
    def shift_1(toShift: str, direction: int = 1) -> str:
        temp = [c for c in toShift]

        if (direction == 1):
            t = temp.pop(0)
            temp.append(t)
        else:
            t = temp.pop()
            temp.insert(0, t)
        
        return "".join(temp)
    
    @staticmethod
    def new(id: int, ratchets: str = "A", s: int = 0):
        seed(s)
        keys_1 = ALPHABET
        keys_2 = [x for x in ALPHABET]
        shuffle(keys_2)
        keys_2 = "".join(keys_2)

        return Rotor(keys_1, keys_2, id, ratchets)

    def __init__(self, keysIn: str, keysOut: str, rotorID: int, ratchet: str | dict = "A") -> None:
        Plate.__init__(self, keysIn, keysOut, rotorID)
        self.ratchet: Ratchet = Ratchet(ratchet)
        self.r = 0
    
    def window(self, useOut = False) -> str:
        if (useOut): return self.pins[self.r].upper()
        else:
            return self.comparison[0].upper()
    
    def rotate_forward(self) -> None:
        self.comparison = Rotor.shift_1(self.comparison)
        self.ratchet.rotate_1(1)
        self.r += 1

        if (self.r >= 26): self.r = 0
    
    def rotate_backward(self) -> None:
        self.comparison = Rotor.shift_1(self.comparison, -1)
        self.ratchet.rotate_1(-1)
        self.r -= 1

        if (self.r <= 0): self.r = 25
    
    def set_orientation(self, target: str) -> None:
        while (self.comparison[0] != target.lower()):
            self.rotate_forward()

    def reset_orientation(self) -> None:
        self.set_orientation(ALPHABET[0])
    
    def __str__(self) -> str:
        output = super().__str__().replace(f'Plate {self.get_pid()}', f'Rotor {self.get_pid()}')
        output += f'\nNotches: \n{self.ratchet}'
        return output

class Mirror(dict):
    @staticmethod
    def new(s: int = 0):
        seed(s)

        keys_1 = [x for x in ALPHABET]
        shuffle(keys_1)
        keys_1 = "".join(keys_1)

        keys_2 = keys_1[::-1]

        return Mirror(keys_1, keys_2)

    def __init__(self, input: dict, output: dict | bool) -> None:
        if (output == False):
            dict.__init__(self, input)
        else:
            dict.__init__(self, wire(input, output))
    
    def passthrough(self, char: str) -> str:
        "Pass a character through the plate (input - output)."
        try: #Input travels over wiring pattern
            return self[char]
        except KeyError:
            return char

class EnigmaMachine:
    """
    Rotor rotations are handled left - right. Not the original right - left.
    
    Rotor wiring is also handled left - right. Rotor Order 123 flows 123 - mirror - 321, not the original 321 - mirror - 123."""

    def __init__(self, rotorSlots: int = 3) -> None:
        """Initialize a new Enigma Machine with a provided number of rotor slots.
        
        Also contains a customizeable mirror plate, plugboard, and entry plate by default"""
        self.plugboard: Plugboard = Plugboard()
        self.mirror: Mirror = Mirror.new()
        self.entryPlate: Plate = Plate.new(0)
        self.rotorSlots: int = rotorSlots
        self.rotors: list[Rotor] = [None for x in range(rotorSlots)]
        self.key: list = ["A" for _ in range(rotorSlots)]

    def remove_plugboard(self) -> Plugboard:
        """Remove the plugbord from the machine"""
        output = self.plugboard
        self.plugboard = None
        return output
    
    def attach_plugboard(self, plugboard: Plugboard) -> None:
        """Attach a plugboard to the machine."""
        if (self.plugboard == None):
            self.plugboard = plugboard
        else:
            raise ValueError("A plugboard is already attached. Please uninstall the current plugboard first.")
    
    def swap_entry_plate(self, entryPlate: Plate) -> Plate:
        """Swap the entry plate for a new one."""
        output = self.entryPlate
        self.entryPlate = entryPlate
        return output
    
    def remove_mirror_plate(self) -> Plugboard:
        """Remove the mirror plate from the machine"""
        output = self.mirror
        self.mirror = None
        return output
    
    def attach_mirror_plate(self, mirror: Mirror) -> None:
        """Attach a plugboard to the machine."""
        if (self.mirror == None):
            self.mirror = mirror
        else:
            raise ValueError("A mirror plate is already installed. Please uninstall the current mirror plate first.")

    def swap_mirror_plate(self, mirror: Mirror) -> Mirror:
        """Swap the mirror for a new one."""
        output = self.mirror
        self.mirror = mirror
        return output

    def encode(self, phrase: str) -> str:
        """Encode a message using the machine's settings"""
        #Check if all rotor slots are filled
        c = 0
        for rotor in self.rotors:
            if (type(rotor) != None): c += 1
        if (c != self.rotorSlots):
            raise ValueError("There are not enough rotors in the machine.")

        #Encode
        encodedMessage = ""
        for char in phrase.lower():
            if (char in ALPHABET): encodedMessage += self.encode_char(char)
            else: encodedMessage += char
        
        return encodedMessage

    def encode_char(self, char: str) -> str:
        #Rotate Rotors (Turnover)
        self.turnover()

        #Pass through the plugboard (if there is one.)
        if (self.plugboard != None):
            char = self.plugboard.passthrough(char)

        #Pass through entry plate
        char = self.entryPlate.passthrough(char)

        #First Pass through the rotors
        for r in range(len(self.rotors)):
            char = self.rotors[r].passthrough(char)

        #Pass through mirror
        char = self.mirror.passthrough(char)
        
        #Mirrored return trip through the rotors
        for r in range(len(self.rotors) - 1, -1, -1):
            char = self.rotors[r].mirrored_passthrough(char)

        #Pass back through entry plate
        char = self.entryPlate.mirrored_passthrough(char)

        #Pass back through the plugboard (if there is one.)
        if (self.plugboard != None):
            char = self.plugboard.passthrough(char)

        #Send to lightboard
        return char
    
    def turnover(self) -> None:
        "Rotate the left-most rotor. With the other rotors rotating according to ratchet positions."
        self.rotors[0].rotate_forward()
        for r in range(1, self.rotorSlots):
            holdsTrue = True
            for r2 in range(r - 1, -1, -1):
                if (not holdsTrue): continue
                if (self.rotors[r2].ratchet.pawl() == False): holdsTrue = False

            if (holdsTrue and self.rotors[r - 1].ratchet.pawl() == True):
                self.rotors[r].rotate_forward()

    def set_plugboard(self, *settings: str) -> None:
        """input settings as in/out; Ex. L/R or l/r
        
        Raises a ValueError if there is no plugboard"""
        if (self.plugboard != None):
            self.plugboard.set_keys(*settings)
        else:
            raise ValueError("No plugobard in the machine.")
    
    def reset_plugboard(self) -> None:
        "Reset the machine's plug board."
        if (self.plugboard != None): self.plugboard = Plugboard()
        else: raise ValueError("No plugobard in the machine.")

    def orient_rotor(self, rotor_id: int | tuple[int], orientation: str) -> None:
        """Orients a rotor or a batch of rotors in the machine to the provided orientations (key(s)).
        
        Ex. Machine.orient_rotor((1, 2, 3), "ABC"), or Machine.orient_rotor(2, "D") """
        if (type(rotor_id) == int):
            index = self.__indexof__(rotor_id)
            self.rotors[index].set_orientation(orientation)
            self.key[index] = orientation

        else:
            for r in range(len(rotor_id)):
                index = self.__indexof__(rotor_id[r])
                self.rotors[index].set_orientation(orientation[r])
                self.key[index] = orientation[r]
    
    def orient_rotors(self, orientation: str) -> None:
        "Orient all rotors in the machine based on the provided key."
        for r in range(len(self.rotors)):
            self.rotors[r].set_orientation(orientation[r])
    
    def orient_ratchets(self, orientation: str) -> None:
        "Orient all ratchets in the machine based on the provided key."
        for r in range(len(self.rotors)):
            self.rotors[r].ratchet.set_orientation(orientation[r])

    def get_rotor(self, rotor_id: int) -> Rotor:
        "Return the rotor with the id of rotor_id"
        return self.rotors[self.__indexof__(rotor_id)]

    def insert(self, rotor: Rotor, slot: int, orientation: str) -> None:
        "Insert a rotor(s) into the machine."
        if (type(rotor) == Rotor):
            rotor.set_orientation(orientation)
            if (self.rotors[slot - 1] == None):
                self.rotors[slot - 1] = rotor
            else:
                raise IndexError(f'A rotor is already in slot {slot}. Please remove it first.')

    def insert_rotors(self, rotors: list[Rotor], orientation: str) -> None:
        for r in range(len(rotors)):
            self.insert(rotors[r], r + 1, orientation[r])
    
    def remove_all_rotors(self) -> list[Rotor]:
        output = []
        for r in range(self.rotorSlots):
            output.append(self.rotors[r])
            self.rotors[r] = None
        
        return output

    def remove(self, rotor_id: int) -> Rotor:
        "Modified pop method. Pulls the rotor with id - rotor_id out of the machine."
        #Find rotor with id
        i = 0
        while (i < self.rotorSlots and self.rotors[i].get_pid() != rotor_id):
            i += 1
        
        if (i < self.rotorSlots):
            output = self.rotors[self.__indexof__(rotor_id)]
            self.rotors[self.__indexof__(rotor_id)] = None
        else:
            output = None

        return output
    
    def remove_from_slot(self, slot: int) -> Rotor:
        if (slot < 1 or slot > len(self.rotors)): return

        self.rotors.insert(slot - 1, None)
        return self.rotors.pop(slot)

    def __indexof__(self, rotor_id: int) -> int:
        "Return the index of the selected rotor."
        i = 0
        while (i < len(self.rotors) and self.rotors[i].get_pid() != rotor_id):
            i += 1

        if (i >= len(self.rotors)):
            raise IndexError(f'Rotor {rotor_id} not found.')
        
        return i

def shuffleAlph(s = 0):
    seed(s)
    keys = [c for c in ALPHABET]
    shuffle(keys)
    return "".join(keys)

#Testing
if __name__ == "__main__":
    R_1 = Rotor.new(1)
    R_2 = Rotor.new(2, "AIY")
    R_3 = Rotor.new(3, "Y")

    machine = EnigmaMachine(3)
    print(machine.mirror)
    #machine.set_plugboard("F/E", "Q/U", "C/H")
    machine.remove_plugboard()
    machine.insert(R_2, 1, "E")
    machine.insert(R_1, 2, "W")
    machine.insert(R_3, 3, "L")

    print("Attempt to encode...")
    phrase = "The Quick Brown Fox Jumps Over They Lazy Dog"
    encoded = machine.encode(phrase)

    print(phrase)
    print(encoded)

    #encoded = machine.encode(encoded) #Encode again to prevent decrypt key from working
    #print(encoded)

    machine.orient_rotors("EWL") #Changing the key will prevent decryption

    print("Attempt to decode...")
    decoded = machine.encode(encoded)

    print(encoded)
    print(decoded)