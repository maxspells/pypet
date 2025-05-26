from pathlib import Path

savefile = Path("data.max")


def save_data(petclass):
    with open('data.max', 'w') as data:
        data.write(petclass.name + "\n")
        data.write(str(petclass.hunger) + "\n")
        data.write(str(petclass.energy) + "\n")
        data.write(str(petclass.happiness) + "\n")
        data.write(str(petclass.state) + "\n")         # Save the state as a string
        data.write(str(petclass.age_stage) + "\n")     # Save the age_stage
        data.write(str(petclass.age) + "\n")           # Save the age


def load_data(petclass):
    if savefile.is_file():
        with open(savefile, 'r') as data:
            lines = data.readlines()
            name = lines[0].strip()
            hunger = float(lines[1].strip())
            energy = float(lines[2].strip())
            happiness = float(lines[3].strip())
            state = lines[4].strip()                   # Load the state as a string
            age_stage = lines[5].strip()
            age = float(lines[6].strip()) if len(lines) > 6 else 0

            pet = type(petclass)(name, age_stage=age_stage)  # Pass age_stage to constructor
            pet.energy = energy
            pet.hunger = hunger
            pet.happiness = happiness
            pet.state = state
            pet.age_stage = age_stage
            pet.age = age
            return pet
    else:
        return None  # Or create a new default pet if you want
