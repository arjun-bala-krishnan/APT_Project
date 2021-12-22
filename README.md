# APT Analyzer

About
Our APT-Analyzer is a simple python Qt application useful for analyzing raw APT data. It aids in the following functions.
1.	The application helps map the peaks of Atom Probe Tomography data with some additional controls during binning and peak resizing. 
2.	We can do additional file analysis after mapping on any program that can read the HDF file.
3.	We can find out monolayer volumes within the 3D-point cloud using a matplotlib viewer along any direction. The extracted .doc file contains other ions inside the monolayers before or after decomposition.
4.	Similarly, we can identify an abstract 3D ion cloud within the data after using DBSCAN to remove noises. The 'convex hull' algorithm then prepares the contour to extract the other ions.
5.	We can find the GM-SRO parameter of the data among two species (or collection) of ions. The methodology uses the literature cited in the reference. The output is a graph across shells surrounding the atoms.
6.	We can extract and plot a composition part using a mix of critical radius and nearest neighbor list (voxels pending).

Installation
1.	Use any python IDE that supports python3 and install the library files given in requirements.txt
2.	It is always better to set up a new custom environment for a new project
3.	Run the program to see the window. I have temporarily disabled loggers till complete testing in initialized.

Useful links
1.	The overall layout of the app (in pdf): https://bit.ly/3H4h3K7
2.	The brainstorming area (need a Lucidchart account): https://bit.ly/3pgWOmA
3.	The collaborators can ask for a different link so that they can make changes or put new ideas here

References
1.	Anna V. Ceguerra , Michael P. Moody , Leigh T. Stephenson , Ross K.W. Marceau & Simon P. Ringer (2010) A three-dimensional Markov field approach for the analysis of atomic clustering in atom probe data, Philosophical Magazine, 90:12, 1657-1683, DOI: 10.1080/14786430903441475
2.	Leigh T. Stephenson, Michael P. Moody, Peter V. Liddicoat, and Simon P. Ringer (2007) New Techniques for the Analysis of Fine-Scaled Clustering Phenomena within Atom Probe Tomography (APT) Data, Microsc. Microanal. 13, 448–463, 2007, DOI: 10.1017/S1431927607070900 
3.	Anna V. Ceguerra, Michael P. Moody, Rebecca C. Powles, Timothy C. Petersen, Ross K. W. Marceau and Simon P. Ringer (2012) Short-range order in multicomponent materials, Acta Cryst. (2012). A68, 547–560
4.	Leigh T. Stephenson, Anna V. Ceguerra, Tong Li, Tanaporn Rojhirunsakool, Soumya Nag, Rajarshi Banerjee, Julie M. Cairney, Simon P. Ringer (2014), Point-by-point compositional analysis for atom probe tomography, MethodsX 1 (2014) 12–18

Future work
The project is still ongoing development. Anybody wishing to contribute can contact me directly. In the future, we will be primarily looking into optimizing the thread safety, voxelizing data, writing a unit test file, and a better visualizing tool other than matplotlib and updating docs. The UI project was made possible with the student assistantship funding from Ruhr University Bochum between Dec 2020 and March 2021. 
