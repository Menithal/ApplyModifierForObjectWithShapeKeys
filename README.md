# ApplyModifierForObjectWithShapeKeys For Blender 2.80
Blender script

Apply modifier and remove from the stack for object with shape keys (Pushing 'Apply' button in 'Object modifiers' tab result in an error 'Modifier cannot be applied to a mesh with shape keys').

Installation

It is a plugin. Select "File -> User Preferences" and choose "Addon" tab. Click "Install from file..." and choose downloaded file.

How script works

Object is duplicated to match number of shapekeys. From every object shapekeys are removed leaving only one shapekey. After that last the shapekey of each object has to be removed. Now each object apply modifier. After that object are joined to first one as shapes.
Note that this solution may not work for modifiers which change different vertices number for different shapes (for example 'Boolean' modifier).
