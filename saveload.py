from pathlib import Path
import item

savefile = Path("data.max")


def save_data(petclass, world_items=None):
    with open('data.max', 'w') as data:
        data.write(petclass.name + "\n")
        data.write(str(petclass.hunger) + "\n")
        data.write(str(petclass.energy) + "\n")
        data.write(str(petclass.happiness) + "\n")
        data.write(str(petclass.state) + "\n")
        data.write(str(petclass.age_stage) + "\n")
        data.write(str(petclass.age) + "\n")
        data.write(str(petclass.idle_time) + "\n")
        data.write(str(petclass.next_wander_time) + "\n")
        data.write(str(petclass.rect.centerx) + "\n")
        data.write(str(petclass.rect.centery) + "\n")
        data.write(str(petclass.poop_timer) + "\n")
        # Save world items
        if world_items:
            data.write(str(len(world_items.items)) + "\n")
            for thing in world_items.items:
                # Save type and position (expand as needed)
                data.write(f"{thing.__class__.__name__},{thing.rect.x},{thing.rect.y}\n")
        else:
            data.write("0\n")


def load_data(petclass, world_items=None):
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
            poop_timer = float(lines[11].strip()) if len(lines) > 11 else 0

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
            pet.poop_timer = poop_timer

            # Load world items
            idx = 12  # Next line after poop_timer
            if len(lines) > idx:
                num_items = int(lines[idx].strip())
                idx += 1
                if world_items:
                    world_items.items.clear()
                    for _ in range(num_items):
                        if idx >= len(lines):
                            break
                        parts = lines[idx].strip().split(",")
                        if parts[0] == "Poop":
                            world_items.add_item(item.Poop(int(parts[1]), int(parts[2])))
                        # Add more item types here as needed
                        idx += 1
            return pet
    else:
        return None
