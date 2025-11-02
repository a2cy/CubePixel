#version 150

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelMatrix;

uniform float u_thickness;

in vec4 p3d_Vertex;
in vec3 p3d_Normal;
in vec2 p3d_MultiTexCoord0;

out vec2 thickness;
out vec2 texcoord;


void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;

    vec3 scale = vec3(p3d_ModelMatrix[0].x, p3d_ModelMatrix[1].y, p3d_ModelMatrix[2].z);

    if (p3d_Normal.x != 0) {
        thickness = u_thickness / scale.zy;
    }

    if (p3d_Normal.y != 0) {
        thickness = u_thickness / scale.xz;
    }

    if (p3d_Normal.z != 0) {
        thickness = u_thickness / scale.xy;
    }

    texcoord = p3d_MultiTexCoord0;
}