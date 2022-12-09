from ursina import Shader


texture_shader = Shader(name="texture_shader", language=Shader.GLSL, 
vertex="""
#version 150

uniform mat4 p3d_ModelViewProjectionMatrix;

in vec4 p3d_Vertex;
in vec3 p3d_MultiTexCoord0;

out vec3 texcoord;

void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;

    texcoord = p3d_MultiTexCoord0;
}
""",

fragment="""
#version 150

uniform sampler2DArray texture_array;

in vec3 texcoord;

out vec4 p3d_FragColor;

void main() {
    vec4 color = texture(texture_array, texcoord);

    p3d_FragColor = color.rgba;
}
""", geometry='',
)
