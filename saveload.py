from pathlib import Path

savefile = Path("data.max")


def save_data(petclass):
    with open('data.max', 'w') as data:
        data.write(petclass.name + "\n")
        data.write(str(petclass.hunger) + "\n")
        data.write(str(petclass.energy) + "\n")
        data.write(str(petclass.happiness) + "\n")
        data.write(str(petclass.state) + "\n")
        data.write(str(petclass.age_stage) + "\n")
        data.write(str(petclass.age) + "\n")
        data.write(str(petclass.idle_time) + "\n")         # Save idle_time
        data.write(str(petclass.next_wander_time) + "\n")  # Save next_wander_time
        data.write(str(petclass.rect.centerx) + "\n")      # Save X position
        data.write(str(petclass.rect.centery) + "\n")      # Save Y position


def load_data(petclass):
    if savefile.is_file():
        with open(savefile, 'r') as data:
            lines = data.readlines()
            name = lines[0].strip()
            hunger = float(lines[1].strip())
            energy = float(lines[2].strip())
            happiness = float(lines[3].strip())
            state = lines[4].strip()
            age_stage = lines[5].strip()
            age = float(lines[6].strip()) if len(lines) > 6 else 0
            idle_time = float(lines[7].strip()) if len(lines) > 7 else 0
            next_wander_time = float(lines[8].strip()) if len(lines) > 8 else 0
            centerx = int(lines[9].strip()) if len(lines) > 9 else 400
            centery = int(lines[10].strip()) if len(lines) > 10 else 300

            pet = type(petclass)(name, age_stage=age_stage)
            pet.energy = energy
            pet.hunger = hunger
            pet.happiness = happiness
            pet.state = state
            pet.age_stage = age_stage
            pet.age = age
            pet.idle_time = idle_time
            pet.next_wander_time = next_wander_time
            pet.rect.center = (centerx, centery)
            return pet
    else:
        return None
