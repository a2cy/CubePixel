#version 150

uniform mat4 p3d_ModelViewProjectionMatrix;

in vec4 p3d_Vertex;
in ivec2 vertex_data;

out float texture_id;
out vec3 fragcoord;
out vec3 normal;


vec3[] normals = vec3[6](
    vec3(-1.0, 0.0, 0.0),
    vec3(0.0, -1.0, 0.0),
    vec3(0.0, 0.0, -1.0),
    vec3(1.0, 0.0, 0.0),
    vec3(0.0, 1.0, 0.0),
    vec3(0.0, 0.0, 1.0)

);


void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * (p3d_Vertex + vec4(-0.5, -0.5, -0.5, 0.0));

    texture_id = vertex_data[0];

    fragcoord = vec3(p3d_Vertex);

    normal = normalize(normals[vertex_data[1]]);
}