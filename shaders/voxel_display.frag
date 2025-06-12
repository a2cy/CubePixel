#version 150

uniform sampler2DArray texture_array;
uniform float texture_id;

in vec2 texcoord;

out vec4 p3d_FragColor;


void main() {
    vec4 color = texture(texture_array, vec3(texcoord, texture_id));

    p3d_FragColor = color.rgba;
}