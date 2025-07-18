#version 150

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform mat3 p3d_NormalMatrix;


in uint vertex_data;

out float texture_id;
out vec3 model_fragcoord;
out vec3 model_normal;
out vec3 view_fragcoord;
out vec3 view_normal;


vec3[] normals = vec3[6](
    vec3(-1.0, 0.0, 0.0),
    vec3(0.0, -1.0, 0.0),
    vec3(0.0, 0.0, -1.0),
    vec3(1.0, 0.0, 0.0),
    vec3(0.0, 1.0, 0.0),
    vec3(0.0, 0.0, 1.0)

);


void main() {
    vec4 vertex = vec4(vertex_data & 0x3Fu, (vertex_data >> 6) & 0x3Fu, (vertex_data >> 12) & 0x3Fu, 1.0);

    gl_Position = p3d_ModelViewProjectionMatrix * (vertex + vec4(-0.5, -0.5, -0.5, 0.0));

    model_normal = normalize(normals[(vertex_data >> 18) & 0x7u]);
    view_normal = normalize(p3d_NormalMatrix * model_normal);

    texture_id = (vertex_data >> 21) & 0xFFu;

    model_fragcoord = vec3(vertex);
    view_fragcoord = vec3(p3d_ModelViewMatrix * (vertex + vec4(-0.5, -0.5, -0.5, 0.0)));


}