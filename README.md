# BRRES Animation Exporter (Blender Add-on)

## Contents
1. [About](#about)
2. [Prerequisite Blender Knowledge](#prerequisite)
3. [Features](#features)
4. [Installation](#installation)
5. [How to Use](#how_to_use)
6. [FAQs](#faqs)
7. [How to add a CHR0 node to a BRRES file with BrawlCrate](#chr0_brawlcrate)
8. [How to add a SRT0 node to a BRRES file with BrawlCrate](#srt0_brawlcrate)
9. [How to add a CLR0 node to a BRRES file with BrawlCrate](#clr0_brawlcrate)  

<a name="about"></a>
## About
This add-on enables animations created in [Blender 2.80](https://builder.blender.org/download/daily/) or above to be used in [Nintendo BRRES](http://wiki.tockdom.com/wiki/BRRES) files. The add-on allows users to export a selection of animation [F-Curves](https://docs.blender.org/manual/en/latest/editors/graph_editor/fcurves/index.html) to a variety of animation formats found in BRRES files, including [CHR0](http://wiki.tockdom.com/wiki/CHR0) (bone transformations), [SRT0](http://wiki.tockdom.com/wiki/SRT0) (texture coordinates) and [CLR0](http://wiki.tockdom.com/wiki/CLR0_(File_Format)) (RGBA data) nodes. Such nodes are easily added to BBRES files using BBRES creation tools such as [BrawlCrate](https://github.com/soopercool101/BrawlCrate).  

<a name="prerequisite"></a>
## Prerequisite Blender Knowledge
A basic understanding of animating properties, creating shaders and rigging is beneficial to using this add-on effectively. In particular, it may be useful to know how to animate the *Mapping* and *RGB* shader nodes, as well as object or bone transformations.

<a name="features"></a>
## Features
- Preserves the shape of F-Curves comprised of key frames with unique left and right tangents and of any interpolation type (Bezier, constant or linear).  

  *Image of Blender F-Curve containing key frames with unique left and right tangents and Bezier, constant or linear interpolation types.*  
  ![Example Curve Before Export](README_images/example_curve_before.png?raw=true)  

  *Resulting curve produced by exporting above F-Curve as CHR0 node using BRRES Animation Exporter add-on, displayed using BrawlCrate. Key features of the original F-Curve are preserved.*  
  ![Example Curve After Export](README_images/example_curve_after.png?raw=true)  

-	[*CHR0 node type*] Exports to all 5 precision formats supported by BRRES CHR0 files. Calculates and exports using the most efficient format by default, but also offers option to force a more precise (resulting in a larger file) format.
-	Displays dynamic, real-time hints to minimise ambiguity. Hides the export button until all hints have been solved.

-	Allows user to choose multiple F-Curves to drive different components of the animation node (specific to the type of animation node). **Any** selection of F-Curves can be used, provided it corresponds one-to-one with the ticked components in the add-on.

    *A ‘valid’ selection of F-Curves in Blender’s graph editor. The number of selected F-Curves in the left panel matches the number of components ticked in the BRRES Animation Exporter add-on. The order of the selected F-Curves (i.e. ‘Scale X’, ‘Scale Y’ etc.) matches the order of the ticked components in the add-on.*  
  ![Example F-Curve Selection](README_images/example_fcurve_selection.png?raw=true)  

- Allows user to specify an interval on the timeline to export from.
-	Exports animation nodes to the same directory as Blend file. Filename includes Blend filename, node type, number of frames and node name. Won’t overwrite existing file with the same filename.
-	[*CHR0 node type*] Offers ability to edit the value used to scale translation data. By default, this value is 100 to account for the change in unit. Useful to adjust for scale of parent bones.  


<a name="installation"></a>
## Installation
To install the add-on, navigate to *Edit > Preferences > Add-ons > Install*, and open *brres_animation_exporter.zip*. To enable the add-on, tick the box next to *Export: BRRES Animation Exporter*.  


<a name="how_to_use"></a>
## How to Use
To quickly access the graph editor, select the *Animation* workspace. In the graph editor, press *N* to toggle the tools panel on the right. Select the *BRRES Animation Exporter* tab. A list of animated properties in the scene are displayed in the left panel of the graph editor. To ensure that all animated properties are displayed here, toggle off the *Only Show Selected* option in the top right of the graph editor.
1. In the *BRRES Animation Exporter* tab, choose a node type, then tick the components of the node that are to be driven by an F-Curve.
2. In the left panel of the graph editor, select an equivalent number of F-Curve channels. The order of the channels in the panel must match the selection made in the *BRRES Animation Exporter* tab. If the F-Curve channels are not in the desired order, they need to be rearranged. First, ensure the F-Curve channels are in a group. To add F-Curve channels to a group, shift select the channels, then right click inside the panel and choose *Group Channels*. Once in a group, move channels up or down using *right click > Move > Up / Down* (**WARNING**: save beforehand, this action is known to crash Blender on some versions).
3. Once in the correct order, shift select the F-Curve channels to be included in the animation node. Note that the selected F-Curve channels must also be visible and editable (toggled by the *eye* and *lock* symbol, respectively).
4. In the *BRRES Animation Exporter* tab, choose an interval on the timeline to export from. If the correct number of F-Curve channels have been selected, the Export button will be available. If the Export button is greyed-out, refer to the hint given.


<a name="faqs"></a>
## FAQs
-	*Q*: Why are the tangents in my CHR0 node flat or slightly off what they should be?
-	*A*: For *Interpolated 4* and *Interpolated 6* formats, tangents are rounded down to the nearest integer. Positive tangents less than 1 will appear flat. To store tangents as floats instead, enable Advanced Options and change the data format to *Interpolated 12*.
-	*Q*: Why are sections of my F-Curve(s) baked to key frames at every frame when I export?
-	*A*: F-Curves used for CLR0 nodes or *Linear 1* / *Linear 4* formatted rotation data in CHR0 nodes are automatically sampled on and sometimes around the interval to export from. To undo this change, just use *CTRL Z*.


<a name="chr0_brawlcrate"></a>
## How to add a CHR0 node to a BRRES file with BrawlCrate
-	*Right click your_brres_name.brres > New > Model Animation*.
-	Rename the new *CHR* node to something meaningful.
-	Select the *CHR* node. Set *G3D Node > Version* to *5*. Set *Bone Animation > FrameCount* and *Loop* as appropriate (the frame count is included in the filename of the exported animation node).
-	*Right click CHR node > New Bone Target*. Rename the bone target node to the name of the bone you want to animate.
-	*Right click the bone target node > Replace*, then select your exported CHR0 node.
-	Save. *Right click the MDL0 > Preview*, to view changes.


<a name="srt0_brawlcrate"></a>
## How to add a SRT0 node to a BRRES file with BrawlCrate
-	Right click *your_brres_name.brres, New > Texture Animation*.
-	Rename the new SRT node to something meaningful.
-	Select the SRT node. Set *G3D Node > Version* to *5*. Set *Texture Coordinate Animation > MatrixMode to MatrixXSI*. Set *Texture Coordinate Animation > FrameCount* and *Loop* as appropriate (if *Loop* is set to true, set *FrameCount* to 1 less than the frame count included in the filename of the exported animation node).
-	Right click SRT node, *New Entry*. Rename the entry node to the name of the material you want to animate.
-	Right click entry node, *New Entry*. Click the new texture entry node. Set *SRT0 Texture Entry > TextureIndex* to the 0-based index of the corresponding texture reference in the material.
-	*Right click the texture entry node > Replace*, then select your exported SRT0 node.
-	Save. *Right click the MDL0 > Preview*, to view changes.


<a name="clr0_brawlcrate"></a>
## How to add a CLR0 node to a BRRES file with BrawlCrate
-	*Right click your_brres_name.brres > New > Color Sequence*.
-	Rename the new CLR node to something meaningful.
-	Select the CLR node. Set *G3D Node > Version* to *4*. Set *Material Color Animation > FrameCount* and *Loop* as appropriate (the frame count is included in the filename of the exported animation node).
-	*Right click CLR node > New Material Entry*. Rename the material entry node to the name of the material you want to animate.
-	If the material entry node does not have a colour sequence node, *right click the material entry node > New Color Sequence*.
-	*Right click the colour sequence node > Replace*, then select your exported CLR0 node.
-	Select the colour sequence node. Set *CLR0 Material Entry > Target* as appropriate. Use this target in the shader to access the animated RGBA stream.
-	Save. *Right click the MDL0 > Preview*, to view changes.
