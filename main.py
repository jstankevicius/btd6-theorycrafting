from game_state import GameState

def main():
    gs = GameState(1250)
    gs.buy_farm()
    for farm in gs.Farms:
        print(farm)

if __name__ == "__main__":
    main()
