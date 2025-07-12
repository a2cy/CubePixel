#version 150

uniform sampler2DArray texture_array;

in float texture_id;
in vec3 model_fragcoord;
in vec3 model_normal;
in vec3 view_fragcoord;
in vec3 view_normal;

out vec4 p3d_FragColor;


vec4 triplanar(vec3 point, vec3 normal, float texture_id, sampler2DArray texture_map) {
    vec2 sample = vec2(0.0);

    if (normal.x != 0) {
        sample = point.zy;
    }

    if (normal.y != 0) {
        sample = point.xz;
    }

    if (normal.z != 0) {
        sample = point.xy;
    }

    return texture(texture_map, vec3(sample, texture_id));
}


void main() {
    vec4 color = triplanar(model_fragcoord, model_normal, texture_id, texture_array);

    p3d_FragColor = color.rgba;
}