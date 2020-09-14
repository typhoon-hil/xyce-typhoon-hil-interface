# Quick-start guide

Follow this guide to set up everything needed to build circuit schematics with Typhoon HIL software and simulate using the Xyce open-source engine.
There are four main steps:
1) Downloading and installing Typhoon HIL Control Center
2) Downloading and installing Xyce
3) Setting up the Typhoon HIL/Xyce interface
4) Building a circuit model

## 1) Typhoon HIL Control Center

If you already have Control Center installed you can ignore these steps, but we highly recommend an update to the latest version

1) Go to https://www.typhoon-hil.com/products/hil-software/
2) In the *Test drive on Virtual HIL* section, click *Download*
3) Fill in the details and submit
4) The installation is straightforward
5) Open the Typhoon HIL Control Center and on the main window, click *Schematic Editor*
6) Wait for the first run setup to finish and close the Control Center

## 2) Xyce
1) Go to Xyce's website: https://xyce.sandia.gov/
2) Click *Download*, then on the left panel, find *Executables*
3) Find the Windows version (the only one supported for now)
4) Download and install
5) Open a **new** Windows Command Prompt and enter the command *xyce*. You should see the following output:

```
Netlist not found on command line
Usage: xyce [arguments] netlist
Use -h argument to get additional help info
```

In case the command is not found, check the extra step at the end of this guide.

## 3) Xyce to Typhoon Schematic Editor converter

1) Go to the master branch of the repository: https://github.com/typhoon-hil/xyce-typhoon-hil-interface
2) Download the contents by clicking the *Clone or download* button then *Download ZIP*
3) Extract the *xyce-typhoon-hil-interface-master* folder
4) With Typhoon HIL Control Center closed, run *install.bat*

## 4) Building a model and simulating

1) Open the Control Center and click on the Schematic Editor
2) You can use elements from the *xyce_lib* library to build your circuit*
3) After the circuit is built, add a *XyceSim* component and double-click it to open the mask
4) Enter the simulation parameters
5) Click on *Start simulation*
6) A window opens with the text output from the *Xyce*
7) If the simulation finishes successfully, a *Signal Analyzer* window opens automatically

You can also find circuit examples within the *xyce-typhoon-hil-interface-master/examples* folder.

## Extra step

In case the *xyce* command was not recognized, you need to add Xyce's path to the environment variables:

1) Type *cmd* in the windows search bar, right-click the Command Prompt icon and select *Open as Administrator*
2) In the command prompt window, paste this: *rundll32.exe sysdm.cpl,EditEnvironmentVariables* and press *Enter*
3) Find *Path* on *System's Variables*, click *Edit* then *New*
4) Enter the path to Xyce's installation folder + *\bin* (e.g. *C:\Program Files\Xyce 7.00 OPENSOURCE\bin*)*
5) Accept the changes by clicking *OK* on both windows
6) Open a **new** Command Prompt window and test the *xyce* command again

> Don't change or remove any other path variable, as it may break the operation of other software
