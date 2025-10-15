#version 150

uniform sampler2DArray u_texture_array;
uniform int u_fog_distance;

in vec3 normal;
in float texture_id;
in vec3 model_fragcoord;
in vec3 view_fragcoord;

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
    vec3 ambient_color = vec3(0.4);
    vec3 light_color = vec3(0.8);
    vec3 fog_color = vec3(0.6);
    float fog_density = 0.6;

    vec3 light_direction = normalize(vec3(1.0, 0.8, 0.5));

    vec4 color = triplanar(model_fragcoord, normal, texture_id, u_texture_array);

    vec3 ambient = ambient_color * color.rgb;
    vec3 diffuse = max(dot(light_direction, normal), 0.0) * light_color * color.rgb;

    color = vec4(ambient + diffuse, color.a);

    float dist_ratio = 4.0 * view_fragcoord.z / u_fog_distance;
    float fog = exp(-pow(dist_ratio * fog_density, 2));
    color.rgb = mix(fog_color.rgb, color.rgb, fog);

    p3d_FragColor = color;
}