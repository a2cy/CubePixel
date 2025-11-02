#version 150

uniform vec4 p3d_ColorScale;
uniform sampler2D p3d_Texture0;

uniform vec4 u_outline_color;

in vec2 thickness;
in vec2 texcoord;

out vec4 p3d_FragColor;


void main() {
    vec4 color = texture(p3d_Texture0, texcoord) * p3d_ColorScale;

    vec2 bl = step(thickness, texcoord);
    vec2 tr = step(thickness, 1.0-texcoord);
    float edge = bl.x * bl.y * tr.x * tr.y;

    if (edge == 0.0) {
       color = u_outline_color;
    }

    p3d_FragColor = color.rgba;
}