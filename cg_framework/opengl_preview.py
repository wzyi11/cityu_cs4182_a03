"""Optional OpenGL diagnostics and image presenter.

This module deliberately hides VAO/VBO, shader, and texture plumbing. The
assignments assess graphics algorithms rather than API setup details.
"""

from __future__ import annotations

import ctypes
from dataclasses import dataclass

import numpy as np

from .figures import as_uint8


@dataclass(frozen=True)
class OpenGLInfo:
    vendor: str
    renderer: str
    version: str
    glsl_version: str


def _decode(value) -> str:
    return value.decode("utf-8", errors="replace") if value else "Unavailable"


def collect_opengl_info() -> OpenGLInfo:
    """Create a hidden context and return implementation information."""
    import glfw
    from OpenGL.GL import GL_RENDERER, GL_SHADING_LANGUAGE_VERSION, GL_VENDOR, GL_VERSION, glGetString

    if not glfw.init():
        raise RuntimeError("GLFW could not initialise. Check the display and driver setup.")
    try:
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
        window = glfw.create_window(64, 64, "CS4182 diagnostics", None, None)
        if window is None:
            raise RuntimeError("GLFW could not create an OpenGL context.")
        try:
            glfw.make_context_current(window)
            return OpenGLInfo(
                vendor=_decode(glGetString(GL_VENDOR)),
                renderer=_decode(glGetString(GL_RENDERER)),
                version=_decode(glGetString(GL_VERSION)),
                glsl_version=_decode(glGetString(GL_SHADING_LANGUAGE_VERSION)),
            )
        finally:
            glfw.destroy_window(window)
    finally:
        glfw.terminate()


def _compile_shader(source: str, shader_type: int) -> int:
    from OpenGL.GL import (
        GL_COMPILE_STATUS,
        glCompileShader,
        glCreateShader,
        glGetShaderInfoLog,
        glGetShaderiv,
        glShaderSource,
    )

    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)
    if not glGetShaderiv(shader, GL_COMPILE_STATUS):
        raise RuntimeError(_decode(glGetShaderInfoLog(shader)))
    return shader


def show_image(image: np.ndarray, title: str = "CS4182 Preview") -> None:
    """Display an RGB array in an OpenGL window until Escape is pressed."""
    import glfw
    from OpenGL.GL import (
        GL_ARRAY_BUFFER,
        GL_CLAMP_TO_EDGE,
        GL_COLOR_BUFFER_BIT,
        GL_FALSE,
        GL_FLOAT,
        GL_FRAGMENT_SHADER,
        GL_LINEAR,
        GL_LINK_STATUS,
        GL_RGB,
        GL_STATIC_DRAW,
        GL_TEXTURE_2D,
        GL_TEXTURE_MAG_FILTER,
        GL_TEXTURE_MIN_FILTER,
        GL_TEXTURE_WRAP_S,
        GL_TEXTURE_WRAP_T,
        GL_TRIANGLES,
        GL_UNPACK_ALIGNMENT,
        GL_UNSIGNED_BYTE,
        GL_VERTEX_SHADER,
        glAttachShader,
        glBindBuffer,
        glBindTexture,
        glBindVertexArray,
        glBufferData,
        glClear,
        glClearColor,
        glCreateProgram,
        glDeleteBuffers,
        glDeleteProgram,
        glDeleteShader,
        glDeleteTextures,
        glDeleteVertexArrays,
        glDrawArrays,
        glEnableVertexAttribArray,
        glGenBuffers,
        glGenTextures,
        glGenVertexArrays,
        glGetProgramInfoLog,
        glGetProgramiv,
        glLinkProgram,
        glPixelStorei,
        glTexImage2D,
        glTexParameteri,
        glUseProgram,
        glVertexAttribPointer,
        glViewport,
    )

    pixels = np.flipud(as_uint8(image)).copy()
    height, width = pixels.shape[:2]
    if not glfw.init():
        raise RuntimeError("GLFW could not initialise.")
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    window = glfw.create_window(width, height, title, None, None)
    if window is None:
        glfw.terminate()
        raise RuntimeError("GLFW could not create an OpenGL 3.3 context.")

    vertex_source = """#version 330 core
    layout(location=0) in vec2 p; layout(location=1) in vec2 uv;
    out vec2 texcoord; void main(){texcoord=uv; gl_Position=vec4(p,0,1);}
    """
    fragment_source = """#version 330 core
    in vec2 texcoord; out vec4 colour; uniform sampler2D image_texture;
    void main(){colour=texture(image_texture, texcoord);}
    """
    vertices = np.array([
        -1, -1, 0, 0, 1, -1, 1, 0, 1, 1, 1, 1,
        -1, -1, 0, 0, 1, 1, 1, 1, -1, 1, 0, 1,
    ], dtype=np.float32)

    glfw.make_context_current(window)
    vertex_shader = fragment_shader = program = vao = vbo = texture = None
    try:
        vertex_shader = _compile_shader(vertex_source, GL_VERTEX_SHADER)
        fragment_shader = _compile_shader(fragment_source, GL_FRAGMENT_SHADER)
        program = glCreateProgram()
        glAttachShader(program, vertex_shader)
        glAttachShader(program, fragment_shader)
        glLinkProgram(program)
        if not glGetProgramiv(program, GL_LINK_STATUS):
            raise RuntimeError(_decode(glGetProgramInfoLog(program)))
        vao = glGenVertexArrays(1)
        vbo = glGenBuffers(1)
        glBindVertexArray(vao)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        stride = 4 * vertices.itemsize
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(2 * vertices.itemsize))
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, pixels)
        glClearColor(0.08, 0.09, 0.12, 1.0)
        while not glfw.window_should_close(window):
            if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
                glfw.set_window_should_close(window, True)
            framebuffer_width, framebuffer_height = glfw.get_framebuffer_size(window)
            glViewport(0, 0, framebuffer_width, framebuffer_height)
            glClear(GL_COLOR_BUFFER_BIT)
            glUseProgram(program)
            glBindVertexArray(vao)
            glBindTexture(GL_TEXTURE_2D, texture)
            glDrawArrays(GL_TRIANGLES, 0, 6)
            glfw.swap_buffers(window)
            glfw.poll_events()
    finally:
        if texture:
            glDeleteTextures([texture])
        if vbo:
            glDeleteBuffers(1, [vbo])
        if vao:
            glDeleteVertexArrays(1, [vao])
        if program:
            glDeleteProgram(program)
        if vertex_shader:
            glDeleteShader(vertex_shader)
        if fragment_shader:
            glDeleteShader(fragment_shader)
        glfw.destroy_window(window)
        glfw.terminate()

