from navbot_x_isaac_lab.demo.inspection_mission import InspectionMission


def main():
    mission = InspectionMission()
    mission.describe()
    print()
    mission.run_demo()
    print()
    print("Phase-1 flagship mission scaffold is ready for future Isaac Sim scene integration.")


if __name__ == "__main__":
    main()