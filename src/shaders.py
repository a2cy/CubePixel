from ursina import Shader


chunk_shader = Shader.load(language=Shader.GLSL, vertex="./res/shaders/chunk.vert", fragment="./res/shaders/chunk.frag")