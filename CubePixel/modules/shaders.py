from ursina import Shader


chunk_shader = Shader.load(language=Shader.GLSL, vertex="./data/shaders/chunk.vert", fragment="./data/shaders/chunk.frag")