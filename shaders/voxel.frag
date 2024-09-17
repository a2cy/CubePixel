#version 150

uniform sampler2DArray texture_array;

in vec3 texcoord;

out vec4 p3d_FragColor;


void main() {
    vec4 color = texture(texture_array, texcoord);

    p3d_FragColor = color.rgba;
}