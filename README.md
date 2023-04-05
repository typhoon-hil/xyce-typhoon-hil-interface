# Quick-start guide

Follow this guide to set up everything needed to build circuit schematics with Typhoon HIL software and simulate using the Xyce open-source engine.
There are four main steps:
1) Downloading and installing Typhoon HIL Control Center (THCC)
2) Downloading and installing Xyce
3) Installing the TSE to Xyce converter package
4) Building a circuit model

## 1) Typhoon HIL Control Center

If you already have Control Center installed you can ignore these steps, but we highly recommend an update to the latest version

1) Go to https://www.typhoon-hil.com/products/hil-software/
2) Click *Download Control Center*
3) Register and get a download link
4) Install Typhoon HIL Control Center

## 2) Xyce
1) Go to Xyce's website: https://xyce.sandia.gov/
2) Click *Downloads | Executables*
3) Find the Windows version (only Windows is supported for now)
4) Download and install

## 3) Typhoon Schematic Editor to Xyce converter

1) Open Typhoon HIL Control Center (close existing Schematic Editor windows) and click on *Additional tools*
2) Click on *Package Manager*
3) In the *Marketplace* tab, locate Xyce
4) Click the *Install* button

## 4) Building a model and simulating

1) Open the Schematic Editor
2) You can use elements from the *xyce_lib* library to build your circuit*
3) After the circuit is built, add a *XyceSim* component from the *Special* category and double-click it to open the mask
4) Enter the simulation parameters
5) Click on *Start simulation*
6) A window opens with the text output from the Xyce simulator
7) If the simulation finishes successfully, a *Signal Analyzer* window opens automatically

- You can also find circuit examples in the *Examples* tool on THCC after installing the package