#version 150

in vec2 texcoord;

out vec4 p3d_FragColor;


void main() {
    vec4 color = vec4(0.0, 0.0, 0.0, 0.15);
    float thickness = 0.02;

    vec2 bl = step(vec2(thickness), texcoord);
    float pct = bl.x * bl.y;

    vec2 tr = step(vec2(thickness), 1.0-texcoord);
    pct *= tr.x * tr.y;

    if (pct == 0) {
        color = vec4(0.15, 0.15, 0.15, 1.0);
    }

    p3d_FragColor = color.rgba;
}