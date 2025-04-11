#version 150

uniform mat4 p3d_ModelViewProjectionMatrix;

in vec4 p3d_Vertex;
in vec3 p3d_Normal;

out vec3 fragcoord;
out vec3 normal;


void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;

    normal = p3d_Normal;

    fragcoord = vec3(p3d_Vertex) - vec3(0.5);
}