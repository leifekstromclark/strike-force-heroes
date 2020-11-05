# SFH

A tribute to a one of remarkable Flash games, Strike Force Heroes.

## Background
In July 2017, [Adode announced that Flash player will be discontinued after December 31, 2020](https://www.adobe.com/sea/products/flashplayer/end-of-life.html). This announcement has led to some Flash games publisher stopped accepting new games (like [Kongregate.com](https://www.theverge.com/2020/7/2/21311318/kongregate-stops-accepting-new-game-submissions-flash-discontinued-layoffs).

Strike Force Heroes, a Flash game made by Armor Games and Not Doppler, will be affected by this announcement. Therefore, Leif Clark (first initiator) wanted to make a sort of tribute to this game.

## Current Plans (As of Nov. 4)
(The following is speculation and subject to change)
The game should be browser based like its predecessors. This will likely be done through javascript and some version of webgl. Right now I am considering pixi.js due to its speed.

Multiplayer is a priority, though I am unsure what language and libraries to use for backend.
Soldier hitboxes for bullets will be some combination of circles and rectangles closely matching the pose of the soldier. Weapons are mostly hitscan. Checking for hits will not be difficult.

Soldiers should have a different simpler hitbox (box or line) for collisions with the map. Additionally, soldiers should rotate depending on the angle of the terrain (soldiers should not stand or rotate on steep/non-ground terrain). Rotation is 0 when not grounded. These rotations will probably be applied with rotation matrices. Soldiers in sfh can climb over small ledges and boxes. Lengths of steep terrain that are shorter than the soldier should be climbable (rotation would be perpendicular).

Things to figure out:

What are the most efficient ways to check for collisions, and what geometry can we choose to optimize this process?

When a collision is detected between an possibly unaligned soldier and arbitrary terrain how can we reposition the soldier just out of the terrain efficiently?
