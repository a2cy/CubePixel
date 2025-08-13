#version 150

uniform sampler2DArray texture_array;

in float texture_id;
in vec3 fragcoord;
in vec3 normal;

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
    vec4 ambient_color = vec4(0.4, 0.4, 0.4, 1.0);
    vec4 light_color = vec4(0.8, 0.8, 0.8, 1.0);

    vec3 light_direction = normalize(vec3(1.0, 0.8, 0.5));

    vec4 color = triplanar(fragcoord, normal, texture_id, texture_array);

    vec4 ambient = ambient_color * color;
    vec4 diffuse = max(dot(light_direction, normal), 0.0) * light_color * color;

    p3d_FragColor = ambient + diffuse;
}