ORIGINAL PAPER

![](P3_Thies_2022_images/290dd646e6453473a439423ade66b72c420b53300d863915fb0b4aff246763cc.jpg)

# Investigation of the landing dynamics of a reusable launch vehicle and derivation of dimension loading for the landing leg

Christoph Thies<sup>1</sup>

Received: 14 February 2022 / Revised: 6 May 2022 / Accepted: 19 May 2022 / Published online: 19 July 2022 © The Author(s) 2022

## Abstract

The EU has deemed it crucial to maintain its own independent access to space. To foster the European industry competitiveness, the cost of the European launch systems needs to be reduced and flexibility needs to be improved. The development of reusable launch vehicle (RLV) is currently changing the global market of space transportation systems and is promising immense cost savings. Within this context, MT Aerospace has been investigating the configurations and possible solutions for landing structures at touch-down in the European Funded H2020 project RETALT. This includes the down-selection of previous designs to the current configuration for RETALT1 (Marwege et al. in System definition report, 2022) and the corresponding architecture of the structural landing leg. A screening of the overall requirements down to driving parameters which have the most significant impact on the structural design is done. Landing events like “nominal” simultaneously fou leg touch-down landings and critical single leg manoeuvres are analysed to evaluated safe configurations for landing. These investigations have a major influence on the specification of the launcher.

Keywords Landing leg · Shock loading · Mathematical model · Shock absorber · Requirements · Landing event

## Abbreviations

CFRP Carbon fibre reinforced polymer CoG Centre of gravity CAD Computer aided design D&D Design and Development ESA European Space Agency ECSS European Cooperation for Space Standardization FEM Finite Element Method FOSY Factor of safety yield FOSU Factor of safety ultimate FOSM Factor of safety mass MBD Multi body dynamic MF Model factor MoS Margin of safety QSL Quasi static load RETALT Retro propulsion assisted landing technologies RLV Reusable launch vehicle RT Room temperature SSTO Single-stage-to-orbit

SF Safety factor TSTO Two-stage-to-orbit TVC Thrust vector control VTVL Vertical take-of, vertical landing

## 1 Introduction

The EU has deemed it crucial to maintain its own independent access to space [1]. To foster the European industry competitiveness, the cost of the European launch systems need to be reduced and flexibility needs to be improved. The development of reusable launch vehicle (RLV) is currently changing the global market of space transportation systems and is promising immense cost savings. The only operational approach of RLV today is the Vertical Take-of Vertical Landing launcher (VTVL), which decelerates by firing its engines against the velocity vector, called retropropulsion and ultimately sets down vertically with the aid of landing structures.

The know-how in the technologies of retro-propulsion assisted landing in Europe is sparse. The RETro propulsion Assisted Landing Technologies (RETALT) project, funded by the European Union’s Horizon 2020 research and innovation framework program has been set up to investigate various aspects around retro-propulsion assisted landing. Its objective is to investigate technologies for reusable, verti cal take-of, vertical landing launch vehicles applying retropropulsion. Within this objective, the project aims to investigate the application to two-stage-to-orbit (TSTO) in the RETALT1 configuration, and single-stage-to-orbit (SSTO) in the RETALT2 configuration [2, 3].

Within this context, MT Aerospace has been investigating the configurations and possible solutions for landing structures, both for aerodynamic control during descent and touch-down. These investigations have been carried out in close collaboration with the project partner Almatech, who in turn have investigated the mechanisms needed for both structures.

This paper focuses on the development and explanation of a mathematical model to investigate the touch-down manoeuvres and further landing scenarios of the launcher. Furthermore, the derivation of the dimensioning loadings for touch-down structures for the RETALT1 configuration, from now on referred to as the landing legs, are made.

The paper is laid out as follows. First, the Sect. 2 discusses the design approach and the down-selection of the most promising landing leg design. Then, the detailed design of this down-selected landing leg solution and its shock absorber properties is described in Sects. 3 and 4. For this aim, the dimensioning loading is derived in Sect. 5. Lastly, an analysis of the landing event is performed. The paper draws a conclusion and an outlook of future work is given.

## 2 Down‑selection of the landing legs concept

The down-selection lists the development of the landing leg design from a large variety of concepts to the current status, which is represented in this paper as the tripod configuration.

## 2.1 Overview of landing gear concepts for reusable launcher

The overview of the landing gear concepts shown in (see Fig. 1) represents five variations of leg arrangements.

The concepts 1 and 2 are identical in the design/concept, but vary in the number of landing legs and the corresponding mass. The landing gear structural behaviour of these two concepts is based on two main components: the absorber system (carries compression loading) and the landing leg (carries tension loading). During the ascend of the launch vehicle the landing gear is retracted in the core stage until it will be deployed when the launch vehicle reaches landing velocity close to the ground. The integral architecture of the landing legs inside the core stage is not further analysed in this paper. The focus is on the deployed legs. The concepts 3 and 4 feature a diferent deployment system, resulting in a diferent kinematic behaviour [8].

The concepts with the number of legs and the corresponding mass estimates are summarized in Table 1. Each landing leg concept difers in the masses of the individual components but account for approx. the same total mass of 4000 kg [2]

<table><tr><td>Concept 1 and 2 (tripod config.)</td><td>Concept 3 (parallel linkage config.)</td><td>Concept 4 (cantilever config.)</td></tr><tr><td></td><td></td><td></td></tr></table>

Fig. 1 Overview of concepts for diferent landing leg configurations [4, 5]

<table><tr><td rowspan="5">Table 1 Overview of concepts for different landing leg configurations incl. mass</td><td></td><td>Concept 1 (tripod config.)</td><td>Concept 2 (tripod config.)</td><td>Concept 3 (parallel linkage config.)</td><td>Concept 4 (cantilever config.)</td></tr><tr><td>Number of legs</td><td>4</td><td>8</td><td>6</td><td>6</td></tr><tr><td>Estimated leg structure mass (/leg) [kg]</td><td>536</td><td>186</td><td>356</td><td>139</td></tr><tr><td>Mass for motorization (/leg) [kg]</td><td>464</td><td>314</td><td>311</td><td>528</td></tr><tr><td>Total mass (/leg) [kg]</td><td>1000</td><td>500</td><td>667</td><td>667</td></tr></table>

## 2.2  Assessment of the proposed landing gear concepts

During the development process multiple critical categories of the diferent concepts of the landing leg were assessed:

• Performance structural performance e.g. buckling, deployment speed of landing leg.

• Design & Development risk (D&D) scalability for other projects.

• Cost cost of manufacturing e.g. expensive materials, complex processes.

• Integration storing of landing leg e.g. launch lock installation, large number of electrical components.

• Life and Reliability failure assessment of components e.g. deployment of landing legs

Advantages and disadvantages of concept 1–4 concerning structural designs were assessed and are scored by points in Table 2. The criteria are multiplied by weighting factors according to their importance according reliability defined in [8].

Under the criteria in Table 2, the diferent concepts were assessed and concept 1 was selected as most promising. Despite the slightly higher scoring of concept 2, depending on the weighting factors, the 4-leg configuration includes lower number of active components which could fail. This leads to an increase in reliability in the single components, which favours concept 1 over 2.

## 3  Design parameters

The design parameters for the RETALT1 launcher configuration in the early stage of the project include well defined boundary conditions, e.g. the diameter or height of the launcher vehicle and also assumptions such as the centre of gravity (CoG) of the rocket, which depends mainly on the design of the rocket (internal structure, tanks or engines). A major driver is the fuel consumption for the retro-propulsion, which influences the mass distribution.

Nevertheless, design parameters are defined by a parameter envelope, which shall cover the uncertainties of boundary conditions. These definitions are summarized in the following chapters.

## 3.1 Geometry and mass of the tripod configuration

In this chapter, the main inputs of geometry and mass of the launcher are summarized. They are used for the description of the multi body dynamics (MBD) mathematical model in the following chapters. These inputs are the nominal values for the launcher. The mass of the complete core stage is divided into the core stage per se (core stage without landing structures), the landing legs and the damping system. The inertia and the CoG are extracted from the RETALT1 configuration report [2] (see Table 3).

The geometry and major fixation points of the landing leg and the damping system are presented in the Fig. 2 below. It describes the position of the legs before touch-down with the launcher in the unloaded, fully deployed as well as in final parking position.

Table 2 Trade-of results

<table><tr><td>Criteria</td><td>Weighting factor</td><td>Concept 1 (4 legs)</td><td>Concept 2 (8 legs)</td><td>Concept 3 (6 legs)</td><td>Concept 4 (6 legs)</td></tr><tr><td>Performance</td><td>1.2</td><td>4.8</td><td>4.8</td><td>3.6</td><td>4.3</td></tr><tr><td>D&amp;D Risk</td><td>0.6</td><td>2.0</td><td>2.0</td><td>1.9</td><td>2.1</td></tr><tr><td>Cost</td><td>1</td><td>4.2</td><td>3.8</td><td>3.2</td><td>3.8</td></tr><tr><td>Integration</td><td>0.8</td><td>3.0</td><td>3.0</td><td>3.0</td><td>3.4</td></tr><tr><td>Life &amp; Reliability</td><td>1.4</td><td>4.2</td><td>4.7</td><td>3.7</td><td>4.0</td></tr><tr><td>Final Score</td><td>-</td><td>3.64</td><td>3.66</td><td>3.09</td><td>3.52</td></tr></table>

Table 3   Overview of the geometry, mass, CoG and inertia of nominal landing configuration

<table><tr><td>Component size</td><td>[m]</td><td></td></tr><tr><td>Height of launcher</td><td>103</td><td rowspan="17"></td></tr><tr><td>Height of core stage</td><td>64.7</td></tr><tr><td>Launcher base diameter</td><td>6</td></tr><tr><td>Engine length</td><td>1.902</td></tr><tr><td>Nozzle diameter</td><td>1.095</td></tr><tr><td>Allowed clearance below nozzle at static equilibrium</td><td>0.5475</td></tr><tr><td>Masses</td><td>[kg]</td></tr><tr><td>Core stage dry mass (incl. margins)+ landing legs</td><td>59288</td></tr><tr><td>Propellant mass at touch-down</td><td>2000</td></tr><tr><td>Landing legs/damping system total</td><td>4000</td></tr><tr><td>Landing mass (Dry Mass + Residual Propellant)</td><td>61288</td></tr><tr><td>CoG of core stage (deployed landing leg)</td><td>[m]</td></tr><tr><td>at landing (from launcher base)</td><td>22.059</td></tr><tr><td>Inertia</td><td>[kg*m2]</td></tr><tr><td>Ixx (pitch)</td><td>2.57*107</td></tr><tr><td>Iyy (roll)</td><td>3.76*105</td></tr><tr><td>Izz (yaw)</td><td>2.57*107</td></tr></table>

Bold values highlight the input parameters for the calculations

![](P3_Thies_2022_images/7a464b63c9b405d23c3f33e4ce98adc775c52fd24a25d6357d6f14875c07f6c9.jpg)  
Fig. 2 Schematic representation of kinematic points in deployed unloaded configuration

These points are defined as follows:

• B: Fixation point of landing leg at core stage.

• P: Ref. point damper hinge and landing leg in deployed unloaded configuration.

• K: Rotation point between damper and support structure of deploying system.

• T: Upper fixation of the support structure of the deploying system.

• β\_0: Angle between damper hinge plane and landing leg.

• β\_1: Angle between damper hinge plane and damper system.

Based on the final design configuration (see Sect. 2.2) and the geometrical inputs (see Table 4) listed in this chapter, the mathematical model of Sect. 5.1.1 is created.

## 3.2 Safety concept and requirements

The requirement specification summarizes the general requirements and safety concepts of the European Cooperation for Space Standardization (ECSS) and the RETALT1 specific boundary conditions. This considers the landing environment and the kinematic conditions such as landing velocity, cross-winds, friction coeficient on the platform and the inclination angle of the launcher itself. The specification diferentiates between nominal and the envelope requirements.

## 3.2.1 ECSS/RETALT safety factors

The ECSS safety philosophy is listed in Table 5.

## 3.2.2 Requirements

The requirements cover diferent flight scenarios of the launch vehicle during landing on a 50 m × 50 m floating platform or on the mainland. These parameters (Table 6) are a first assumption and will be analysed in Sect. 6 to proof their acceptance for a stable landing and to reach the parking position. For the worst-case investigation, the scenario on floating platform is analysed, for which the total inclination angle is larger, because of the additional angle caused by the swell of the sea. Also, the space on the platform is limited, which could cause damage on the launcher when the launcher starts to slide of the platform after touch-down.

The analyses consider diferent boundary conditions such as landing speed, inclination angles of the launcher and platform (see Table 6). Further parameters which are analysed in future programmes, such as friction or damping characteristics are crucial elements for guaranteeing the integrity of the launcher during landing.

<table><tr><td rowspan="10">Table 4 Geometry of landing leg and deployable landing gear</td><td>Name</td><td colspan="3">Symbols</td><td>Inputs</td></tr><tr><td>Selected configuration (Deployed unloaded)</td><td colspan="3"></td><td>Tripod</td></tr><tr><td>Number of legs</td><td colspan="3"></td><td>4</td></tr><tr><td>Height of upper attachment T from hinge plane [m]</td><td colspan="3">h1 (T)</td><td>9.0</td></tr><tr><td>Height of upper attachment K from hinge plane [m]</td><td colspan="3">h (hk)</td><td>5.7</td></tr><tr><td>Height of lower attachment B from hinge plane [m]</td><td colspan="3">h2</td><td>4.4</td></tr><tr><td>Angle of leg to hinge plane (static case) [°]</td><td colspan="3">Beta 0</td><td>33</td></tr><tr><td>Angle of strut to hinge plane (static case) [°]</td><td colspan="3">Beta 1</td><td>51</td></tr><tr><td>Leg length [m]</td><td colspan="3">L_leg [PB]</td><td>8.1</td></tr><tr><td>Strut length [m]</td><td colspan="3">L_strut [PT/KP]</td><td>11.2/7.4</td></tr><tr><td rowspan="5">Table 5 ECSS safety factors</td><td>Description</td><td>Value</td><td>Comment</td><td>Chapter</td><td>Reference</td></tr><tr><td>Safety factors (SF)</td><td></td><td></td><td></td><td></td></tr><tr><td>A SF of 1.1 on the applied load to obtain the yield load</td><td>1.1</td><td>FOSY</td><td>4.3.2.1</td><td>[7]</td></tr><tr><td>A SF of 1.25 on the applied load to obtain the ultimate load</td><td>1.25</td><td>FOSU</td><td>4.3.2.1</td><td></td></tr><tr><td>A third margin of 1.2 as a model factor</td><td>1.2</td><td>MF</td><td>4.1.4.2</td><td></td></tr></table>

Table 6 Envelope of landing variables of all possible landing manoeuvres for the VTVL launcher

<table><tr><td></td><td>Units</td><td>Nominal</td><td>Min</td><td>Max</td><td colspan="2">Orientation about vertical axis</td><td>Comment</td></tr><tr><td>Launcher incident angle</td><td>°</td><td>0</td><td>0</td><td>10</td><td>-180</td><td>180</td><td>Includes off-axis landing of launcher and effect of waves on platform at sea</td></tr><tr><td>Launcher touch-down vertical velocity</td><td>m/s</td><td>5</td><td>1</td><td>15</td><td>0</td><td>0</td><td>Includes launcher residual velocity and effects of waves during sea landing. (absolute numbers)</td></tr><tr><td>Launcher touch-down lateral velocity</td><td>m/s</td><td>0</td><td>0</td><td>5</td><td>-180</td><td>180</td><td>Includes effect of 5 s cross-wind of 50 km/h at touch-down</td></tr><tr><td>Launcher touch-down pitch rotational velocity</td><td>°/s</td><td>0</td><td>0</td><td>2</td><td>-180</td><td>180</td><td></td></tr><tr><td>Launcher touch-down yaw rotational velocity</td><td>°/s</td><td>0</td><td>0</td><td>2</td><td>-180</td><td>180</td><td></td></tr><tr><td>Launcher touch-down roll velocity</td><td>°/s</td><td>0</td><td>0</td><td>2</td><td>0</td><td>0</td><td></td></tr><tr><td>Cross-wind</td><td>km/h</td><td>0</td><td>0</td><td>50</td><td>-180</td><td>180</td><td>Considers effect of cross-wind on tipping of launcher once landed</td></tr><tr><td>Friction coefficient between platform and landing legs</td><td></td><td>0.5</td><td>0.1</td><td>1</td><td></td><td></td><td></td></tr><tr><td>Launcher mass at touch-down</td><td>t</td><td>61.3</td><td>[2]</td><td>[2]</td><td></td><td></td><td></td></tr></table>

## 3.2.3  Landing parameters for multi‑body‑dynamics (MBD) simulation

The listed variables are the inputs which are used for a preliminary dynamic touch-down MBD simulation of the launcher to derive the reaction forces. They are extracted from Table 6. The data in Table 7 are limit loads.

## 3.3  Final design concept for further analysis

The chosen concept 1, that is selected for the analysis, is shown in Fig. 3. The principle of concept 1 is an inverted tripod configuration with a locking mechanism. The landing gear consists of the landing leg and an absorber system placed inside the core stage (see Fig. 3A), which is unfolded during descent flight close to the ground. The landing gear comprises several subcomponents as shown in Fig. 3B.

## 4 Shock absorber properties

The absorber characteristics shown in Figs. 4 and 5 are iteratively determined by numerical simulation.

In Fig.  4, the stifness of the absorber is shown. The stroke and the resulting force describe the stifness of the spring, which is low at little displacement during landing and increase at higher displacement of the absorber. The highest stifness of the absorber reached at the maximum spring deflection guarantees that the launcher will not sink in at parking by the dead weight of the launcher and finally touches the ground due to creep efects. The negative values for stroke and force describe the compression mode of the shock absorber.

In Fig. 5 the damping of the four absorbers is described. This digressive progression of the damping guarantees that the resulting force on the absorber is constant over the whole deflection of the damper. This damper curve describes a shock absorber, which results in constant force distribution over the defined stroke, as shown in Sect. 5.1.2.

## 5 Derivation of dimensioning loading

This section describes the MBD simulation of the dynamic behaviour of the RETALT1 inverted tripod launcher configuration during landing and the derivation of the corresponding reaction forces in the landing leg and shock absorber.

## 5.1 Nominal landing assessment

The nominal landing assessment describes a touch-down scenario of the tripod configuration defined in Sect. 3 with an almost ideal shock absorber configuration, for which four landing pads touch simultaneously the ground. All four landing legs and absorbers experience the same loading. Based on the landing parameters Table 7, the reaction forces are determined.

## 5.1.1 MBD model

The simulation at MT-Aerospace is performed with multi body dynamics MSC software Adams, which is able to predict large translational and rotational motions of structural rigid components.

The MBD model includes mass distribution of diferent components:

• Core stage (rigid body)

• Landing legs (rigid body)

• Landing pads (rigid body)

• Damping system (spring damper system)

• Landing platform (mass-spring-damper system)

This leads to the global mass of inertia shown in Table 3.

Table 7   Specified variables for landing scenario

<table><tr><td>Design variables</td><td>Unit</td><td>Values</td><td>Remarks</td></tr><tr><td>Launcher incident angle</td><td>°</td><td>0</td><td>Initial assumption</td></tr><tr><td>Launcher touch-down axial velocity (Design velocity  $v_z$ )</td><td>m/s</td><td>5</td><td></td></tr><tr><td>Launcher touch-down lateral velocity</td><td></td><td>0</td><td></td></tr><tr><td>Yaw, pitch, role velocity</td><td></td><td>0</td><td>Initial assumption</td></tr><tr><td>Number of first legs touch-down</td><td>-</td><td>4</td><td></td></tr><tr><td>Cross-wind</td><td>km/h</td><td>0</td><td>Initial assumption</td></tr><tr><td>Launcher mass at touch-down</td><td>kg</td><td>61,288</td><td>Stage Mass empty incl. margin [1]</td></tr><tr><td>Defined temperature by MTA during landing</td><td>K</td><td>294</td><td>RT (room temperature)</td></tr><tr><td>Friction coefficient between platform and landing legs</td><td>-</td><td>-</td><td>No friction assumed in the early phase of load derivation</td></tr><tr><td>Kinetic energy of launcher at touch-down</td><td>kJ</td><td>766</td><td>Assuming nominal configuration</td></tr></table>

Fig. 3   Tripod configuration [6]  
![](P3_Thies_2022_images/803e333ce5d9ebc708b8ae500f2510c3b004932c4b235fcbf1df9e1d872ba70e.jpg)

![](P3_Thies_2022_images/bfb938b4b025de62024aea22234a3daa51848b61e214e37de279617d39255bbc.jpg)  
Fig. 4 Spring property of the absorbers

![](P3_Thies_2022_images/58c1d11873c0f7d72a6367e59197301766ebf82125e217ad370f79aecee7bb66.jpg)  
Fig. 5 Damper property of the absorbers

The detailed VTVL geometry (CAD landing legs folded) is shown in Fig. 6A which is transferred by Adams to a rigid body model with deployed landing legs (B).

The reference coordinate system for the MBD model is shown in Fig. 7 and is centred in the plane through the lower ends of the launcher legs.

![](P3_Thies_2022_images/3e63e6a533e3dad25d16c46f88ba3344245bc774f3bd99b77a5cf5f928a77b3b.jpg)

![](P3_Thies_2022_images/460c7fa5bd9edb1b3e70f599dcfafa8579eec24f81d574480ba5b1c25bdbd025.jpg)  
Fig. 6 CAD and MBD (MSC Adams) model of RETALT1  
Fig. 7 Overview of main reference frame and CoG

## 5.1.2 Results of the MBD analysis

The results of nominal landing analysis include the axial touch-down force per leg, the displacement in the spring damper system and the nozzle clearance, which means the minimum distance between the nozzle and landing pad during landing. The results are calculated with shock absorber properties as presented in Sect. 4.

5.1.2.1 Energy MT-Aerospace has applied a shock absorber in the mathematical model, which guarantees that no shock wave, represented by large peak force, runs through the landing legs and causes structural damage or overloading. The force in the absorber is kept approx. constant over the total stroke of the absorber until the kinetic energy is fully absorbed and the launcher reaches parking position.

To compare the numerical simulation with an analytical approach, the work/energy equation is applied:

$$
\Delta E _ {\mathrm{kin}} = W _ {\mathrm{Accel}} = \int_ {0} ^ {s} F \times \mathrm{d} s.
$$

Figure 8 shows the result of the numerical simulation in comparison with the ideal shock absorber behaviour. The red curve represents the force over displacement. The area below this curve, describes the MBD energy distribution with shock absorber properties of Sect. 4. The blue curve describes the force over displacement, too, but for the ideal absorber and the corresponding energy distribution. The nonlinear efects of the red curve are caused by the spring damper system properties in Sect. 4, which do not represent an ideal shock absorber configuration. Therefore, the reaction forces are also nonlinear, especially when the stroke reaches its maximum and absorber properties show larger gradients in the stifness (see Fig. 4).

Fig. 8 Comparison between ideal and simulated shock absorber behaviour  
![](P3_Thies_2022_images/9d47c8a6d1ca05df5dc356351cdb927c96161b14de373c25c7d420664fbde682.jpg)

5.1.2.2 Reaction forces In this chapter the reaction forces are numerically determined in the landing leg and in the shock absorber over a duration of three seconds. Additionally, the stroke of the damper during landing is plotted. During touch-down, the loading of the damper and legs occurs in three phases as indicated in Fig. 9:

I. Fast increase of force in the absorber at touch-down. II. Constant loading over approximately total stroke.

III. Unloading until static equilibrium of the launcher is reached.

The oscillations of the forces in Fig. 9 are caused by the contact definition and is a numerical efect. A physical reason for the oscillation due to friction can be excluded since no friction is applied.

5.1.2.3 Clearance between nozzle and platform This section shows the translation in axial direction of the nozzle towards the landing platform. The distance between nozzle end and landing platform is initially 2200 mm and is reduced during landing to 570 mm until the launcher reaches parking position. Therefore, the nozzle does not touch the ground and the requirement of the allowed minimum distance of

Fig. 9 Forces per damper/leg and stroke of the absorber  
![](P3_Thies_2022_images/2fdfa2cf6697c5e1f3070495b32eb5fd2f44fd4439c6087c4f80f667379d83a2.jpg)

Fig. 10   Nozzle clearance during landing  
![](P3_Thies_2022_images/d8f34df50cad3ac3bfa64ab57a9620d19a16c736835f98e32e3426e3256c2d1b.jpg)

![](P3_Thies_2022_images/c7b24ebaed1bee8c5caec17ca191fc93e485afd31ae24bd280264f64ceb9bef6.jpg)  
Fig. 11 Leg Alignment and orientation (top view of the launcher)

547.5  mm (see Table  3) is not violated. The diagram is divided into two phases of the landing (see Fig. 10):

I. Landing phase with touch-down 0.0 until 0.5 s.

II. Parking phase 0.5 until 3 s.

5.1.2.4 Summary of  results of  nominal landing This section shows the maximum forces and displacements under the design configurations of Table 7 and Sect. 4 during landing, exemplarily for leg number 4. The MBD coordinates x, y and z are aligned as shown in Fig. 11.

The maximum reaction forces in the landing leg and in the absorber system are shown in Table 8.

The simulated values in Table 8 represent the dimensioning loadings for the nominal landing for the landing legs. These loads will be used for a further strength finite element method (FEM) analysis of the landing leg in the future. The reaction forces are determined as quasi static loading (QSL).

## 6 Analysis of landing events

The landing analysis of landing events via MBD model includes the investigation, if the launcher vehicle RETALT1 is able to touch-down safely and reach a stable parking position.

This assessment considers constant spring damper properties. It encompasses landing variables from Table 6 as well as additional variables such as friction (stick, slip) and inclination angles of the launcher and the platform. Since the launcher will land on a floating platform on the sea, the platform is mainly afected by the sea state. This includes rough swell, which defines the inclination of the platform or the ground conditions of the landing pad.

Table 8 Results of simulation

<table><tr><td rowspan="2">Nozzle clearance [mm]</td><td rowspan="2">Deformation damper magnitude [mm]</td><td colspan="4">Leg force (Leg 4) [kN]</td><td>Spring damper force [kN]</td></tr><tr><td>Mag</td><td>X</td><td>Y</td><td>Z</td><td>Mag</td></tr><tr><td>570</td><td>420</td><td>902</td><td>814</td><td>387</td><td>0</td><td>935</td></tr></table>

![](P3_Thies_2022_images/83c52c2c060ca15e477aeee068602ae8e51f07b29121fde2379a91a6f21165da.jpg)  
Fig. 12 Landing event with inclination of landing platform

It has to be mentioned that due to inclination of the platform (see Fig. 12), the landing pad, which comes in first contact with the platform will exhibit the highest loading and deformation. Therefore, the stifness is increased (see Fig. 12) to ensure that the clearance between the nozzle and the platform is established and no touching between nozzle and platform occurs. For the single leg touch-down, the clearance is lower than one half of the nozzle diameter, which is the minimum allowable for the nominal case (see Table 3) but this is considered acceptable in the current status of the project. Increasing of the damping minimizes the oscillation of the structure and the rebound of the launcher vehicle is reduced to a minimum. At the current status, crash cushions to compensate overloading due to landing on a single leg are not applied. This will be considered in future investigations (see Table 9).

In the analysis, the following major inputs are applied:

The assessment in this chapter shall give an orientation if the assumptions of the landing variables in Table 6 are acceptable or have to be modified to reach parking position.

Out of Table  10, a first set of parameters can be identified which are critical for the landing event and ensure a safe parking configuration. Given the assumptions described above, the major drivers for this landing assessment are the inclination angle of the platform and the launcher, friction and positive defined lateral velocity. The focus of the future investigations will be on these parameters.

Table 9 Input variables of MBD model for landing event analysis

<table><tr><td>IXX [kg × m2]</td><td>IYY [kg × m2]</td><td>IZZ [kg × m2]</td><td>Mass [kg]</td><td>Stiffness damper [N/mm]</td><td>Stiffness platform [N/mm]</td><td>Damping damper [Nsec/mm]</td><td>Damping platform [Nsec/mm]</td></tr><tr><td>Table 3</td><td></td><td></td><td></td><td>2600.0</td><td>100,000.0</td><td>1300.0</td><td>10.0</td></tr></table>

Table 10 Results of first landing event simulation

<table><tr><td rowspan="2">Mass core stage [t]</td><td rowspan="2">Total mass [t]</td><td rowspan="2">Velocity v_0 axial [m/s]</td><td rowspan="2">Velocity v_0 lateral [m/s]</td><td rowspan="2">Friction [Stick]</td><td rowspan="2">Friction [Slip]</td><td rowspan="2">Inclination Angle [°]</td><td colspan="3">Reach parking position</td></tr><tr><td>yes</td><td>no</td><td>comment</td></tr><tr><td rowspan="19">59.3</td><td rowspan="4">61.3</td><td>-15.0</td><td rowspan="8">0.0</td><td>0.5</td><td rowspan="17">0.1</td><td rowspan="5">10.0</td><td>-</td><td>x</td><td>sliding from Pad</td></tr><tr><td rowspan="3">-5.0</td><td>0.5</td><td>x</td><td>-</td><td>less sliding no drop off from pad</td></tr><tr><td>0.3</td><td>-</td><td>x</td><td>sliding from Pad</td></tr><tr><td>0.4</td><td>-</td><td>x</td><td>sliding from Pad</td></tr><tr><td>66.3</td><td>-5.0</td><td>0.5</td><td>x</td><td>-</td><td>less sliding no drop off from pad</td></tr><tr><td rowspan="14">61.3</td><td rowspan="3">-15.0</td><td>0.5</td><td rowspan="3">5.0</td><td>x</td><td>-</td><td>less sliding no drop off from pad</td></tr><tr><td>0.3</td><td>x</td><td>-</td><td>less sliding no drop off from pad</td></tr><tr><td>0.1</td><td>x</td><td>-</td><td>less sliding no drop off from pad</td></tr><tr><td>-4.3</td><td>-5</td><td rowspan="5">0.5</td><td rowspan="5">10</td><td>x</td><td>-</td><td>less sliding no drop off from pad</td></tr><tr><td>-5.5</td><td>5</td><td>-</td><td>x</td><td>sliding from Pad</td></tr><tr><td>-5.5</td><td>4</td><td>-</td><td>x</td><td>sliding from Pad</td></tr><tr><td>-4.5</td><td>3</td><td>-</td><td>x</td><td>sliding from Pad</td></tr><tr><td>-4.5</td><td>0.5</td><td>x</td><td>-</td><td>less sliding no drop off from pad</td></tr><tr><td rowspan="6">-15</td><td>5</td><td>0.1</td><td rowspan="6">5</td><td>-</td><td>x</td><td>sliding from Pad</td></tr><tr><td>3</td><td>0.5</td><td>-</td><td>x</td><td>sliding from Pad</td></tr><tr><td rowspan="2">1</td><td>0.1</td><td>-</td><td>x</td><td>sliding from Pad</td></tr><tr><td rowspan="3">0.5</td><td>x</td><td></td><td>large sliding no drop off from pad</td></tr><tr><td rowspan="2">5</td><td>0.5</td><td>-</td><td>x</td><td>launcher is tipping</td></tr><tr><td>0.2</td><td>x</td><td>-</td><td>large sliding no drop off from pad</td></tr></table>

## 7 Conclusion and future work

In this paper, MT-Aerospace presented the development of a mathematical model with the commercial software MSC Adams, which describes the dynamic behaviour of the RETALT1 configuration during landing, assuming rigid elements.

With the developed mathematical model MT-Aerospace is able to derive dimensioning loadings for structural com ponents e.g. landing legs on system level in the early development stage of a launcher. Additionally, diferent complex landing scenarios for a stable landing to reach parking position can be analysed. The model is able to consider diferent launcher masses, landing velocities, platform configurations (e.g. inclination of platform caused by the swell) and friction. Using this mathematical model, MT-Aerospace can predict landing manoeuvres on system level for VTLV launchers. Furthermore, the model is able to describe the kinetic functionality, the dissipation of energy of the shock absorbers by the corresponding functions of force over velocity for the damping and force over stroke for the spring stifness. These non-linear functions for the spring damper system represent characteristics such as diferent fluid prop erties and mechanical mechanisms such as closing or opening of the valves in the damper.

The future work for MT-Aerospace is to apply the detailed shock absorber characteristics, derived from the upcoming drop test, on the mathematical model and to correlate the mathematical model with the test results concerning the dynamic behaviour.

Particularly for critical landing manoeuvres such as landing on one leg where an overloading of the absorber is expected, a crush cushion will be applied. The consideration of this will be considered in the future work.

Furthermore, the current mathematical model shall be extended to a coupled simulation between rigid and flexible components like the stifness representative components of the landing legs. The landing legs made of carbon fibre reinforced plastic (CFRP) and 3D printed high strength components (i.e. Ti-6-4) will be further dimensioned with respect to strength and stability using FEM. The mathematical model derived for the RETALT 1 configuration is set up in generalized manner such that it could be used in future programs such as Themis.

Acknowledgements The RETALT project has received funding from the European Union’s Horizon 2020 research and innovation framework program under grant agreement No 821890.

Open Access This article is licensed under a Creative Commons Attribution 4.0 International License, which permits use, sharing, adaptation, distribution and reproduction in any medium or format, as long as you give appropriate credit to the original author(s) and the source, provide a link to the Creative Commons licence, and indicate if changes were made. The images or other third party material in this article are included in the article's Creative Commons licence, unless indicated otherwise in a credit line to the material. If material is not included in the article's Creative Commons licence and your intended use is not permitted by statutory regulation or exceeds the permitted use, you will need to obtain permission directly from the copyright holder. To view a copy of this licence, visit http://creativecommons.org/licenses/by/4.0/.

## References

1. COM (2016) 705-Communication from the Commission to the European Parliament, the Council, the European Economic and Social Committee and the Committee of the Regions, European Commission (2016)

2. Marwege, A., Klevanski J., Riehmer J.: System Definition Report (2022)

3. Marwege, A., Gülhan, A., Klevanski, J., Riehmer, J., Kirchheck, D., Karl, S., Bonetti, D., Vos, J., Jevons, M., Krammer, A., Carvalho, J.: Retro Propulsion Assisted Landing Technologies (RETALT): current status and outlook of the EU funded project on reusable launch vehicles. In: 70th International Astronautical Congress (IAC), Washington D.C., United States, 21–25 October 2019

4. New Shepard. https://www.blueorigin.com/new-shepard. 2022. Accessed 18 Jan 2022

5. New Glenn. https://www.blueorigin.com/new-glenn. 2022. Accessed 18 Jan 2022

6. Krammer A., Blech L., Lichtenberger M.: Fin actuation vector control and landing leg mechanism design for the RETALT VTVL launcher (-)

7. Authors: ECSS-E-ST-32.10C Rev 1 (2009)

8. Jevons, M., Krammer A., Starke P., Lichtenberger M.: Structural Concept Report (2019)

Publisher's Note Springer Nature remains neutral with regard to jurisdictional claims in published maps and institutional afiliations.