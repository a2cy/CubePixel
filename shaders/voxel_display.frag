#version 150

uniform sampler2DArray texture_array;
uniform float texture_id;

in vec3 fragcoord;
in vec3 normal;

out vec4 p3d_FragColor;


vec4 triplanar(vec3 point, vec3 normal, float texture_id, sampler2DArray texture_map) {
    vec4 dx = texture(texture_map, vec3(point.zy, texture_id));
    vec4 dy = texture(texture_map, vec3(point.xz, texture_id));
    vec4 dz = texture(texture_map, vec3(point.xy, texture_id));

    vec3 weights = abs(normal.xyz);
    weights = weights / (weights.x + weights.y + weights.z);

    return dx * weights.x + dy * weights.y + dz * weights.z;
}


void main() {
    vec4 color = triplanar(fragcoord, normal, texture_id, texture_array);

    p3d_FragColor = color.rgba;
}