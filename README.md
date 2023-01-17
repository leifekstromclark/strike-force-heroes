# SFH

A tribute to a one of remarkable Flash games, Strike Force Heroes.

## Background
In July 2017, [Adode announced that Flash player would be discontinued after December 31, 2020](https://www.adobe.com/sea/products/flashplayer/end-of-life.html). This announcement has led to some Flash games publisher stopped accepting new games (like [kongregate.com](https://www.theverge.com/2020/7/2/21311318/kongregate-stops-accepting-new-game-submissions-flash-discontinued-layoffs)).

Strike Force Heroes, a Flash game sponsored by ArmorGames.com and NotDoppler.com, will be affected by this announcement. Therefore, Leif Clark (first initiator) wanted to make a sort of tribute to this game.

Original SFH games can still be played using emulators and some downloadable projectors. [Sky9 Is now working on a remastered version of SFH1](https://www.youtube.com/watch?v=D8DCW2asa1U). Check out [Strike Force Heroes: Unification](https://discord.gg/NGaw7g2Vr8), another fan game, as well as the [the official SFH subreddit](https://www.reddit.com/r/StrikeForceHeroes/) and [discord server](https://discord.gg/p5zGTE4BWY).

[Discord server for this project](https://discord.gg/3GvtYyNWEq) (unfortunately very dead at the moment)

View demos [here](https://leifekstromclark.github.io).

## Demo Videos
### Movement
https://user-images.githubusercontent.com/59668580/212800238-f6e0ed1a-4ac8-422d-b975-6e78860a41d9.mp4

### Ledge Mantling
https://user-images.githubusercontent.com/59668580/212800362-82cc2ae7-6dc8-45c1-ac97-6fa181aeeaa8.mp4

## Updates
### Jul. 29
Pixi implementation of physics engine is well underway.

### Jan. 14
Movement related physics complete apart from edge mantling.

### Dec. 20
Landing has been implemented. I am working on movement (debugging, organizing, and optimization).

### Nov. 10
Added alternate collision detection and response for grounded player.

### Nov. 9
I did some tests in sfh 1. The hitboxes appear to be very basic and might not even rotate. Soldiers can clamber up ledges taller than themselves if they are near the top (I need to rethink the climbing mechanic). It seems rotation and complex hitboxes may not be necessary for collisions (rotation is still needed for animation however). As we have nearly solved these more complex issues it may be worth it to use them regardless.

### Nov. 6
Progress has been made on collision detection and response. The current algorithm, however, may be unnessesarily powerful and yield unwanted behaviour in some cases. It will be tweaked. Variations may also be created for certain cases.

### Nov. 4
(The following is speculation and subject to change)

The game should be browser based like its predecessors. This will likely be done through javascript and some version of webgl. Right now I am considering [pixi.js](https://github.com/pixijs/pixi.js) due to its speed.

Multiplayer is a priority, though I am unsure what language and libraries to use for backend.
Soldier hitboxes for bullets will be some combination of circles and rectangles closely matching the pose of the soldier. Weapons are mostly hitscan. Checking for hits will not be difficult.

Soldiers should have a different simpler hitbox (box or line) for collisions with the map. Additionally, soldiers should rotate depending on the angle of the terrain (soldiers should not stand or rotate on steep/non-ground terrain). Rotation is 0 when not grounded. These rotations will probably be applied with rotation matrices. Soldiers in sfh can climb over small ledges and boxes. Lengths of steep terrain that are shorter than the soldier should be climbable (rotation would be perpendicular).

Things to figure out:

What are the most efficient ways to check for collisions, and what geometry can we choose to optimize this process?

When a collision is detected between an possibly unaligned soldier and arbitrary terrain how can we reposition the soldier just out of the terrain efficiently?

Client side prediction.
